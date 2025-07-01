"""Модуль для работы с паролями.

Содержит функции хеширования и проверки паролей.
"""
import bcrypt

def hash_password(password: str) -> str:
    """Хеширует пароль с использованием bcrypt.
    
    Args:
        password: Пароль в открытом виде.
        
    Returns:
        Хешированный пароль.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля его хешу.
    
    Args:
        plain_password: Пароль в открытом виде.
        hashed_password: Хешированный пароль.
        
    Returns:
        True если пароль верный, иначе False.
    """
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
