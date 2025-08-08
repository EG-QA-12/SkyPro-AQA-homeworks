#!/usr/bin/env python3
"""
Конфигурация тестов для интеграционных тестов

Содержит фикстуры для подготовки данных и авторизации,
соблюдая принцип изоляции и атомарности тестов.
"""

import pytest
from config.secrets_manager import SecretsManager
from framework.utils.simple_api_auth import mass_api_auth
from framework.utils.auth_cookie_provider import get_auth_cookies


@pytest.fixture(scope="session")
def auth_session():
    """
    Фикстура для массовой авторизации пользователей
    
    Область видимости session - авторизация выполняется один раз
    для всей сессии тестов, что повышает производительность.
    
    Returns:
        dict: Результаты авторизации
    """
    # Загружаем тестовых пользователей
    test_users = SecretsManager.load_users_from_csv()
    if not test_users:
        pytest.skip("Нет тестовых пользователей")
    
    # Выполняем массовую авторизацию
    auth_results = mass_api_auth(users=test_users, threads=5)
    
    return {
        "users": test_users,
        "results": auth_results
    }


@pytest.fixture
def admin_cookies(auth_session):
    """
    Фикстура для получения куки администратора
    
    Зависит от auth_session, поэтому авторизация выполняется
    автоматически перед получением куки.
    
    Args:
        auth_session: Результаты авторизации
        
    Returns:
        list: Список куки администратора
    """
    admin_cookies = get_auth_cookies(role="admin")
    
    if not admin_cookies:
        pytest.fail("Не удалось получить куки администратора")
    
    return admin_cookies


@pytest.fixture
def session_cookie(admin_cookies):
    """
    Фикстура для получения сессионной куки
    
    Извлекает конкретную куку test_joint_session из списка
    куки администратора.
    
    Args:
        admin_cookies: Список куки администратора
        
    Returns:
        str: Значение сессионной куки
        
    Raises:
        pytest.fail: Если кука не найдена
    """
    session_cookie = next(
        (cookie for cookie in admin_cookies if cookie['name'] == "test_joint_session"), 
        None
    )
    
    if not session_cookie:
        pytest.fail("Кука test_joint_session не найдена")
    
    return session_cookie["value"]
