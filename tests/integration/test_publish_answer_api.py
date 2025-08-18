#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест публикации (модерации) ответа через админ-API.

Сценарий:
1. Авторизация под ролью 'admin'.
2. Поиск в панели модерации самого свежего ответа, ожидающего публикации.
   - Уникальный признак такого ответа: Тип='П' и текст НЕ содержит 'Вопрос'.
3. Получение CSRF-токенов со страницы модерации.
4. Отправка POST-запроса на /admin/posts/update для изменения статуса ответа.
5. Проверка успешности операции по JSON-ответу.

Особенности:
- **Гибкая настройка через ENV:**
  - `PUBLISH_ANSWER_MODE`: `default`, `supportive`, `maximum`, `other`, `random`, `all`.
  - `PUBLISH_ANSWER_SELECTOR`: `latest` (по умолчанию), `by_user`, `by_marker`.
  - `TARGET_ANSWER_USER`, `TARGET_ANSWER_MARKER`: значения для селекторов.
- **Параметризация:** Режим `all` запускает 4 теста для каждого типа ответа.
- **Отказоустойчивость:** Используется `SmartAuthManager` для обработки 401/419.
- **Переиспользование кода:** Используется универсальная функция `find_entry_in_panel`.
"""

import os
import random
import logging
from typing import Dict, List, Optional, Tuple, Any

import pytest
import requests
import allure
from urllib.parse import unquote

from framework.utils.smart_auth_manager import SmartAuthManager
from framework.utils.html_parser import ModerationPanelParser, fetch_csrf_tokens_from_panel
from framework.utils.enums import AnswerPublicationType

logger = logging.getLogger(__name__)

# --- Конфигурация ---
BASE_URL = "https://expert.bll.by"
PUBLISH_ENDPOINT = "/admin/posts/update"

# --- Хелперы для параметризации ---

def get_answer_publication_modes() -> List[AnswerPublicationType]:
    """Определяет режимы для параметризации теста на основе ENV."""
    mode = os.getenv("PUBLISH_ANSWER_MODE", "default").lower()
    if mode == "all":
        return list(AnswerPublicationType)
    if mode == "random":
        return [random.choice(list(AnswerPublicationType))]
    
    # Сопоставляем строковое значение с членом Enum
    try:
        if mode == "default":
            return [AnswerPublicationType.ANSWER]
        return [AnswerPublicationType[mode.upper()]]
    except KeyError:
        # Если указан неверный режим, используем default
        logger.warning(f"Неизвестный режим '{mode}', используется 'default'")
        return [AnswerPublicationType.ANSWER]

# --- Основные функции теста ---

@pytest.fixture
def fx_auth_manager() -> SmartAuthManager:
    return SmartAuthManager()

@pytest.fixture
def fx_panel_parser() -> ModerationPanelParser:
    return ModerationPanelParser()

@allure.title("Публикация ответа через админ-API: {pub_type}")
@allure.feature("API Тестирование")
@pytest.mark.api
@pytest.mark.parametrize(
    "pub_type",
    get_answer_publication_modes(),
    ids=lambda pt: pt.name.lower()
)
def test_publish_answer(
    fx_auth_manager: SmartAuthManager,
    fx_panel_parser: ModerationPanelParser,
    pub_type: AnswerPublicationType,
):
    """
    Основной тест для модерации и публикации ответа.
    """
    with allure.step("1. Получение валидной сессии администратора"):
        session_cookie = fx_auth_manager.get_valid_session_cookie(role="admin")
        assert session_cookie, "Не удалось получить валидную сессионную куку"

    with allure.step("2. Поиск ответа для публикации в панели модерации"):
        selector = os.getenv("PUBLISH_ANSWER_SELECTOR", "latest").lower()
        user_val = os.getenv("TARGET_ANSWER_USER")
        marker_val = os.getenv("TARGET_ANSWER_MARKER")

        search_criteria = {
            "entry_type": "П",
            "text_not_contains": "Вопрос",
        }
        if selector == "by_user" and user_val:
            search_criteria["user"] = user_val
        elif selector == "by_marker" and marker_val:
            search_criteria["text_contains"] = marker_val

        answer_to_publish = fx_panel_parser.find_entry_in_panel(session_cookie, **search_criteria)
        if not answer_to_publish:
            pytest.fail(f"Не найден ответ для публикации по критериям: {search_criteria}")

        answer_id = answer_to_publish.get("id")
        assert answer_id, "В найденной записи ответа отсутствует ID"
        logger.info(f"Найден ответ для публикации: ID={answer_id}, Текст='{answer_to_publish.get('text', '')[:50]}...'")

    with allure.step("2.5. Взятие ответа в работу (Assign)"):
        # Используем ту же логику получения токенов, что работает в test_publish_question_api.py
        assign_url = f"{BASE_URL}/admin/posts/assign/{answer_id}"
        
        # Сначала синхронизируем сессию парсера с кукой администратора
        fx_panel_parser.session.cookies.set("test_joint_session", session_cookie)
        
        # Получаем свежие CSRF-токены для assign-запроса
        tokens = fetch_csrf_tokens_from_panel(fx_panel_parser.session, BASE_URL)
        xsrf_token = unquote(tokens.get('xsrf_cookie') or '') if tokens.get('xsrf_cookie') else None
        
        if not xsrf_token:
            pytest.fail("Не удалось получить XSRF-токен для assign-запроса")
        
        assign_headers = {
            'Accept': '*/*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': BASE_URL,
            'Referer': f'{BASE_URL}/admin/posts/new',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-TOKEN': tokens.get('form_token'),
            'X-XSRF-TOKEN': xsrf_token,
        }
        
        try:
            assign_response = fx_panel_parser.session.patch(
                assign_url,
                headers=assign_headers,
                timeout=10
            )
            
            # Если получили 401/419, пробуем переавторизоваться (по аналогии с test_publish_question_api.py)
            if assign_response.status_code in (401, 419):
                logger.warning(f"Получен статус {assign_response.status_code} при assign. Попытка реавторизации...")
                
                # Получаем новую куку
                auth_manager = SmartAuthManager()
                new_cookie = auth_manager.get_valid_session_cookie(role="admin")
                if not new_cookie:
                    pytest.fail("Не удалось получить новую куку для повторного assign")
                
                # Обновляем сессию парсера
                fx_panel_parser.session.cookies.clear()
                fx_panel_parser.session.cookies.set("test_joint_session", new_cookie)
                
                # Получаем новые токены и повторяем запрос
                tokens = fetch_csrf_tokens_from_panel(fx_panel_parser.session, BASE_URL)
                xsrf_token = unquote(tokens.get('xsrf_cookie') or '') if tokens.get('xsrf_cookie') else None
                
                if xsrf_token:
                    assign_headers['X-XSRF-TOKEN'] = xsrf_token
                    assign_headers['X-CSRF-TOKEN'] = tokens.get('form_token')
                    assign_response = fx_panel_parser.session.patch(
                        assign_url,
                        headers=assign_headers,
                        timeout=10
                    )
            
            allure.attach(
                f"URL: {assign_url}\nStatus: {assign_response.status_code}\nResponse: {assign_response.text}",
                name="Assign API Response",
                attachment_type=allure.attachment_type.TEXT
            )
            
            assert assign_response.status_code == 200, f"Не удалось 'взять в работу' ответ ID={answer_id}. Статус: {assign_response.status_code}"
            logger.info(f"Успешно 'взят в работу' ответ ID={answer_id}")
            
        except requests.RequestException as e:
            pytest.fail(f"Ошибка при выполнении assign для ответа ID={answer_id}: {str(e)}")

    with allure.step("3. Отправка запроса на публикацию"):
        payload = {
            'id': answer_id,
            'post_type_id': pub_type.value,
            'status_id': 3,
            'answered': 1,
            'rejection_reason_id': 0,
            'moder_msg': '',
            'delete_reason': 0,
            'hand_over_moderator': '',
        }
        
        # Синхронизируем сессию SmartAuthManager с сессией парсера перед публикацией
        fx_auth_manager.session.cookies.clear()
        fx_auth_manager.session.cookies.update(fx_panel_parser.session.cookies)
        
        # Делегируем отправку SmartAuthManager для отказоустойчивости
        result = fx_auth_manager.publish_answer_with_retry(
            role="admin",
            payload=payload
        )

    with allure.step("4. Проверка ответа API"):
        allure.attach(str(payload), name="Request Payload", attachment_type=allure.attachment_type.TEXT)
        allure.attach(result.get("response_text", ""), name="API Response", attachment_type=allure.attachment_type.TEXT)

        assert result.get("success") is True, f"Ожидался success=True. Ответ: {result.get('response_text')}"
        
        json_response = result.get("json_response")
        logger.info(f"Успешно опубликован ответ ID={answer_id} с типом '{pub_type.name}'. Сообщение: {json_response.get('message')}")
        print(f"✅ Ответ ID={answer_id} опубликован. Message: {json_response.get('message')}")
