#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для очистки базы данных от тестовых пользователей
или полного удаления и пересоздания базы данных.
"""

import argparse
import os
import shutil
import sqlite3
import sys

# Добавляем путь к корню проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from projects.auth_management.config import config
from projects.auth_management.database import DatabaseManager
from projects.auth_management.logger import setup_logger
from projects.auth_management.user_manager import UserManager

logger = setup_logger(__name__)

def delete_test_users(db_manager, pattern=None):
    """Удаляет пользователей с тестовыми именами."""
    try:
        conn = db_manager.conn
        cursor = conn.cursor()
        
        if pattern:
            # Удаление пользователей по шаблону имени
            cursor.execute("SELECT username FROM users WHERE username LIKE ?", (f"%{pattern}%",))
            users = cursor.fetchall()
            if not users:
                logger.info(f"Удаление пользователей с паттерном: {pattern}")
                return 0
                
            count = 0
            for user in users:
                username = user[0]
                db_manager.delete_user(username)
                count += 1
                logger.info(f"Удален пользователь: {username}")
            
            return count
        else:
            # Запрашиваем список пользователей
            cursor.execute("SELECT username FROM users")
            users = cursor.fetchall()
            
            if not users:
                logger.info("Пользователи успешно удалены.")
                return 0
                
            print("Найдены следующие пользователи:")
            for i, user in enumerate(users):
                print(f"{i+1}. {user[0]}")
                
            choice = input("\nВведите номера пользователей для удаления через запятую или 'all' для удаления всех: ")
            
            if choice.lower() == 'all':
                deleted_count = 0
                for user in users:
                    db_manager.delete_user(user[0])
                    logger.info(f"Удален пользователь: {user[0]}")
                    deleted_count += 1
                return deleted_count
            else:
                try:
                    indices = [int(idx.strip()) - 1 for idx in choice.split(',')]
                    deleted_count = 0
                    for idx in indices:
                        if 0 <= idx < len(users):
                            username = users[idx][0]
                            db_manager.delete_user(username)
                            logger.info(f"Удален пользователь: {username}")
                            deleted_count += 1
                        else:
                            logger.warning(f"Недопустимый индекс: {idx+1}")
                    return deleted_count
                except ValueError:
                    logger.error("Неверный формат ввода. Используйте числа, разделенные запятыми.")
                    return 0
    except Exception as e:
        logger.error(f"Ошибка при удалении пользователей: {e}")
        return 0

def print_users(db_manager, role_filter=None):
    """Выводит список пользователей из базы данных
    
    Args:
        db_manager: Экземпляр DatabaseManager
        role_filter: Если указан, выводит только пользователей с этой ролью
    """
    try:
        conn = db_manager.conn
        cursor = conn.cursor()
        
        if role_filter:
            cursor.execute("SELECT username, role FROM users WHERE role=?", (role_filter,))
            title = f"Список пользователей с ролью '{role_filter}':"
        else:
            cursor.execute("SELECT username, role FROM users")
            title = "Список всех пользователей:"
            
        users = cursor.fetchall()
        
        if not users:
            print(f"В базе данных нет пользователей{'' if not role_filter else f' с ролью {role_filter}'}")
            return
            
        print(title)
        print("-" * 30)
        print(f"{'Логин':<20} | {'Роль':<10}")
        print("-" * 30)
        for username, role in users:
            print(f"{username:<20} | {role:<10}")
        print("-" * 30)
        print(f"Всего пользователей: {len(users)}")
        
    except sqlite3.Error as e:
        print(f"Ошибка при получении пользователей: {e}")

def recreate_database():
    """Удаляет и пересоздает базу данных."""
    db_path = os.path.join("user_data", "users.db")
    
    if os.path.exists(db_path):
        # Создаем резервную копию перед удалением
        backup_path = db_path + ".backup"
        shutil.copy2(db_path, backup_path)
        logger.info(f"Создана резервная копия базы данных: {backup_path}")
        
        # Удаляем файл базы данных
        os.remove(db_path)
        logger.info(f"База данных удалена: {db_path}")
        
        # База будет пересоздана при первом обращении к DatabaseManager
        db_manager = DatabaseManager()
        logger.info("База данных успешно пересоздана.")
        
        return True
    else:
        logger.warning(f"Файл базы данных не найден: {db_path}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Утилита для очистки базы данных пользователей")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--delete-pattern', type=str, help='Удалить пользователей по шаблону имени (например, "test" или "user")')
    group.add_argument('--delete-interactive', action='store_true', help='Интерактивный режим удаления пользователей')
    group.add_argument('--recreate-db', action='store_true', help='Полностью удалить и пересоздать базу данных')
    group.add_argument('--print-users', action='store_true', help='Вывести список пользователей')
    group.add_argument('--print-users-role', type=str, help='Вывести список пользователей с указанной ролью')
    
    args = parser.parse_args()
    
    if args.recreate_db:
        if recreate_database():
            print("База данных успешно пересоздана.")
        else:
            print("Не удалось пересоздать базу данных.")
    else:
        db_manager = DatabaseManager()
        
        if args.delete_pattern:
            count = delete_test_users(db_manager, args.delete_pattern)
            print(f"Удалено {count} пользователей с шаблоном '{args.delete_pattern}' в имени.")
        elif args.delete_interactive:
            count = delete_test_users(db_manager)
            print(f"Удалено {count} пользователей.")
        elif args.print_users:
            print_users(db_manager)
        elif args.print_users_role:
            print_users(db_manager, args.print_users_role)

if __name__ == "__main__":
    main()
