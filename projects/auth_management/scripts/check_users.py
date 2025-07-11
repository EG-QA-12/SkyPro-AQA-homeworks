#!/usr/bin/env python3
"""
Скрипт для проверки доступных пользователей в системе

Показывает список всех пользователей с их логинами и ролями.
"""

import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.user_manager import UserManager


def check_users() -> None:
    """
    Проверяет и выводит список всех доступных пользователей.
    """
    try:
        um = UserManager()
        users = um.get_all_users()
        
        print("Доступные пользователи:")
        print("-" * 40)
        
        for user in users:
            print(f"Login: {user['login']:<15} | Role: {user['role']}")
        
        print("-" * 40)
        print(f"Всего пользователей: {len(users)}")
        
    except Exception as e:
        print(f"Ошибка при получении пользователей: {e}")
        sys.exit(1)


if __name__ == "__main__":
    check_users()
