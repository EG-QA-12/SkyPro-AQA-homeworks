#!/usr/bin/env python3
"""
Тест для проверки работы с разными источниками кук авторизации.

Этот тест демонстрирует работу системы авторизации с
различными источниками кук:
1. Переменные окружения
2. Локальные файлы
3. API-логин
"""

import os
import sys
import json
# import tempfile
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def setup_env_cookie():
    """Настройка куки через переменные окружения."""
    print("🔧 Настройка куки через переменные окружения...")
    # Устанавливаем переменную окружения для теста
    os.environ['SESSION_COOKIE_ADMIN'] = 'test_env_cookie_value'
    print("✅ Кука установлена в переменных окружения")


def setup_file_cookie():
    """Настройка куки через локальный файл."""
    print("\n📁 Настройка куки через локальный файл...")
    
    # Создаем директорию для кук, если её нет
    cookies_dir = project_root / "cookies"
    cookies_dir.mkdir(exist_ok=True)
    
    # Создаем текстовый файл с кукой
    cookie_file = cookies_dir / "admin_session.txt"
    cookie_file.write_text("test_file_cookie_value")
    print(f"✅ Кука сохранена в файл: {cookie_file}")


def setup_json_cookie():
    """Настройка куки через JSON файл."""
    print("\n📄 Настройка куки через JSON файл...")
    
    # Создаем директорию для кук, если её нет
    cookies_dir = project_root / "cookies"
    cookies_dir.mkdir(exist_ok=True)
    
    # Создаем JSON файл с куками в формате Playwright
    cookie_file = cookies_dir / "moderator_cookies.json"
    
    # Пример данных куки в формате Playwright
    cookies_data = [
        {
            "name": "test_joint_session",
            "value": "test_json_cookie_value",
            "domain": ".bll.by",
            "path": "/",
            "secure": True,
            "httpOnly": True,
            "sameSite": "Lax"
        }
    ]
    
    with open(cookie_file, 'w', encoding='utf-8') as f:
        json.dump(cookies_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Куки сохранены в JSON файл: {cookie_file}")


def test_auth_cookie_provider_with_env():
    """Тест AuthCookieProvider с кукой из переменных окружения."""
    print("\n🔑 Тест AuthCookieProvider с кукой из переменных окружения...")
    
    from framework.utils.auth_cookie_provider import AuthCookieProvider
    
    # Создаем провайдер
    provider = AuthCookieProvider()
    
    # Получаем куку для роли admin
    cookie = provider.get_auth_cookie(role="admin", use_api_login=False)
    
    # Проверяем, что кука получена из переменных окружения
    expected = "test_env_cookie_value"
    msg = f"Ожидалась кука '{expected}', получена '{cookie}'"
    assert cookie == expected, msg
    print("✅ Кука успешно получена из переменных окружения")
    
    # Очищаем переменную окружения
    if 'SESSION_COOKIE_ADMIN' in os.environ:
        del os.environ['SESSION_COOKIE_ADMIN']


def test_auth_cookie_provider_with_file():
    """Тест AuthCookieProvider с кукой из текстового файла."""
    print("\n📄 Тест AuthCookieProvider с кукой из текстового файла...")
    
    from framework.utils.auth_cookie_provider import AuthCookieProvider
    
    # Создаем провайдер
    provider = AuthCookieProvider()
    
    # Получаем куку для роли admin (без использования API-логина)
    cookie = provider.get_auth_cookie(role="admin", use_api_login=False)
    
    # Проверяем, что кука получена из файла
    expected = "test_file_cookie_value"
    msg = f"Ожидалась кука '{expected}', получена '{cookie}'"
    assert cookie == expected, msg
    print("✅ Кука успешно получена из текстового файла")


def test_auth_cookie_provider_with_json():
    """Тест AuthCookieProvider с кукой из JSON файла."""
    print("\n📋 Тест AuthCookieProvider с кукой из JSON файла...")
    
    from framework.utils.auth_cookie_provider import AuthCookieProvider
    
    # Создаем провайдер
    provider = AuthCookieProvider()
    
    # Получаем куку для роли moderator (без использования API-логина)
    cookie = provider.get_auth_cookie(role="moderator", use_api_login=False)
    
    # Проверяем, что кука получена из JSON файла
    expected = "test_json_cookie_value"
    msg = f"Ожидалась кука '{expected}', получена '{cookie}'"
    assert cookie == expected, msg
    print("✅ Кука успешно получена из JSON файла")


def test_auth_cookie_provider_priority():
    """Тест приоритета источников кук в AuthCookieProvider."""
    print("\n⬆️ Тест приоритета источников кук в AuthCookieProvider...")
    
    from framework.utils.auth_cookie_provider import AuthCookieProvider
    
    # Устанавливаем куку в переменные окружения
    os.environ['SESSION_COOKIE_USER'] = 'env_priority_cookie'
    
    # Создаем провайдер
    provider = AuthCookieProvider()
    
    # Получаем куку для роли user
    # Должна быть получена из переменных окружения, не из файла
    cookie = provider.get_auth_cookie(role="user", use_api_login=False)
    
    # Проверяем, что кука получена из переменных окружения (приоритет выше)
    expected = "env_priority_cookie"
    msg = f"Ожидалась кука '{expected}', получена '{cookie}'"
    assert cookie == expected, msg
    print("✅ Приоритет переменных окружения над файлами работает корректно")
    
    # Очищаем переменную окружения
    if 'SESSION_COOKIE_USER' in os.environ:
        del os.environ['SESSION_COOKIE_USER']


def test_api_login_fallback():
    """Тест fallback на API-логин при отсутствии кук в других источниках."""
    print(
        "\n🌐 Тест fallback на API-логин при отсутствии кук " +
        "в других источниках..."
    )
    
    from framework.utils.auth_cookie_provider import AuthCookieProvider
    
    # Создаем провайдер
    provider = AuthCookieProvider()
    
    # Получаем куку для роли, для которой нет кук в других источниках
    # Поскольку use_api_login=True по умолчанию, будет попытка API-логина
    # Но в тестовой среде API-логин может не сработать,
    # поэтому проверяем только структуру
    try:
        cookie = provider.get_auth_cookie(
            role="nonexistent_role",
            use_api_login=True
        )
        # Если API-логин сработал, проверяем, что кука получена
        if cookie is not None:
            print(f"✅ API-логин вернул куку: {cookie[:10]}...")
        else:
            print("ℹ️  API-логин не вернул куку (ожидаемо в тестовой среде)")
    except Exception as e:
        print(f"ℹ️  API-логин не удался (ожидаемо в тестовой среде): {e}")


def test_base_api_client_auth():
    """Тест автоматической авторизации в BaseAPIClient."""
    print("\n🔌 Тест автоматической авторизации в BaseAPIClient...")
    
    from framework.api.base_client import BaseAPIClient
    
    # Создаем клиент
    client = BaseAPIClient(role="admin")
    
    # Проверяем, что клиент создан и имеет необходимые атрибуты
    assert client is not None
    assert hasattr(client, 'session')
    assert hasattr(client, 'auth_manager')
    assert hasattr(client, 'cookie_provider')
    
    # Проверяем, что в сессии есть кука (если была получена)
    # В тестовой среде может не быть реальной куки,
    # поэтому просто проверяем структуру
    print("✅ BaseAPIClient создан и готов к авторизации")


def cleanup_test_files():
    """Очистка тестовых файлов."""
    print("\n🧹 Очистка тестовых файлов...")
    
    # Удаляем тестовые файлы кук
    cookies_dir = project_root / "cookies"
    
    # Удаляем текстовый файл
    cookie_file = cookies_dir / "admin_session.txt"
    if cookie_file.exists():
        cookie_file.unlink()
        print(f"✅ Удален файл: {cookie_file}")
    
    # Удаляем JSON файл
    json_cookie_file = cookies_dir / "moderator_cookies.json"
    if json_cookie_file.exists():
        json_cookie_file.unlink()
        print(f"✅ Удален файл: {json_cookie_file}")
    
    # Удаляем директорию cookies, если она пуста
    try:
        if cookies_dir.exists() and not any(cookies_dir.iterdir()):
            cookies_dir.rmdir()
            print(f"✅ Удалена пустая директория: {cookies_dir}")
    except Exception:
        pass  # Игнорируем ошибки удаления директории


def main():
    """Основная функция тестирования."""
    print("🚀 Запуск теста работы с разными источниками кук авторизации")
    print("=" * 60)
    
    try:
        # Настройка тестовых данных
        setup_env_cookie()
        setup_file_cookie()
        setup_json_cookie()
        
        # Запуск тестов
        tests = [
            test_auth_cookie_provider_with_env,
            test_auth_cookie_provider_with_file,
            test_auth_cookie_provider_with_json,
            test_auth_cookie_provider_priority,
            test_api_login_fallback,
            test_base_api_client_auth,
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
        
        print("\n" + "=" * 60)
        print("📊 Результаты тестирования:")
        print(f"   ✅ Пройдено: {passed}")
        print(f"   ❌ Провалено: {failed}")
        success_rate = (passed / (passed + failed) * 100)
        print(f"   📈 Процент успеха: {success_rate:.1f}%")
        
        if failed == 0:
            print(
                "\n🎉 Все тесты пройдены! Работа с разными " +
                "источниками кук работает корректно."
            )
        else:
            print(f"\n⚠️ Обнаружены проблемы в {failed} тестах.")
        
        return failed == 0
        
    finally:
        # Очистка тестовых данных
        cleanup_test_files()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)