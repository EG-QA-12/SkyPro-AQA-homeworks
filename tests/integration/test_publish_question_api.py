#!/usr/bin/env python3
"""
Тест публикации вопроса через админ-API

Сценарий:
1. Получаем сессионную куку администратора
2. Выбираем вопрос для публикации (по умолчанию - самый свежий)
3. Формируем тело запроса в формате raw-urlencoded
4. Отправляем POST на /admin/posts/update
5. Проверяем успешность операции

## Использование параметризации

Этот тест можно запускать для массовой публикации вопросов, используя параметризацию Pytest.
Количество публикуемых вопросов контролируется переменной окружения `NUM_QUESTIONS_TO_PUBLISH`.

**Примеры запуска:**

*   **Опубликовать 1 вопрос (по умолчанию):**
    ```bash
    python -m pytest tests/integration/test_publish_question_api.py -v -s
    ```

*   **Опубликовать 5 вопросов:**
    ```bash
    NUM_QUESTIONS_TO_PUBLISH=5 python -m pytest tests/integration/test_publish_question_api.py -v -s
    ```

*   **Опубликовать 10 вопросов:**
    ```bash
    NUM_QUESTIONS_TO_PUBLISH=10 python -m pytest tests/integration/test_publish_question_api.py -v -s
    ```

**Выбор конкретных вопросов для публикации:**
Помимо массовой публикации, вы можете управлять выбором конкретного вопроса с помощью следующих 
переменных окружения (они переопределяют поведение по умолчанию):

*   `PUBLISH_MODE`: Определяет критерий выбора вопроса.
    *   `latest` (по умолчанию): Самый свежий неопубликованный вопрос.
    *   `by_marker`: Поиск вопроса по текстовому маркеру (см. `PUBLISH_MARKER`).
    *   `by_user`: Поиск вопроса по имени пользователя (см. `PUBLISH_USER`).
*   `PUBLISH_MARKER`: Фрагмент текста для поиска в вопросе (используется с `PUBLISH_MODE=by_marker`).
*   `PUBLISH_USER`: Имя пользователя, задавшего вопрос (используется с `PUBLISH_MODE=by_user`).

**Отчетность Allure:**
Каждая операция публикации вопроса будет отображаться как отдельный тестовый кейс в отчете Allure, 
что обеспечивает высокую детализацию и упрощает отладку.
"""

import os
import logging
import pytest
import requests
import allure
import contextlib
import io
from typing import Dict, List, Optional, Tuple
from framework.utils.html_parser import ModerationPanelParser
from framework.utils.smart_auth_manager import SmartAuthManager
from urllib.parse import urlencode, unquote

logger = logging.getLogger(__name__)

# Конфигурация
BASE_URL = "https://expert.bll.by"
PUBLISH_ENDPOINT = "/admin/posts/update"

def select_question(entries: List[Dict], mode: str = "latest", marker: Optional[str] = None, user: Optional[str] = None) -> Dict:
    """
    Выбирает вопрос для публикации по заданным критериям
    
    Args:
        entries: Список записей из панели модерации
        mode: Критерий выбора (latest, by_marker, by_user)
        marker: Фрагмент текста для поиска (для by_marker)
        user: Имя пользователя (для by_user)
    
    Returns:
        Dict: Выбранная запись вопроса
        
    Raises:
        ValueError: Если не удалось найти подходящий вопрос
    """
    # Фильтруем только вопросы (тип '?')
    questions = [e for e in entries if e.get('type') == '?']
    
    if not questions:
        raise ValueError("Не найдено вопросов для публикации (тип '?')")
    
    # Выбор по маркеру
    if mode == "by_marker" and marker:
        marker_lower = marker.lower()
        for q in questions:
            if 'text' in q and marker_lower in q['text'].lower():
                return q
        raise ValueError(f"Не найден вопрос с маркером: {marker}")
    
    # Выбор по пользователю
    if mode == "by_user" and user:
        user_lower = user.lower()
        for q in questions:
            if 'user' in q and user_lower in q['user'].lower():
                return q
        raise ValueError(f"Не найден вопрос от пользователя: {user}")
    
    # Выбор самого свежего вопроса (по timestamp)
    # Если несколько с одинаковым timestamp, берем с наибольшим id (предполагая, что id увеличиваются)
    # Сначала сортируем по timestamp (по убыванию), затем по id (по убыванию)
    sorted_questions = sorted(questions, key=lambda x: (x.get('timestamp', 0), int(x.get('id', 0)) if x.get('id') and x.get('id').isdigit() else 0), reverse=True)
    return sorted_questions[0]


def _get_num_to_publish_env() -> int:
    """Возвращает количество вопросов для публикации из ENV NUM_QUESTIONS_TO_PUBLISH.

    По умолчанию возвращает 1. Некорректные значения приводятся к 1.

    Returns:
        int: Количество вопросов для публикации.
    """
    try:
        value = int(os.getenv("NUM_QUESTIONS_TO_PUBLISH", "1").strip())
        return value if value > 0 else 1
    except Exception:
        return 1

def generate_params_list(question_id: str, extra_params: Optional[List[Tuple[str, str]]] = None) -> List[Tuple[str, str]]:
    params_list: List[Tuple[str, str]] = [
        ('id', str(question_id)),
        ('post_type_id', '1'),
        ('status_id', '3'),
        ('answered', '0'),
        ('rejection_reason_id', '0'),
        ('moder_msg', ''),
        ('delete_reason', '0'),
        ('hand_over_moderator', ''),
    ]
    for i in range(1, 66):
        params_list.append(('sub_theme_id[]', str(i)))
    if extra_params:
        params_list.extend(extra_params)
    return params_list


def _fetch_csrf_tokens(session: requests.Session, session_cookie: str) -> Dict[str, Optional[str]]:
    """
    Получает CSRF-токены с админ-страницы: cookie XSRF-TOKEN и hidden _token из HTML.

    Args:
        session: Сессия requests для повторного использования кук/заголовков
        session_cookie: Значение куки test_joint_session

    Returns:
        Dict[str, Optional[str]]: {'xsrf_cookie': str|None, 'form_token': str|None}
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        'Referer': f'{BASE_URL}/admin/posts/new',
    }
    # Устанавливаем сессионную куку
    session.cookies.set('test_joint_session', session_cookie)
    resp = session.get(f"{BASE_URL}/admin/posts/new", headers=headers, timeout=10)
    xsrf_cookie = resp.cookies.get('XSRF-TOKEN') or session.cookies.get('XSRF-TOKEN')

    form_token = None
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text or "", 'html.parser')
        meta = soup.select_one('meta[name="csrf-token"]')
        if meta and meta.get('content'):
            form_token = meta['content']
        if not form_token:
            hidden = soup.select_one('input[name="_token"]')
            if hidden and hidden.get('value'):
                form_token = hidden['value']
    except Exception:
        form_token = None

    return {'xsrf_cookie': xsrf_cookie, 'form_token': form_token}

@allure.title("Публикация вопроса через админ-API")
@allure.description("Тестирование публикации вопроса через POST /admin/posts/update")
@allure.feature("API тестирование")
@pytest.mark.api
@pytest.mark.parametrize(
    "case_index",
    tuple(range(_get_num_to_publish_env())),
    ids=lambda i: f"publish_q_{int(i)+1}",
)
def test_publish_question(case_index: int):
    """
    Тест публикации вопроса через админ-панель
    """
    # 1. Умная авторизация: получаем валидную куку без массового логина
    auth_manager = SmartAuthManager()
    # Подавляем побочные принты из процедуры авторизации: нам важен только итог публикации
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        session_cookie = auth_manager.get_valid_session_cookie(role=os.getenv("TEST_ROLE", "admin"))
    assert session_cookie, "Не удалось получить валидную сессионную куку"

    # 2. Получаем данные панели модерации
    parser = ModerationPanelParser()
    entries = parser.get_moderation_panel_data(session_cookie, limit=100)
    
    if not entries:
        pytest.fail("Не удалось получить данные панели модерации")
    
    # 3. Выбираем вопрос для публикации
    mode = os.getenv("PUBLISH_MODE", "latest")
    marker = os.getenv("PUBLISH_MARKER")
    user = os.getenv("PUBLISH_USER")
    
    try:
        question = select_question(entries, mode, marker, user)
        allure.dynamic.title(f"Публикация вопроса (ID: {question.get('id', 'N/A')})")
        
        # Логируем выбор
        logger.info(f"Выбран вопрос: ID={question.get('id')}, "
                   f"Пользователь={question.get('user')}, "
                   f"Текст={question.get('text')[:50]}...")
    except ValueError as e:
        pytest.fail(str(e))
    
    # 4. Формируем тело запроса
    # Получаем CSRF-токены с админ-страницы и готовим заголовки
    tokens = _fetch_csrf_tokens(parser.session, session_cookie)
    xsrf_token = unquote(tokens.get('xsrf_cookie') or '') if tokens.get('xsrf_cookie') else None
    form_token = tokens.get('form_token')

    extra: List[Tuple[str, str]] = []
    if form_token:
        extra.append(('_token', form_token))
    params_list = generate_params_list(question['id'], extra_params=extra)

    # 5. Отправляем запрос
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Origin': BASE_URL,
        'Referer': f'{BASE_URL}/admin/posts/new',
        'X-Requested-With': 'XMLHttpRequest',
    }
    if xsrf_token:
        headers['X-XSRF-TOKEN'] = xsrf_token
    if form_token:
        headers['X-CSRF-TOKEN'] = form_token

    try:
        # Отправляем через тот же session, чтобы сохранить куки и заголовки
        response = parser.session.post(
            f"{BASE_URL}{PUBLISH_ENDPOINT}",
            data=params_list,
            headers=headers,
            timeout=10
        )
    except Exception as e:
        pytest.fail(f"Ошибка при отправке запроса: {str(e)}")
    
    # 6. Проверяем результат
    # 6.1. Проверка HTTP статуса
    assert response.status_code == 200, (
        f"Неожиданный статус код: {response.status_code}. "
        f"Ответ: {response.text[:200]}..."
    )
    
    # 5.2. Проверка JSON ответа
    try:
        json_response = response.json()
    except Exception:
        pytest.fail(f"Невалидный JSON ответ: {response.text[:200]}...")
    
    # Прикрепляем диагностику в Allure
    from urllib.parse import urlencode
    allure.attach(urlencode(params_list), name="Request Payload", attachment_type=allure.attachment_type.TEXT)
    allure.attach(response.text, name="API Response", attachment_type=allure.attachment_type.TEXT)
    allure.attach(
        (
            "Выбранный вопрос:\n"
            f"ID: {question.get('id')}\n"
            f"Пользователь: {question.get('user')}\n"
            f"Дата: {question.get('date')}\n"
            f"Текст: {question.get('text')}"
        ),
        name="Question Details",
        attachment_type=allure.attachment_type.TEXT
    )
    
    # 5.3. Проверка успешности операции
    assert 'success' in json_response, "В ответе отсутствует ключ 'success'"
    assert json_response['success'] is True, (
        f"Ожидалось success=True, получено {json_response['success']}. "
        f"Сообщение: {json_response.get('message', 'N/A')}"
    )
    
    logger.info(f"Успешно опубликован вопрос ID={question['id']}")
    # Явный краткий вывод по сути теста: публикация вопроса
    print(f"✅ Вопрос опубликован: ID={question['id']}, success={json_response.get('success')}, message={json_response.get('message')}")

if __name__ == "__main__":
    # Для отладки
    pytest.main([__file__, '-s', '-v'])
