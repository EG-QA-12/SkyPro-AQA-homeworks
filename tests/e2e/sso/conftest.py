"""
Фикстуры для SSO тестирования через requests API.

Обеспечивает изолированные HTTP сессии и случайный выбор пользователей
для тестирования авторизации между доменами.
"""
from __future__ import annotations

import pytest
import random
from typing import Dict, List, Any
from pathlib import Path

from framework.utils.sso_requests import SSORequestsClient, get_available_users
from tests.e2e.sso.constants import SSOTestConfig


@pytest.fixture
def isolated_sso_client() -> SSORequestsClient:
    """
    Создает изолированный SSO клиент для каждого теста.
    
    Обеспечивает полную изоляцию между тестами - каждый тест
    получает новую HTTP сессию без кук и состояния.
    
    Returns:
        Новый SSO клиент с чистой сессией
    """
    client = SSORequestsClient(timeout=SSOTestConfig.REQUEST_TIMEOUT)
    
    yield client
    
    # Очистка ресурсов после теста
    client.close()


@pytest.fixture
def random_user_cookies(isolated_sso_client: SSORequestsClient) -> Dict[str, Any]:
    """
    Загружает куки случайного пользователя для тестирования.
    
    Args:
        isolated_sso_client: Изолированный SSO клиент
        
    Returns:
        Словарь с данными пользователя и куками
        
    Raises:
        pytest.skip: Если нет доступных пользователей для тестирования
    """
    available_users = get_available_users()
    
    if not available_users:
        pytest.skip("Нет доступных файлов кук для тестирования SSO")
    
    # Выбираем случайного пользователя
    selected_user = random.choice(available_users)
    
    try:
        # Загружаем куки пользователя
        user_cookies = isolated_sso_client.load_user_cookies(selected_user)
        
        if not user_cookies:
            pytest.skip(f"Файл кук пользователя {selected_user} пуст или поврежден")
        
        return {
            "username": selected_user,
            "cookies": user_cookies,
            "cookies_count": len(user_cookies)
        }
        
    except Exception as e:
        pytest.skip(f"Ошибка загрузки кук пользователя {selected_user}: {e}")


@pytest.fixture
def admin_user_cookies(isolated_sso_client: SSORequestsClient) -> Dict[str, Any]:
    """
    Загружает куки администратора для критичных тестов.
    
    Args:
        isolated_sso_client: Изолированный SSO клиент
        
    Returns:
        Словарь с данными админа и куками
        
    Raises:
        pytest.skip: Если куки админа недоступны
    """
    try:
        admin_cookies = isolated_sso_client.load_user_cookies("admin")
        
        if not admin_cookies:
            pytest.skip("Куки администратора недоступны для тестирования")
        
        return {
            "username": "admin",
            "cookies": admin_cookies,
            "cookies_count": len(admin_cookies)
        }
        
    except Exception as e:
        pytest.skip(f"Ошибка загрузки кук администратора: {e}")


@pytest.fixture
def specific_user_cookies(isolated_sso_client: SSORequestsClient):
    """
    Фабрика для загрузки кук конкретного пользователя.
    
    Args:
        isolated_sso_client: Изолированный SSO клиент
        
    Returns:
        Функция для загрузки кук по имени пользователя
    """
    def _load_user_cookies(username: str) -> Dict[str, Any]:
        """
        Загружает куки указанного пользователя.
        
        Args:
            username: Имя пользователя
            
        Returns:
            Словарь с данными пользователя и куками
        """
        try:
            user_cookies = isolated_sso_client.load_user_cookies(username)
            
            if not user_cookies:
                raise ValueError(f"Куки пользователя {username} пусты или повреждены")
            
            return {
                "username": username,
                "cookies": user_cookies,
                "cookies_count": len(user_cookies)
            }
            
        except Exception as e:
            raise ValueError(f"Ошибка загрузки кук пользователя {username}: {e}")
    
    return _load_user_cookies


@pytest.fixture
def sso_test_info() -> Dict[str, Any]:
    """
    Предоставляет информацию о текущем SSO тесте.
    
    Returns:
        Словарь с метаданными тестирования
    """
    available_users = get_available_users()
    cookies_dir = Path(SSOTestConfig.COOKIES_DIR)
    
    return {
        "available_users": available_users,
        "users_count": len(available_users),
        "cookies_dir_exists": cookies_dir.exists(),
        "timeout": SSOTestConfig.REQUEST_TIMEOUT,
        "expected_cookie_name": SSOTestConfig.COOKIE_NAME,
        "test_domain": SSOTestConfig.COOKIE_DOMAIN
    }


@pytest.fixture(scope="session")
def sso_session_info() -> Dict[str, Any]:
    """
    Информация о сессии тестирования SSO (создается один раз за сессию).
    
    Returns:
        Словарь с информацией о доступных ресурсах для тестирования
    """
    available_users = get_available_users()
    cookies_dir = Path(SSOTestConfig.COOKIES_DIR)
    
    # Проверяем наличие кук для ключевых пользователей
    key_users = ["admin", "user", "moderator", "expert"]
    available_key_users = [user for user in key_users if user in available_users]
    
    session_info = {
        "total_users": len(available_users),
        "available_users": available_users,
        "key_users_available": available_key_users,
        "cookies_directory": str(cookies_dir),
        "cookies_dir_exists": cookies_dir.exists(),
        "has_admin_cookies": "admin" in available_users,
        "random_test_possible": len(available_users) > 0
    }
    
    return session_info 