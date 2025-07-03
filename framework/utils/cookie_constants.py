"""
Константы для работы с cookies и авторизацией.

Этот модуль содержит все основные константы, используемые для работы с cookie-файлами и авторизацией в тестах.
"""
from __future__ import annotations

from typing import Dict

# Имя основной cookie авторизации
COOKIE_NAME: str = "test_joint_session"

# URL страницы логина (используется для прямых переходов в тестах)
LOGIN_URL: str = "https://ca.bll.by/login"


def joint_cookie(value: str, domain: str, path: str = "/") -> Dict[str, str]:
    """Создаёт словарь куки Playwright формата с именем `test_joint_session`.

    Args:
        value: Значение куки (уникально для каждого авторизованного пользователя).
        domain: Домен сайта, для которого устанавливается кука.
        path: Путь куки. По умолчанию ``"/"``.

    Returns:
        Словарь, совместимый с ``BrowserContext.add_cookies``.
    """
    return {"name": COOKIE_NAME, "value": value, "domain": domain, "path": path}

