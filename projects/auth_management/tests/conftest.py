#!/usr/bin/env python3
"""
Пользовательские фикстуры pytest для auth_project.

Обеспечивает параметризацию тестов по пользователям и
универсальные фикстуры для авторизации.
"""

import pytest
from pathlib import Path
from typing import Optional


def pytest_addoption(parser):
    """Добавляет пользовательские опции командной строки."""
    parser.addoption(
        "--user-role",
        action="store",
        default="admin",
        help="Роль пользователя для авторизации (admin, moderator, expert, user, qa, tester)"
    )
    parser.addoption(
        "--user-login",
        action="store",
        default=None,
        help="Логин конкретного пользователя для авторизации (например: admin, DxYZ-Ab7, yR-SUV-t)"
    )


@pytest.fixture
def user_login(request):
    """
    Фикстура для получения логина пользователя из аргументов командной строки.
    
    Приоритет:
    1. --user-login (конкретный логин)
    2. --user-role (роль пользователя)
    3. По умолчанию "admin"
    """
    # Получаем значения из аргументов командной строки
    explicit_login = request.config.getoption("--user-login")
    user_role = request.config.getoption("--user-role")
    
    # Если указан конкретный логин, используем его
    if explicit_login:
        return explicit_login
    
    # Иначе, используем роль (для совместимости)
    return user_role


@pytest.fixture
def cookies_file_path(user_login):
    """
    Фикстура для получения пути к файлу кук для конкретного пользователя.
    
    Возвращает путь в формате: {user_login}_cookies.json
    """
    from src.config import config
    return config.COOKIES_PATH.parent / f"{user_login}_cookies.json"
