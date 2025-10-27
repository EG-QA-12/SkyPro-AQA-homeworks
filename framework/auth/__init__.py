#!/usr/bin/env python3
"""
Unified Authentication Framework for BLL Tests

Предоставляет единую точку входа для всех типов авторизации:
- API авторизация для integration тестов
- Browser авторизация для UI/e2e тестов

Автоматически выбирает подходящий тип авторизации по контексту.
"""

from framework.auth.manager import UnifiedAuthManager
from framework.auth.api.manager import APIManager
from framework.auth.browser.manager import BrowserManager

__version__ = "1.0.0"

# Unified interface - ЕДИНАЯ ТОЧКА ВХОДА
auth_manager = UnifiedAuthManager()

# Legacy compatibility methods
def get_session_cookie(role: str = "admin") -> str:
    """Устаревший метод для обратной совместимости"""
    return auth_manager.get_session_cookie(role)

def get_browser_auth(role: str = "admin"):
    """Устаревший метод для обратной совместимости"""
    return auth_manager.get_valid_cookies_list(role)

__all__ = [
    "UnifiedAuthManager",
    "APIManager",
    "BrowserManager",
    "auth_manager",
    "get_session_cookie",
    "get_browser_auth"
]
