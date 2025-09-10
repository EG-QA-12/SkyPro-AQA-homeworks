"""
Модуль авторизации для фреймворка автотестов.

Этот модуль предоставляет единую точку доступа для всех операций авторизации,
следуя принципам Page Object и обеспечивая обратную совместимость.
"""

from .auth_manager import AuthManager, get_session_cookie, get_auth_cookies
from .cookie_provider import CookieProvider
from .auth_utils import validate_cookie, save_cookie, load_cookie, AuthError

__all__ = [
    "AuthManager",
    "CookieProvider", 
    "validate_cookie",
    "save_cookie", 
    "load_cookie",
    "get_session_cookie",
    "get_auth_cookies",
    "AuthError"
]
