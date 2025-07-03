"""
Утилиты для работы с URL-адресами в тестах.

Этот модуль содержит функции для генерации и проверки URL-адресов, используемых в тестах.
"""
from typing import Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

PARAM_NAME = "allow-session"
PARAM_VALUE = "1"


def ensure_allow_session_param(url: str) -> str:
    """Return *url* with ``allow-session=1`` query parameter present.

    The order of query parameters is preserved (new param appended).  If the
    parameter already present we keep the original url unchanged.
    """
    parsed = urlparse(url)
    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    if any(k == PARAM_NAME for k, _ in query_params):
        return url  # already present
    query_params.append((PARAM_NAME, PARAM_VALUE))
    new_query = urlencode(query_params)
    return urlunparse(parsed._replace(query=new_query))


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
