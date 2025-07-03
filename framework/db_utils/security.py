"""Модуль для работы с безопасностью и хешированием паролей.

Содержит функции для хеширования и проверки паролей пользователей.
"""
import hashlib
from typing import Optional

def hash_password(password: str) -> str:
    """
    Хеширует пароль пользователя с помощью SHA-256.

    Args:
        password (str): Пароль в открытом виде.

    Returns:
        str: Хеш пароля в шестнадцатеричном виде.

    Example:
        >>> hash_password('password123')
        'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """
    Проверяет соответствие пароля и его хеша.

    Args:
        password (str): Пароль в открытом виде.
        password_hash (str): Ожидаемый хеш пароля.

    Returns:
        bool: True, если пароль соответствует хешу, иначе False.

    Example:
        >>> verify_password('password123', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f')
        True
    """
    return hash_password(password) == password_hash
