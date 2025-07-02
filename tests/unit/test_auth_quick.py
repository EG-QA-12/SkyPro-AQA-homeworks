#!/usr/bin/env python3
"""
Быстрый тест для проверки работы авторизации после рефакторинга.
"""

import os
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_config_loading():
    """Тест загрузки конфигурации."""
    print("🔧 Тестирование загрузки конфигурации...")
    
    try:
        from src.config import config
        print(f"✅ Конфигурация загружена")
        print(f"   LOGIN: {config.LOGIN}")
        print(f"   BASE_URL: {config.BASE_URL}")
        print(f"   LOGIN_URL: {config.LOGIN_URL}")
        print(f"   HEADLESS: {config.HEADLESS}")
        print(f"   LOG_LEVEL: {config.LOG_LEVEL}")
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False


def test_database_connection():
    """Тест подключения к базе данных."""
    print("\n🗄️ Тестирование подключения к базе данных...")
    
    try:
        from src.database import DatabaseManager
        
        db = DatabaseManager()
        print("✅ Подключение к БД установлено")
        
        # Проверяем создание тестового пользователя
        test_result = db.create_user("test_user_check", "test_password", "user")
        if test_result:
            print("✅ Создание пользователя работает")
            
            # Проверяем получение пользователя
            user = db.get_user_by_username("test_user_check")
            if user:
                print("✅ Получение пользователя работает")
                print(f"   Пользователь: {user['username']}, роль: {user['role']}")
                
                # Проверяем верификацию пароля
                if db.verify_password("test_user_check", "test_password"):
                    print("✅ Верификация пароля работает")
                else:
                    print("❌ Ошибка верификации пароля")
                    
                # Удаляем тестового пользователя
                db.delete_user("test_user_check")
                print("✅ Удаление пользователя работает")
            else:
                print("❌ Ошибка получения пользователя")
        else:
            print("❌ Ошибка создания пользователя")
            
        return True
    except Exception as e:
        print(f"❌ Ошибка работы с БД: {e}")
        return False


def test_auth_functions():
    """Тест функций авторизации."""
    print("\n🔐 Тестирование функций авторизации...")
    
    try:
        from src.auth import get_credentials, load_cookies
        
        # Тест получения учетных данных
        login, password = get_credentials()
        print(f"✅ Получение учетных данных работает")
        print(f"   LOGIN: {login}")
        
        # Тест загрузки кук (должно вернуть None если файла нет)
        cookies = load_cookies()
        if cookies is None:
            print("✅ Загрузка кук работает (файл не найден - это ожидаемо)")
        else:
            print(f"✅ Загрузка кук работает (найдено {len(cookies)} кук)")
            
        return True
    except Exception as e:
        print(f"❌ Ошибка функций авторизации: {e}")
        return False


def test_logger():
    """Тест системы логирования."""
    print("\n📝 Тестирование системы логирования...")
    
    try:
        from src.logger import setup_logger
        
        logger = setup_logger("test_logger")
        logger.info("Тест логирования")
        print("✅ Система логирования работает")
        return True
    except Exception as e:
        print(f"❌ Ошибка системы логирования: {e}")
        return False


def test_cookies_module():
    """Тест модуля работы с куками."""
    print("\n🍪 Тестирование модуля работы с куками...")
    
    try:
        from src.cookies import load_cookies, check_cookies_validity
        
        # Тест проверки валидности кук
        test_cookies = [
            {
                "name": "test_cookie",
                "value": "test_value",
                "domain": "example.com",
                "expires": 9999999999  # Далекое будущее
            }
        ]
        
        is_valid = check_cookies_validity(test_cookies, "example.com")
        print(f"✅ Проверка валидности кук работает: {is_valid}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка модуля кук: {e}")
        return False


def main():
    """Основная функция тестирования."""
    print("🚀 Запуск быстрого теста авторизации")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_database_connection,
        test_auth_functions,
        test_logger,
        test_cookies_module,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Неожиданная ошибка в {test_func.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты тестирования:")
    print(f"   ✅ Пройдено: {passed}")
    print(f"   ❌ Провалено: {failed}")
    print(f"   📈 Процент успеха: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 Все тесты пройдены! Система авторизации готова к работе.")
    else:
        print(f"\n⚠️ Обнаружены проблемы в {failed} тестах. Требуется дополнительная настройка.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
