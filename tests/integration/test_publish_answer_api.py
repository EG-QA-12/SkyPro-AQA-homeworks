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
from framework.utils.html_parser import ModerationPanelParser
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
