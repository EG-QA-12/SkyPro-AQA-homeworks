"""
Утилиты для улучшения сообщений об ошибках HTTP статусов в тестах.

Предоставляет функции для создания понятных сообщений об ошибках
с классификацией типов ошибок (клиентские/серверные).
"""

from typing import List


def get_http_error_message(
    actual_status: int,
    expected_statuses: List[int],
    url: str,
    context: str = ""
) -> str:
    """
    Создает понятное сообщение об ошибке HTTP статуса.

    Args:
        actual_status: Фактический HTTP статус код
        expected_statuses: Список ожидаемых статус кодов
        url: URL, для которого проверялся статус
        context: Дополнительный контекст (например, название теста)

    Returns:
        str: Понятное сообщение об ошибке с классификацией типа ошибки
    """
    expected_str = ", ".join(map(str, expected_statuses))

    # Определяем тип ошибки
    if 400 <= actual_status < 500:
        error_type = "КЛИЕНТСКАЯ ОШИБКА (4XX)"
        error_desc = _get_client_error_description(actual_status)
    elif 500 <= actual_status < 600:
        error_type = "СЕРВЕРНАЯ ОШИБКА (5XX)"
        error_desc = _get_server_error_description(actual_status)
    else:
        error_type = "НЕОЖИДАННЫЙ СТАТУС"
        error_desc = "Неизвестный тип ошибки"

    context_msg = f" [{context}]" if context else ""

    return (
        f"❌ {error_type}{context_msg}\n"
        f"   Ожидался один из статусов: {expected_str}\n"
        f"   Получен статус: {actual_status} ({error_desc})\n"
        f"   URL: {url}"
    )


def _get_client_error_description(status: int) -> str:
    """Возвращает описание клиентской ошибки."""
    descriptions = {
        400: "Bad Request - некорректный запрос",
        401: "Unauthorized - требуется авторизация",
        403: "Forbidden - доступ запрещен",
        404: "Not Found - ресурс не найден",
        405: "Method Not Allowed - метод не разрешен",
        408: "Request Timeout - таймаут запроса",
        409: "Conflict - конфликт с текущим состоянием",
        410: "Gone - ресурс больше не доступен",
        422: "Unprocessable Entity - некорректные данные",
        429: "Too Many Requests - слишком много запросов",
    }
    return descriptions.get(status, "Неизвестная клиентская ошибка")


def _get_server_error_description(status: int) -> str:
    """Возвращает описание серверной ошибки."""
    descriptions = {
        500: "Internal Server Error - внутренняя ошибка сервера",
        501: "Not Implemented - функция не реализована",
        502: "Bad Gateway - плохой шлюз",
        503: "Service Unavailable - сервис недоступен",
        504: "Gateway Timeout - таймаут шлюза",
        505: "HTTP Version Not Supported - версия HTTP не поддерживается",
    }
    return descriptions.get(status, "Неизвестная серверная ошибка")


def assert_http_status_with_better_message(
    response_status: int,
    expected_statuses: List[int],
    url: str,
    context: str = ""
) -> None:
    """
    Проверяет HTTP статус с понятным сообщением об ошибке.

    Args:
        response_status: Фактический статус код ответа
        expected_statuses: Список разрешенных статус кодов
        url: URL для которого проверялся статус
        context: Контекст проверки (для сообщения об ошибке)

    Raises:
        AssertionError: Если статус не входит в список разрешенных
    """
    if response_status not in expected_statuses:
        error_message = get_http_error_message(
            response_status, expected_statuses, url, context
        )
        raise AssertionError(error_message)