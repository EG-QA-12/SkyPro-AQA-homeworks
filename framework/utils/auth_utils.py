"""Утилиты для работы с авторизационными куками и сессиями.

Модуль предоставляет функции для сохранения/загрузки значения авторизационной
куки, а также универсальную проверку валидности куки без сетевых запросов.

Функции спроектированы с акцентом на простоту и устойчивость:
- Не зависят от внешних сервисов (нет сетевых проверок);
- Подходят для юнит/интеграционных тестов и локального запуска;
- Обеспечивают чёткие типы и сообщения об ошибках.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict


def validate_cookie(cookie: str, required_role: str) -> bool:
    """Проверяет базовую валидность значения авторизационной куки.

    Проверка преднамеренно «лёгкая», без сетевых запросов:
    - значение должно быть непустой строкой;
    - не должно состоять из одних пробельных символов;
    - разумная минимальная длина (>= 8 символов);

    Параметр ``required_role`` зарезервирован для будущих проверок
    соответствия роли. Сейчас не используется, но сохраняется для
    совместимости вызовов по всему проекту.

    Args:
        cookie: Значение авторизационной куки ``test_joint_session``.
        required_role: Требуемая роль пользователя (например, ``"admin"``).

    Returns:
        True, если значение похоже на валидное; иначе False.
    """
    # Параметр сохраняется для совместимости API, используем как заглушку,
    # чтобы удовлетворить строгий линтер без изменения сигнатуры.
    _ = required_role

    # Базовая проверка типа роли позволяет задействовать аргумент в валидации,
    # сохраняя совместимость API и устраняя предупреждение линтера.
    if required_role is not None and not isinstance(required_role, str):
        return False

    if not isinstance(cookie, str):
        return False
    value: str = cookie.strip()
    if not value:
        return False
    if len(value) < 8:
        return False
    if " " in value:
        return False
    return True


def save_cookie(cookie: str, path: str) -> None:
    """Сохраняет значение куки в текстовый файл.

    Файл создаётся вместе с недостающими директориями.

    Args:
        cookie: Значение авторизационной куки.
        path: Путь к файлу, куда будет записано значение.

    Raises:
        ValueError: Если значение куки некорректно.
        OSError: Ошибки файловой системы при записи.
    """
    if not validate_cookie(cookie, required_role="any"):
        raise ValueError("Невалидное значение куки: пусто или слишком короткое")
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(cookie, encoding="utf-8")


def load_cookie(path: str) -> str:
    """Загружает значение куки из текстового файла.

    Args:
        path: Путь к файлу с сохранённым значением куки.

    Returns:
        Строка со значением куки.

    Raises:
        FileNotFoundError: Если файл отсутствует.
        OSError: Ошибки чтения файла.
        ValueError: Если считано пустое значение.
    """
    value = Path(path).read_text(encoding="utf-8").strip()
    if not value:
        raise ValueError(f"Файл {path} прочитан, но значение куки пустое")
    return value


class SecureAuthManager:
    """Условный менеджер безопасной авторизации.

    Используется как лёгкая заглушка для совместимости.
    Реальных сетевых операций не выполняет.
    """

    def __init__(self) -> None:
        self.cookies: Dict[str, str] = {}


class UnifiedAuthManager:
    """Условный унифицированный менеджер авторизации.

    Поддерживает интерфейс совместимости, не выполняя реальных сетевых операций.
    """

    def __init__(self) -> None:
        self.sessions: Dict[str, str] = {}
