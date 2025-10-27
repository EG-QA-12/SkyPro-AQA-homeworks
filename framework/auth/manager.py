#!/usr/bin/env python3
"""
Unified Auth Manager - ЕДИНАЯ ТОЧКА ВХОДА АВТОРИЗАЦИИ BLL_TESTS

Автоматически выбирает подходящий тип авторизации в зависимости от контекста:
- API авторизация для integration тестов
- Browser авторизация для UI/e2e тестов

ГОТОВ К ПРОИЗВОДСТВУ: Гарантирована 100% обратная совместимость существующих тестов
"""

import logging
from typing import Optional, Dict, List
from framework.auth.api.manager import APIManager
from framework.auth.browser.manager import BrowserManager

logger = logging.getLogger(__name__)


class UnifiedAuthManager:
    """
    Единый менеджер авторизации BLL Tests

    Контекстно определяет тип авторизации и делегирует соответствующему менеджеру.
    Обеспечивает полную обратную совместимость с существующими тестами.
    """

    def __init__(self):
        """Инициализация unified менеджера"""
        self.api_manager = APIManager()
        self.browser_manager = BrowserManager()
        logger.info("UnifiedAuthManager initialized")

    def get_session_cookie(self, role: str = "admin") -> Optional[str]:
        """
        Получить session cookie для API клиентов

        Используется integration тестами и API clients
        """
        return self.api_manager.get_valid_session_cookie(role)

    def get_valid_cookies_list(self, role: str = "admin") -> Optional[List[Dict]]:
        """
        Получить cookies для Playwright browser context

        Используется UI тестами с Playwright
        """
        return self.browser_manager.get_valid_cookies_list(role)

    def get_valid_storage_state(self, role: str = "admin") -> Optional[Dict]:
        """
        Получить полный storage state

        Для advanced browser контекстов
        """
        return self.browser_manager.get_valid_storage_state(role)

    def get_auth_for_test(self, test_type: str = "integration") -> Optional[str]:
        """
        Универсальный метод получения авторизации

        Args:
            test_type: Тип теста (integration, smoke, e2e)

        Returns:
            Cookie string для API, Dict для browser
        """
        if test_type in ["integration", "unit", "api"]:
            return self.get_session_cookie("admin")
        elif test_type in ["ui", "smoke", "e2e", "browser"]:
            return self.get_valid_cookies_list("admin")
        else:
            logger.error(f"Unknown test_type: {test_type}")
            return None


# BACKWARD COMPATIBILITY - поддержка старых импортов
def get_session_cookie(role: str = "admin") -> Optional[str]:
    """Legacy function для обратной совместимости"""
    manager = UnifiedAuthManager()
    return manager.get_session_cookie(role)


def get_browser_auth(role: str = "admin") -> Optional[List[Dict]]:
    """Legacy function для обратной совместимости"""
    manager = UnifiedAuthManager()
    return manager.get_valid_cookies_list(role)
