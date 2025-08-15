#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Вспомогательный модуль ("фреймворк") для всех операций, связанных с ответами на вопросы.

Этот модуль инкапсулирует логику:
- Выбора вопроса по различным критериям.
- Отправки ответа на вопрос.
- Проверки наличия ответа в административной панели.

Это сделано для соблюдения Принципа Одной Ответственности (SoC) и для переиспользования
логики в различных тестах.
"""

import re
from typing import Dict, Optional, Tuple, List
import logging
import time

import requests
from bs4 import BeautifulSoup

from framework.utils.question_factory import QuestionFactory
from framework.utils.html_parser import ModerationPanelParser
from framework.utils.smart_auth_manager import SmartAuthManager


# Создаем логгер для нашего модуля
logger = logging.getLogger(__name__)

# Константы URL для избежания "магических" строк в коде
QUESTIONS_PAGE_URL = "https://expert.bll.by/questions?allow-session=2"
ADMIN_PANEL_URL = "https://expert.bll.by/admin/posts/new?allow-session=2"
BASE_URL = "https://expert.bll.by"


def select_question(
    selection_mode: str,
    session_cookie: str,
    author_nickname: str = "Admin",
    exclude_ids: Optional[List[int]] = None,
) -> Optional[Dict]:
    """
    Выбирает вопрос по указанному критерию, получая данные со страницы со списком вопросов.

    Args:
        selection_mode: Критерий выбора ('latest', 'zero_answers', 'by_author').
        session_cookie: Сессионная кука для авторизации.
        author_nickname: Никнейм автора для поиска (используется с 'by_author').
        exclude_ids: Список ID вопросов, которые нужно исключить из выборки.

    Returns:
        Словарь с данными о вопросе или None, если ничего не найдено.
    """
    logger.info(f"Начинаем выбор вопроса по критерию: '{selection_mode}'")
    try:
        response = requests.get(
            QUESTIONS_PAGE_URL, cookies={"test_joint_session": session_cookie}, timeout=15
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        all_questions: List[Dict] = []
        # Корректный селектор на основе анализа HTML: каждый вопрос - это <li>
        question_blocks = soup.select('ul.search-list-result > li')

        if not question_blocks:
            logger.warning("Не найдено ни одного блока с вопросами по селектору 'ul.search-list-result > li'.")
            # Оставляем print на случай, если верстка снова изменится
            # print("HTML snippet for debugging:\n", response.text)
            return None

        for item in question_blocks:
            try:
                # Извлекаем ID из ссылки на вопрос
                link_tag = item.select_one('a.search-list-result__link_2')
                if not link_tag or not link_tag.has_attr('href'):
                    continue
                
                href = link_tag['href']
                question_id_match = re.search(r'/answers/(\d+)', href)
                if not question_id_match:
                    continue

                # Извлекаем количество ответов
                answers_tag = item.select_one('span.pt10')
                answers_count = 0
                if answers_tag and answers_tag.text:
                    answers_match = re.search(r'Ответов:\s*(\d+)', answers_tag.text)
                    if answers_match:
                        answers_count = int(answers_match.group(1))

                # Извлекаем остальные данные
                question_text = link_tag.text.strip().replace('\n', ' ').replace('\r', '')
                author_tag = item.select_one('a.search-list-result__link_orange')
                author_name = author_tag.text.strip() if author_tag else "Unknown"
                
                # Используем ID как суррогат timestamp для сортировки
                question_id = int(question_id_match.group(1))

                all_questions.append(
                    {
                        "id": question_id,
                        "text": question_text,
                        "author": author_name,
                        "answers_count": answers_count,
                    }
                )
            except (AttributeError, ValueError, TypeError) as e:
                logger.warning(f"Не удалось распарсить блок вопроса: {e}. Блок: {str(item)[:300]}")
                continue

        if not all_questions:
            logger.error("Не удалось извлечь информацию ни по одному вопросу.")
            return None

        logger.info(f"Всего найдено и распарсено вопросов: {len(all_questions)}")

        # ---- Новая логика: фильтрация по exclude_ids ----
        if exclude_ids:
            filtered_questions = [q for q in all_questions if q.get("id") not in exclude_ids]
            if not filtered_questions:
                logger.warning(
                    f"После исключения ID {exclude_ids} не осталось кандидатов для выбора."
                )
                return None
            logger.info(
                f"Исключено {len(all_questions) - len(filtered_questions)} вопросов. "
                f"Осталось кандидатов: {len(filtered_questions)}"
            )
            search_pool = filtered_questions
        else:
            search_pool = all_questions
        # --------------------------------------------------

        # Фильтрация по критерию
        if selection_mode == "latest":
            # Сортируем по ID в обратном порядке (предполагаем, что больший ID = более новый)
            return sorted(search_pool, key=lambda q: q["id"], reverse=True)[0]

        if selection_mode == "zero_answers":
            zero_answer_questions = [q for q in search_pool if q["answers_count"] == 0]
            if not zero_answer_questions:
                logger.warning("Не найдено вопросов с 0 ответов.")
                return None
            # Возвращаем самый свежий из них
            return sorted(zero_answer_questions, key=lambda q: q["id"], reverse=True)[0]

        if selection_mode == "by_author":
            author_questions = [
                q for q in search_pool if q["author"].lower() == author_nickname.lower()
            ]
            if not author_questions:
                logger.warning(f"Не найдено вопросов от автора '{author_nickname}'.")
                return None
            # Возвращаем самый свежий из них
            return sorted(author_questions, key=lambda q: q["id"], reverse=True)[0]

        # Если критерий не подошел, возвращаем None
        logger.error(f"Неизвестный критерий выбора: {selection_mode}")
        return None

    except requests.RequestException as e:
        logger.error(f"Сетевая ошибка при запросе к странице вопросов: {e}")
        return None


def submit_answer(
    question_id: int, session_cookie: str, role: str
) -> Tuple[Optional[int], str]:
    """
    Готовит и отправляет ответ на вопрос, используя SmartAuthManager для отказоустойчивости.

    Args:
        question_id: ID вопроса, на который нужно ответить.
        session_cookie: Сессионная кука для авторизации.
        role: Роль пользователя, необходимая для возможной реавторизации.

    Returns:
        Кортеж (ID отправленного ответа, Текст отправленного ответа).
        В случае ошибки ID будет None.
    """
    auth_manager = SmartAuthManager()
    answer_text = QuestionFactory().generate_answer_text()
    question_page_url = f"{BASE_URL}/questions/answers/{question_id}?allow-session=2"

    try:
        session = requests.Session()
        session.cookies.set("test_joint_session", session_cookie)

        # 1. Получаем страницу вопроса, чтобы извлечь CSRF-токен
        response = session.get(question_page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 2. Ищем CSRF-токен в мета-теге или скрытом поле
        token_input = soup.select_one('input[name="_token"]')
        csrf_token = token_input.get("value") if token_input else None
        if not csrf_token:
             meta_token = soup.select_one('meta[name="csrf-token"]')
             if meta_token:
                csrf_token = meta_token.get('content')
        
        if not csrf_token:
            logger.error(f"Не удалось найти CSRF-токен на странице вопроса {question_page_url}")
            return None, answer_text

        # 3. Готовим payload и делегируем отправку SmartAuthManager
        payload = {
            "t": "1063102",
            "d": "0",
            "question_id": str(question_id),
            "p": answer_text,
            "_token": csrf_token,
        }

        result = auth_manager.submit_answer_with_retry(
            session_cookie=session_cookie, role=role, payload=payload
        )

        if result.get("success"):
            logger.info(f"Ответ на вопрос ID {question_id} успешно отправлен. Статус: {result.get('status_code')}")
            return 99999, answer_text # Возвращаем фиктивный ID

        logger.error(
            f"Ошибка отправки ответа. Статус: {result.get('status_code')}, "
            f"Ответ: {result.get('response_text', '')[:500]}"
        )
        return None, answer_text

    except requests.RequestException as e:
        logger.error(f"Сетевая ошибка при подготовке к отправке ответа: {e}")
        return None, answer_text


def verify_answer_in_admin_panel(
    answer_text: str, admin_cookie: str, delays: Tuple[float, ...] = (0, 1.5, 3.0, 5.0)
) -> bool:
    """
    Проверяет наличие ответа в админ-панели с механизмом повторных попыток.

    Args:
        answer_text: Текст ответа для поиска.
        admin_cookie: Сессионная кука администратора.
        delays: Кортеж задержек между попытками проверки.

    Returns:
        True, если ответ найден и имеет корректную маркировку, иначе False.
    """
    parser = ModerationPanelParser()
    unique_part = re.search(r"\(тех. ID (\d+)\)", answer_text)
    if not unique_part:
        logger.error("Не удалось извлечь уникальный ID из текста ответа.")
        return False
    
    search_fragment = unique_part.group(1)
    logger.info(f"Начинаем проверку наличия ответа в админ-панели по фрагменту: '{search_fragment}'")

    for attempt, delay in enumerate(delays, 1):
        if delay > 0:
            time.sleep(delay)
        
        logger.info(f"Попытка {attempt}/{len(delays)}: получение данных с панели модерации...")
        entries = parser.get_moderation_panel_data(admin_cookie, limit=30)
        
        for entry in entries:
            # Ищем по уникальному ID и проверяем тип "П"
            if search_fragment in entry.get("text", "") and entry.get("type") == "П":
                logger.info(f"✅ Успех! Ответ найден в панели модерации: {entry}")
                return True
    
    logger.error("Ответ не найден в панели модерации после всех попыток.")
    return False

