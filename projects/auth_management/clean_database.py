#!/usr/bin/env python3
"""
Удобный скрипт для очистки базы данных пользователей.

Использование:
    python clean_database.py --help               # Справка
    python clean_database.py --clear-all          # Полная очистка БД
    python clean_database.py --clear-users        # Удалить пользователей (кроме системных)
    python clean_database.py --clear-cookies      # Очистить только куки
    python clean_database.py --reset-project      # Полный сброс с переинициализацией
"""

import argparse
import os
import sys
from pathlib import Path

# Добавляем путь к корню проекта
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.user_manager import UserManager
from src.database import DatabaseManager
from src.config import config
from src.logger import setup_logger

logger = setup_logger(__name__)


def clear_database():
    """Полностью очищает базу данных."""
    print("🗑️  Полная очистка базы данных...")
    
    # Удаляем файл базы данных
    if config.DB_PATH.exists():
        config.DB_PATH.unlink()
        print(f"✅ База данных удалена: {config.DB_PATH}")
    else:
        print(f"ℹ️  База данных не найдена: {config.DB_PATH}")
    
    # Удаляем файлы куков
    clear_cookie_files()
    
    # Создаем новую пустую базу
    try:
        db = DatabaseManager()
        print("✅ Новая пустая база данных создана")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания новой БД: {e}")
        return False


def clear_users():
    """Удаляет всех пользователей кроме системных."""
    print("🗑️  Удаление пользователей (кроме системных)...")
    
    try:
        user_manager = UserManager()
        all_users = user_manager.get_all_users()
        
        # Системные пользователи, которых НЕ удаляем
        system_users = {'admin', 'moderator', 'expert', 'EvgenQA', 'Xf2gijK8'}
        
        deleted_count = 0
        skipped_count = 0
        
        for user in all_users:
            username = user.get('username') or user.get('login')
            if username and username not in system_users:
                try:
                    user_manager.delete_user(username)
                    print(f"🗑️  Удален: {username}")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Ошибка удаления {username}: {e}")
            else:
                skipped_count += 1
        
        # Очищаем файлы куков
        clear_cookie_files()
        
        print(f"\n✅ Операция завершена:")
        print(f"   Удалено пользователей: {deleted_count}")
        print(f"   Пропущено системных: {skipped_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False


def clear_cookies():
    """Очищает только куки пользователей."""
    print("🍪 Очистка куков пользователей...")
    
    try:
        user_manager = UserManager()
        all_users = user_manager.get_all_users()
        
        cleared_count = 0
        
        for user in all_users:
            user_id = user.get('id')
            username = user.get('username') or user.get('login')
            
            if user_id:
                try:
                    user_manager.clear_user_cookie(user_id)
                    print(f"🗑️  Очищены куки: {username}")
                    cleared_count += 1
                except Exception as e:
                    print(f"❌ Ошибка очистки куков {username}: {e}")
        
        # Удаляем файлы куков
        clear_cookie_files()
        
        print(f"\n✅ Операция завершена:")
        print(f"   Очищено куков пользователей: {cleared_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False


def clear_cookie_files():
    """Удаляет файлы куков из директории data."""
    print("🗑️  Удаление файлов куков...")
    
    data_dir = config.DB_PATH.parent
    cookie_files = list(data_dir.glob("*_cookies.json"))
    
    if cookie_files:
        for cookie_file in cookie_files:
            try:
                cookie_file.unlink()
                print(f"🗑️  Удален файл: {cookie_file.name}")
            except Exception as e:
                print(f"❌ Ошибка удаления {cookie_file.name}: {e}")
        print(f"✅ Удалено файлов куков: {len(cookie_files)}")
    else:
        print("ℹ️  Файлы куков не найдены")


def reset_project():
    """Полный сброс проекта с переинициализацией."""
    print("🔄 Полный сброс проекта...")
    
    # Шаг 1: Очистка БД
    print("\n🗑️  Шаг 1/3: Очистка базы данных...")
    if not clear_database():
        return False
    
    # Шаг 2: Инициализация пользователей
    print("\n🔄 Шаг 2/3: Инициализация пользователей...")
    if config.BULK_CSV_PATH.exists():
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "scripts/init_users.py"
            ], capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                print("✅ Пользователи успешно импортированы")
            else:
                print(f"⚠️  Возможны ошибки при импорте: {result.stderr}")
        except Exception as e:
            print(f"❌ Ошибка запуска init_users.py: {e}")
    else:
        print(f"⚠️  Файл {config.BULK_CSV_PATH} не найден, импорт пропущен")
    
    # Шаг 3: Показываем статистику
    print("\n📊 Шаг 3/3: Проверка результата...")
    try:
        user_manager = UserManager()
        users = user_manager.get_all_users()
        print(f"✅ В базе данных: {len(users)} пользователей")
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
    
    return True


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(
        description="Утилита для очистки базы данных пользователей",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python clean_database.py --clear-all          # Полная очистка БД
  python clean_database.py --clear-users        # Удалить пользователей (кроме системных)
  python clean_database.py --clear-cookies      # Очистить только куки
  python clean_database.py --reset-project      # Полный сброс с переинициализацией
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--clear-all",
        action="store_true",
        help="Полностью очистить базу данных и файлы куков"
    )
    group.add_argument(
        "--clear-users",
        action="store_true",
        help="Удалить всех пользователей кроме системных"
    )
    group.add_argument(
        "--clear-cookies",
        action="store_true", 
        help="Очистить только куки пользователей"
    )
    group.add_argument(
        "--reset-project",
        action="store_true",
        help="Полный сброс проекта с переинициализацией"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  УТИЛИТА ОЧИСТКИ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    success = False
    
    if args.clear_all:
        print("Режим: ПОЛНАЯ ОЧИСТКА")
        print("⚠️  ВНИМАНИЕ: Все данные будут удалены!")
        response = input("\nВведите 'DELETE' для подтверждения: ").strip()
        if response == 'DELETE':
            success = clear_database()
        else:
            print("Операция отменена.")
            return
            
    elif args.clear_users:
        print("Режим: УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЕЙ")
        print("⚠️  Будут удалены все пользователи кроме системных")
        response = input("\nПродолжить? (y/N): ").strip().lower()
        if response in ['y', 'yes', 'да']:
            success = clear_users()
        else:
            print("Операция отменена.")
            return
            
    elif args.clear_cookies:
        print("Режим: ОЧИСТКА КУКОВ")
        success = clear_cookies()
        
    elif args.reset_project:
        print("Режим: ПОЛНЫЙ СБРОС ПРОЕКТА")
        print("⚠️  ВНИМАНИЕ: Все данные будут удалены и переинициализированы!")
        response = input("\nВведите 'RESET' для подтверждения: ").strip()
        if response == 'RESET':
            success = reset_project()
        else:
            print("Операция отменена.")
            return
    
    print("\n" + "=" * 60)
    if success:
        print("  ОПЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        logger.info("Операция очистки завершена успешно")
    else:
        print("  ОПЕРАЦИЯ ЗАВЕРШЕНА С ОШИБКАМИ!")
        print("=" * 60)
        logger.error("Операция очистки завершена с ошибками")
        sys.exit(1)


if __name__ == "__main__":
    main()
