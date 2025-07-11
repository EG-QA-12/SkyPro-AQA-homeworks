"""
Утилиты для работы с URL-адресами в тестах.

Этот модуль содержит функции для генерации и проверки URL-адресов, используемых в тестах.
"""
from typing import Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

PARAM_NAME = "allow-session"
PARAM_VALUE = "1"


def is_headless() -> bool:
    """Определяет, запущен ли тест в headless-режиме.

    Возвращает True, если тесты запущены в headless-режиме. Проверяет переменную окружения HEADLESS
    или другие параметры запуска (можно доработать под нужды проекта).

    Returns:
        bool: True, если headless, иначе False.
    """
    import os
    value = os.getenv("HEADLESS", "false").lower()
    return value in ("1", "true", "yes")


def add_allow_session_param(url: str, headless: bool = True) -> str:
    """
    Добавляет параметр allow-session=2 к URL, если headless=True.
    Если параметр уже есть, URL не меняется.

    Args:
        url (str): Исходный URL.
        headless (bool): Флаг headless-режима.

    Returns:
        str: Модифицированный URL.

    Пример:
        >>> add_allow_session_param('https://site/page', True)
        'https://site/page?allow-session=2'
        >>> add_allow_session_param('https://site/page?foo=bar', True)
        'https://site/page?foo=bar&allow-session=2'
        >>> add_allow_session_param('https://site/page', False)
        'https://site/page'
    """
    if not headless:
        return url
    from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
    parsed = urlparse(url)
    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    if any(k == PARAM_NAME for k, _ in query_params):
        return url  # already present
    query_params.append((PARAM_NAME, "2"))
    new_query = urlencode(query_params)
    return urlunparse(parsed._replace(query=new_query))


def ensure_allow_session_param(url: str) -> str:
    """[Устарело] Используйте add_allow_session_param. Оставлено для обратной совместимости."""
    return add_allow_session_param(url, headless=True)


def build_url(base_url: str, path: str) -> str:
    """
    Формирует полный URL из базового адреса и относительного пути.

    Args:
        base_url (str): Базовый URL (например, 'https://ca.bll.by').
        path (str): Относительный путь (например, '/login').

    Returns:
        str: Полный URL, объединяющий базовый адрес и путь.

    Example:
        >>> build_url('https://ca.bll.by', '/login')
        'https://ca.bll.by/login'
    """
    if not base_url.endswith('/') and not path.startswith('/'):
        return f"{base_url}/{path}"
    elif base_url.endswith('/') and path.startswith('/'):
        return f"{base_url[:-1]}{path}"
    else:
        return f"{base_url}{path}"


def get_query_param(url: str, param: str) -> Optional[str]:
    """
    Извлекает значение параметра из строки URL.

    Args:
        url (str): URL-адрес, из которого нужно извлечь параметр.
        param (str): Имя параметра для поиска.

    Returns:
        Optional[str]: Значение параметра, если найден, иначе None.

    Example:
        >>> get_query_param('https://ca.bll.by/page?user=admin', 'user')
        'admin'
    """
    from urllib.parse import parse_qs, urlparse
    query = urlparse(url).query
    params = parse_qs(query)
    values = params.get(param)
    if values:
        return values[0]
    return None
