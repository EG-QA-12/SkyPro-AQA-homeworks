#!/usr/bin/env python3
"""
Улучшенный скрипт для запуска тестов авторизации модератора.

Поддерживает различные режимы:
- Прямая авторизация с сохранением кук
- Авторизация через куки
- Валидация прав модератора
"""
import sys
import os
import argparse
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import config
from tests.integration.test_moderator_auth import (
    test_moderator_direct_login,
    test_moderator_cookie_auth,
    validate_moderator_permissions,
)


def find_moderator_cookie_files():
    """
    Находит все файлы кук модераторов в директории проекта.
    
    Returns:
        list: Список файлов кук модераторов.
    """
    data_dir = config.COOKIES_PATH.parent
    
    # Потенциальные шаблоны имен файлов для модераторов
    moderator_patterns = [
        "moderator_cookies.json",
        "moderator_user_cookies.json",
        "EvgenQA_cookies.json",
    ]
    
    # Поиск по шаблонам
    moderator_files = []
    for pattern in moderator_patterns:
        if (data_dir / pattern).exists():
            moderator_files.append(data_dir / pattern)
            
    # Если не нашли по шаблонам, ищем все файлы, содержащие "moderator" в имени
    if not moderator_files:
        for file in data_dir.glob("*cookies.json"):
            if "moderator" in file.name.lower():
                moderator_files.append(file)
                
    # Если не нашли модераторов, попробуем найти куки с настроенными в config модераторами
    if not moderator_files:
        moderator_login_file = data_dir / f"{config.MODERATOR_LOGIN}_cookies.json"
        if moderator_login_file.exists():
            moderator_files.append(moderator_login_file)
                
    return moderator_files


def get_available_moderators():
    """
    Получает список доступных пользователей-модераторов.
    
    Returns:
        list: Список логинов модераторов.
    """
    moderator_files = find_moderator_cookie_files()
    moderators = []
    
    for file in moderator_files:
        user_login = file.stem.replace("_cookies", "")
        moderators.append(user_login)
        
    return moderators


def run_direct_login_test(headless=False):
    """
    Запускает тест прямой авторизации модератора.
    
    Args:
        headless: Запускать браузер в headless режиме.
        
    Returns:
        bool: True если тест успешен.
    """
    print("=" * 60)
    print("🔐 ТЕСТ ПРЯМОЙ АВТОРИЗАЦИИ МОДЕРАТОРА")
    print("=" * 60)
    
    cookies_path = config.COOKIES_PATH.parent / f"{config.MODERATOR_LOGIN}_cookies.json"
    print(f"📝 Будет использован логин модератора: {config.MODERATOR_LOGIN}")
    print(f"💾 Куки будут сохранены в: {cookies_path}")
    print("-" * 60)
    
    result = test_moderator_direct_login(
        cookies_path=cookies_path,
        login_url=config.LOGIN_URL,
        target_url=config.TARGET_URL,
        headless=headless
    )
    
    print("=" * 60)
    if result:
        print("🎉 ТЕСТ ПРЯМОЙ АВТОРИЗАЦИИ УСПЕШЕН!")
    else:
        print("❌ ТЕСТ ПРЯМОЙ АВТОРИЗАЦИИ ПРОВАЛЕН!")
    print("=" * 60)
    
    return result


def run_cookie_auth_test(user_login=None, headless=False):
    """
    Запускает тест авторизации модератора через куки.
    
    Args:
        user_login: Логин пользователя-модератора.
        headless: Запускать браузер в headless режиме.
        
    Returns:
        bool: True если тест успешен.
    """
    print("=" * 60)
    print("🍪 ТЕСТ АВТОРИЗАЦИИ МОДЕРАТОРА ЧЕРЕЗ КУКИ")
    print("=" * 60)
    
    # Если логин не указан, пытаемся найти доступного модератора
    if user_login is None:
        moderators = get_available_moderators()
        if not moderators:
            print("❌ Не найдены файлы кук для модераторов")
            return False
        user_login = moderators[0]
    
    print(f"👤 Выбран модератор: {user_login}")
    print("-" * 60)
    
    result = test_moderator_cookie_auth(user_login=user_login, headless=headless)
    
    print("=" * 60)
    if result:
        print("🎉 ТЕСТ АВТОРИЗАЦИИ ЧЕРЕЗ КУКИ УСПЕШЕН!")
    else:
        print("❌ ТЕСТ АВТОРИЗАЦИИ ЧЕРЕЗ КУКИ ПРОВАЛЕН!")
    print("=" * 60)
    
    return result


def run_validation_test(user_login=None, headless=False):
    """
    Запускает тест валидации прав модератора.
    
    Args:
        user_login: Логин пользователя-модератора.
        headless: Запускать браузер в headless режиме.
        
    Returns:
        bool: True если тест успешен.
    """
    print("=" * 60)
    print("🔍 ТЕСТ ВАЛИДАЦИИ ПРАВ МОДЕРАТОРА")
    print("=" * 60)
    
    # Если логин не указан, пытаемся найти доступного модератора
    if user_login is None:
        moderators = get_available_moderators()
        if not moderators:
            print("❌ Не найдены файлы кук для модераторов")
            return False
        user_login = moderators[0]
    
    print(f"👤 Выбран модератор: {user_login}")
    print("-" * 60)
    
    result = validate_moderator_permissions(user_login=user_login, headless=headless)
    
    print("=" * 60)
    if result:
        print("🎉 ТЕСТ ВАЛИДАЦИИ ПРАВ МОДЕРАТОРА УСПЕШЕН!")
    else:
        print("❌ ТЕСТ ВАЛИДАЦИИ ПРАВ МОДЕРАТОРА ПРОВАЛЕН!")
    print("=" * 60)
    
    return result


def parse_args():
    """
    Разбирает аргументы командной строки.
    
    Returns:
        argparse.Namespace: Разобранные аргументы.
    """
    parser = argparse.ArgumentParser(
        description="Тесты авторизации модератора"
    )
    
    # Добавляем аргументы
    parser.add_argument(
        "--mode", 
        choices=["direct", "cookie", "validate", "all"],
        default="all",
        help="Режим тестирования: direct (прямая авторизация), cookie (через куки), "
             "validate (валидация прав) или all (все тесты)"
    )
    parser.add_argument(
        "--user", 
        help="Логин пользователя-модератора"
    )
    parser.add_argument(
        "--headless", 
        action="store_true",
        help="Запускать браузер в headless режиме"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Показать список доступных модераторов"
    )
    
    return parser.parse_args()


def main():
    """
    Основная функция для запуска тестов модератора.
    
    Returns:
        int: 0 в случае успеха, 1 в случае ошибки.
    """
    args = parse_args()
    
    # Переходим в корневую директорию проекта
    os.chdir(project_root)
    
    # Показываем список доступных модераторов
    if args.list:
        moderators = get_available_moderators()
        print("📋 Доступные модераторы:")
        if moderators:
            for moderator in moderators:
                print(f"  - {moderator}")
        else:
            print("  - Модераторы не найдены")
        return 0
    
    # Выполняем тесты в соответствии с выбранным режимом
    success = True
    
    if args.mode == "direct" or args.mode == "all":
        direct_success = run_direct_login_test(headless=args.headless)
        success = success and direct_success
    
    if args.mode == "cookie" or args.mode == "all":
        cookie_success = run_cookie_auth_test(user_login=args.user, headless=args.headless)
        success = success and cookie_success
    
    if args.mode == "validate" or args.mode == "all":
        validate_success = run_validation_test(user_login=args.user, headless=args.headless)
        success = success and validate_success
    
    # Выводим итоговый результат
    print("\n" + "=" * 60)
    if success:
        print("🎉 ВСЕ ТЕСТЫ АВТОРИЗАЦИИ МОДЕРАТОРА УСПЕШНЫ!")
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ АВТОРИЗАЦИИ МОДЕРАТОРА ПРОВАЛЕНЫ!")
    print("=" * 60)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
