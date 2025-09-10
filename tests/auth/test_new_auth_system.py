"""
Тестирование новой системы авторизации.
"""

import pytest
from framework.auth import AuthManager, CookieProvider, validate_cookie


class TestNewAuthSystem:
    """Тесты для новой системы авторизации."""

    def test_auth_manager_initialization(self):
        """Проверяет инициализацию AuthManager."""
        manager = AuthManager()
        assert manager is not None
        assert hasattr(manager, 'cache_timeout')
        assert hasattr(manager, '_cache')

    def test_cookie_provider_initialization(self):
        """Проверяет инициализацию CookieProvider."""
        provider = CookieProvider()
        assert provider is not None

    def test_cookie_validation(self):
        """Проверяет валидацию кук."""
        # Валидная кука
        valid_cookie = "valid_session_token_123"
        assert validate_cookie(valid_cookie) is True
        
        # Невалидные куки
        assert validate_cookie("") is False
        assert validate_cookie("   ") is False
        assert validate_cookie("abc") is False  # слишком короткая
        assert validate_cookie("token with spaces") is False

    def test_auth_manager_cache_mechanism(self):
        """Проверяет механизм кэширования AuthManager."""
        manager = AuthManager(cache_timeout=1)  # 1 секунда для теста
        
        # Проверяем, что кэш пуст
        assert not manager._cache
        
        # Проверяем валидность несуществующего кэша
        assert manager._is_cache_valid("admin") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
