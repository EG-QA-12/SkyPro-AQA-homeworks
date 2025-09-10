"""
Вспомогательные утилиты для системы авторизации.

Содержит базовые функции для работы с куками и валидации авторизации.
"""

from __future__ import annotations
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def validate_cookie(cookie: str, required_role: str = "any") -> bool:
    """
    Проверяет базовую валидность значения авторизационной куки.
    
    Args:
        cookie: Значение авторизационной куки
        required_role: Требуемая роль (для совместимости)
        
    Returns:
        True если кука валидна, иначе False
    """
    if not isinstance(cookie, str):
        return False
    
    value = cookie.strip()
    if not value:
        return False
    
    if len(value) < 8:
        return False
        
    if " " in value:
        return False
        
    return True


def save_cookie(cookie: str, path: str) -> None:
    """
    Сохраняет значение куки в текстовый файл.
    
    Args:
        cookie: Значение авторизационной куки
        path: Путь к файлу для сохранения
        
    Raises:
        ValueError: Если значение куки некорректно
        OSError: Ошибки файловой системы
    """
    if not validate_cookie(cookie):
        raise ValueError("Невалидное значение куки")
    
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(cookie, encoding="utf-8")
    logger.debug(f"Кука сохранена в {path}")


def load_cookie(path: str) -> str:
    """
    Загружает значение куки из текстового файла.
    
    Args:
        path: Путь к файлу с кукой
        
    Returns:
        Значение куки
        
    Raises:
        FileNotFoundError: Если файл не найден
        ValueError: Если значение куки пустое
    """
    try:
        value = Path(path).read_text(encoding="utf-8").strip()
        if not value:
            raise ValueError(f"Файл {path} содержит пустое значение куки")
        return value
    except FileNotFoundError:
        logger.warning(f"Файл куки не найден: {path}")
        raise


def get_cookie_path(role: str) -> str:
    """
    Возвращает стандартный путь к файлу с куками для роли.
    
    Args:
        role: Роль пользователя
        
    Returns:
        Путь к файлу куки
    """
    project_root = Path(__file__).parent.parent.parent
    cookies_dir = project_root / "cookies"
    return str(cookies_dir / f"{role}_session.txt")


class AuthError(Exception):
    """Базовое исключение для авторизации."""
    pass


class InvalidCookieError(AuthError):
    """Исключение для невалидных кук."""
    pass


class AuthConfigError(AuthError):
    """Исключение для ошибок конфигурации авторизации."""
    pass
