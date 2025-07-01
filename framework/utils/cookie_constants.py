"""Константы и вспомогательные функции для работы с авторизационной кукой.

Все тесты и утилиты должны использовать только куку с именем
`test_joint_session`. Значение куки отличается у разных пользователей и
передаётся динамически (получается после логина).
"""
from __future__ import annotations

from typing import Dict

# Имя единственной авторизационной куки, используемой во всех тестах
COOKIE_NAME: str = "test_joint_session"

LOGIN_URL = "https://ca.bll.by/login"


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

