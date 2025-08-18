"""
Централизованные фикстуры для авторизации.

Этот модуль предоставляет удобные фикстуры для работы с авторизацией
в тестах, включая различные режимы и роли пользователей.
"""

import pytest
import logging
from typing import Dict, Optional
from framework.api.admin_client import AdminAPIClient
from framework.utils.auth_cookie_provider import AuthCookieProvider
from framework.utils.smart_auth_manager import SmartAuthManager

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def auth_manager() -> SmartAuthManager:
    """
    Фикстура для получения менеджера авторизации.
    
    Returns:
        SmartAuthManager: Менеджер авторизации
    """
    return SmartAuthManager()


@pytest.fixture(scope="session")
def cookie_provider() -> AuthCookieProvider:
    """
    Фикстура для получения провайдера кук.
    
    Returns:
        AuthCookieProvider: Провайдер кук авторизации
    """
    return AuthCookieProvider()


@pytest.fixture
def admin_client() -> AdminAPIClient:
    """
    Фикстура для получения административного API клиента.
    
    Returns:
        AdminAPIClient: Административный клиент
    
    Example:
        def test_publish_question(admin_client):
            response = admin_client.submit_question("Тестовый вопрос")
            assert response.success
    """
    client = AdminAPIClient(role="admin")
    yield client
    client.close()


@pytest.fixture
def user_client() -> AdminAPIClient:
    """
    Фикстура для получения пользовательского API клиента.
    
    Returns:
        AdminAPIClient: Пользовательский клиент
    """
    client = AdminAPIClient(role="user")
    yield client
    client.close()


@pytest.fixture
def moderator_client() -> AdminAPIClient:
    """
    Фикстура для получения клиентского API модератора.
    
    Returns:
        AdminAPIClient: Клиент модератора
    """
    client = AdminAPIClient(role="moderator")
    yield client
    client.close()


@pytest.fixture
def session_cookie(auth_manager: SmartAuthManager, request) -> str:
    """
    Фикстура для получения валидной сессионной куки.
    
    Args:
        auth_manager: Менеджер авторизации
        request: Объект запроса pytest
        
    Returns:
        str: Валидная сессионная кука
        
    Example:
        def test_api_call(session_cookie):
            # Используем куку в запросе
            pass
    """
    # Получаем роль из параметров теста или используем по умолчанию
    role = getattr(request, 'param', 'admin')
    cookie = auth_manager.get_valid_session_cookie(role=role)
    
    if not cookie:
        pytest.fail(f"Не удалось получить валидную сессионную куку для роли: {role}")
    
    return cookie


@pytest.fixture
def fresh_session_cookie(auth_manager: SmartAuthManager, request) -> str:
    """
    Фикстура для получения свежей сессионной куки (с принудительным обновлением).
    
    Args:
        auth_manager: Менеджер авторизации
        request: Объект запроса pytest
        
    Returns:
        str: Свежая сессионная кука
    """
    # Получаем роль из параметров теста или используем по умолчанию
    role = getattr(request, 'param', 'admin')
    cookie = auth_manager.get_valid_session_cookie(role=role, force_refresh=True)
    
    if not cookie:
        pytest.fail(f"Не удалось получить свежую сессионную куку для роли: {role}")
    
    return cookie


@pytest.fixture
def api_clients() -> Dict[str, AdminAPIClient]:
    """
    Фикстура для получения словаря API клиентов для разных ролей.
    
    Returns:
        Dict[str, AdminAPIClient]: Словарь клиентов по ролям
    """
    clients = {
        'admin': AdminAPIClient(role="admin"),
        'user': AdminAPIClient(role="user"),
        'moderator': AdminAPIClient(role="moderator"),
    }
    
    yield clients
    
    # Закрываем все клиенты
    for client in clients.values():
        client.close()


# Параметризованные фикстуры для тестирования разных ролей

@pytest.fixture(params=["admin", "user", "moderator"])
def user_role(request) -> str:
    """
    Параметризованная фикстура для тестирования разных ролей.
    
    Args:
        request: Объект запроса pytest
        
    Returns:
        str: Роль пользователя
    """
    return request.param


@pytest.fixture
def role_client(request) -> AdminAPIClient:
    """
    Параметризованная фикстура для получения клиента по роли.
    
    Args:
        request: Объект запроса pytest
        
    Returns:
        AdminAPIClient: Клиент для указанной роли
    """
    role = getattr(request, 'param', 'admin')
    client = AdminAPIClient(role=role)
    yield client
    client.close()


# Утилиты для работы с фикстурами

class AuthTestHelper:
    """
    Вспомогательный класс для тестов авторизации.
    
    Предоставляет удобные методы для проверки авторизации
    и работы с куками в тестах.
    """
    
    def __init__(self, auth_manager: SmartAuthManager):
        """
        Инициализация помощника.
        
        Args:
            auth_manager: Менеджер авторизации
        """
        self.auth_manager = auth_manager
    
    def get_valid_cookie(self, role: str = "admin") -> str:
        """
        Получение валидной куки для указанной роли.
        
        Args:
            role: Роль пользователя
            
        Returns:
            str: Валидная сессионная кука
        """
        cookie = self.auth_manager.get_valid_session_cookie(role=role)
        if not cookie:
            raise ValueError(f"Не удалось получить валидную куку для роли: {role}")
        return cookie
    
    def refresh_cookie(self, role: str = "admin") -> str:
        """
        Принудительное обновление куки для указанной роли.
        
        Args:
            role: Роль пользователя
            
        Returns:
            str: Обновленная сессионная кука
        """
        cookie = self.auth_manager.get_valid_session_cookie(role=role, force_refresh=True)
        if not cookie:
            raise ValueError(f"Не удалось обновить куку для роли: {role}")
        return cookie
    
    def validate_cookie(self, cookie: str, role: str = "admin") -> bool:
        """
        Проверка валидности куки.
        
        Args:
            cookie: Кука для проверки
            role: Ожидаемая роль
            
        Returns:
            bool: True если кука валидна
        """
        from framework.utils.auth_utils import validate_cookie
        return validate_cookie(cookie, required_role=role)


@pytest.fixture
def auth_helper(auth_manager: SmartAuthManager) -> AuthTestHelper:
    """
    Фикстура для получения помощника тестов авторизации.
    
    Args:
        auth_manager: Менеджер авторизации
        
    Returns:
        AuthTestHelper: Помощник тестов авторизации
    """
    return AuthTestHelper(auth_manager)
