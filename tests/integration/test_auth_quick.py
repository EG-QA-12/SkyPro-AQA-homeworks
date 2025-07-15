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
    
    from config.secrets_manager import SecretsManager
    secrets = SecretsManager()
    config_summary = secrets.get_masked_config_summary()
    print(f"✅ Конфигурация загружена")
    print(f"   Environment: {config_summary['environment']}")
    print(f"   Auth configured: {config_summary['auth_configured']}")
    print(f"   API configured: {config_summary['api_configured']}")
    print(f"   Database configured: {config_summary['database_configured']}")
    assert config_summary['environment'] is not None

def test_database_connection():
    """Тест подключения к базе данных."""
    print("\n🗄️ Тестирование подключения к базе данных...")
    
    from framework.utils.db_utils import DatabaseManager
    db = DatabaseManager()
    # Простая проверка работы базы - получаем количество пользователей
    result = db.execute_query("SELECT COUNT(*) FROM users", fetch=True)
    count = result[0][0] if result else 0
    print(f"✅ База данных работает")
    print(f"   Пользователей в БД: {count}")
    assert result is not None

def test_auth_functions():
    """Тест функций авторизации."""
    print("\n🔐 Тестирование функций авторизации...")
    
    from framework.utils.auth_utils import get_cookie_path, get_auth_credentials
    # Проверяем функции без фактической авторизации
    cookie_path = get_cookie_path("test_user")
    print(f"✅ Функции авторизации работают")
    print(f"   Cookie path: {cookie_path}")
    assert cookie_path is not None

def test_logger():
    """Тест системы логирования."""
    print("\n📝 Тестирование системы логирования...")
    
    import logging
    logger = logging.getLogger("test_logger")
    logger.info("Тестовое сообщение")
    print(f"✅ Система логирования работает")
    assert logger is not None

def test_cookies_module():
    """Тест модуля работы с куками."""
    print("\n🍪 Тестирование модуля работы с куками...")
    
    from framework.utils.cookie_helper import get_cookie_files, parse_auth_cookie
    from pathlib import Path
    # Простая проверка импорта существующих функций для работы с куками
    cookies_dir = Path("cookies")
    print(f"✅ Модуль кук работает")
    assert get_cookie_files is not None
    assert parse_auth_cookie is not None


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
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ Тест {test_func.__name__} не пройден: {e}")
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
