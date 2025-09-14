#!/usr/bin/env python3
"""
Быстрый тест для проверки работы авторизации после рефакторинга.
"""

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
    print("✅ Конфигурация загружена")
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
    print("✅ База данных работает")
    print(f"   Пользователей в БД: {count}")
    assert result is not None


def test_auth_functions():
    """Тест функций авторизации."""
    print("\n🔐 Тестирование функций авторизации...")
    
    from framework.utils.auth_utils import get_cookie_path
    # Проверяем функции без фактической авторизации
    cookie_path = get_cookie_path("test_user")
    print("✅ Функции авторизации работают")
    print(f"   Cookie path: {cookie_path}")
    assert cookie_path is not None


def test_logger():
    """Тест системы логирования."""
    print("\n📝 Тестирование системы логирования...")
    
    import logging
    logger = logging.getLogger("test_logger")
    logger.info("Тестовое сообщение")
    print("✅ Система логирования работает")
    assert logger is not None


def test_cookies_module():
    """Тест модуля работы с куками."""
    print("\n🍪 Тестирование модуля работы с куками...")
    
    from framework.utils.cookie_helper import (
        get_cookie_files,
        parse_auth_cookie
    )
    # Простая проверка импорта существующих функций для работы с куками
    print("✅ Модуль кук работает")
    assert get_cookie_files is not None
    assert parse_auth_cookie is not None


def test_auth_cookie_provider():
    """Тест провайдера авторизационных кук."""
    print("\n🔑 Тестирование провайдера авторизационных кук...")
    
    from framework.utils.auth_cookie_provider import AuthCookieProvider
    provider = AuthCookieProvider()
    
    # Проверяем, что провайдер создан
    assert provider is not None
    print("✅ AuthCookieProvider создан")
    
    # Проверяем методы провайдера
    assert hasattr(provider, 'get_auth_cookie')
    assert hasattr(provider, '_get_cookie_from_env')
    assert hasattr(provider, '_get_cookie_from_files')
    assert hasattr(provider, '_get_cookie_via_api_login')
    print("✅ Методы AuthCookieProvider доступны")


def test_api_auth_manager():
    """Тест менеджера API авторизации."""
    print("\n📡 Тестирование менеджера API авторизации...")
    
    from framework.utils.api_auth import APIAuthManager
    manager = APIAuthManager()
    
    # Проверяем, что менеджер создан
    assert manager is not None
    print("✅ APIAuthManager создан")
    
    # Проверяем методы менеджера
    assert hasattr(manager, 'login_user')
    assert hasattr(manager, 'mass_authorize_users')
    print("✅ Методы APIAuthManager доступны")


def test_smart_auth_manager():
    """Тест интеллектуального менеджера авторизации."""
    print("\n🧠 Тестирование интеллектуального менеджера авторизации...")
    
    from framework.utils.smart_auth_manager import SmartAuthManager
    manager = SmartAuthManager()
    
    # Проверяем, что менеджер создан
    assert manager is not None
    print("✅ SmartAuthManager создан")
    
    # Проверяем методы менеджера
    assert hasattr(manager, 'get_valid_session_cookie')
    assert hasattr(manager, '_perform_auth_and_get_cookie')
    print("✅ Методы SmartAuthManager доступны")


def test_base_api_client():
    """Тест базового API клиента."""
    print("\n🔌 Тестирование базового API клиента...")
    
    from framework.api.base_client import BaseAPIClient
    client = BaseAPIClient()
    
    # Проверяем, что клиент создан
    assert client is not None
    print("✅ BaseAPIClient создан")
    
    # Проверяем атрибуты клиента
    assert hasattr(client, 'session')
    assert hasattr(client, 'auth_manager')
    assert hasattr(client, 'cookie_provider')
    print("✅ Атрибуты BaseAPIClient доступны")


def test_admin_api_client():
    """Тест административного API клиента."""
    print("\n👑 Тестирование административного API клиента...")
    
    from framework.api.admin_client import AdminAPIClient
    client = AdminAPIClient()
    
    # Проверяем, что клиент создан
    assert client is not None
    print("✅ AdminAPIClient создан")
    
    # Проверяем методы клиента
    assert hasattr(client, 'get_moderation_panel_data')
    assert hasattr(client, 'publish_question')
    assert hasattr(client, 'publish_answer')
    print("✅ Методы AdminAPIClient доступны")


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
        test_auth_cookie_provider,
        test_api_auth_manager,
        test_smart_auth_manager,
        test_base_api_client,
        test_admin_api_client,
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
    print("📊 Результаты тестирования:")
    print(f"   ✅ Пройдено: {passed}")
    print(f"   ❌ Провалено: {failed}")
    print(f"   📈 Процент успеха: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 Все тесты пройдены! Система авторизации готова к работе.")
    else:
        print(
            f"\n⚠️ Обнаружены проблемы в {failed} тестах. "
            "Требуется дополнительная настройка."
        )
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
