#!/usr/bin/env python3
"""
Тест для парсинга панели модерации

Выполняет запрос к панели модератора, парсит HTML и выводит список
последних вопросов и ответов.
"""

import pytest
import requests
import allure
from framework.utils.auth_cookie_provider import get_auth_cookies
from framework.utils.html_parser import ModerationPanelParser
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)



@allure.title("Парсинг панели модерации")
@allure.description("Получение и вывод списка последних вопросов и ответов из панели модерации")
@allure.feature("API тестирование")
@pytest.mark.api
def test_parse_moderation_panel():
    """
    Тест парсинга панели модерации
    
    Выполняет запрос к панели модератора, парсит HTML и выводит список
    последних вопросов и ответов.
    """
    # Получаем куку администратора локально, без сетевой авторизации
    cookies = get_auth_cookies(role="admin")
    session_cookie_item = next((c for c in cookies if c.get('name') == 'test_joint_session'), None)
    if not session_cookie_item:
        pytest.skip("Нет локальной куки admin (test_joint_session). Пропускаем быстрый парсинг")
    session_cookie = session_cookie_item["value"]
    
    # Создаем парсер панели модерации
    parser = ModerationPanelParser()
    
    # Получаем данные из панели модерации
    data = parser.get_moderation_panel_data(session_cookie, limit=5)
    
    # Проверяем, что данные получены
    assert len(data) > 0, "Не удалось получить данные из панели модерации"
    
    # Выводим таблицу с данными
    print("\n📋 Последние записи из панели модерации:")
    parser.print_table(data)
    
    # Проверяем наличие обязательных полей
    for entry in data:
        assert 'user' in entry, "Поле 'user' отсутствует в записи"
        assert 'date' in entry, "Поле 'date' отсутствует в записи"
        assert 'type' in entry, "Поле 'type' отсутствует в записи"
        assert 'text' in entry, "Поле 'text' отсутствует в записи"
    
    print(f"\n✅ Успешно получено {len(data)} записей из панели модерации")


if __name__ == "__main__":
    # Для отладки
    auth_manager = SmartAuthManager()
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")
    
    if session_cookie:
        parser = ModerationPanelParser()
        data = parser.get_moderation_panel_data(session_cookie, limit=5)
        parser.print_table(data)