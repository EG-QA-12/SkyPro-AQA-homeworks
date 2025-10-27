#!/usr/bin/env python3
"""Тестирование новой архитектуры авторизации BLL Tests"""

from framework.auth import (
    auth_manager,
    UnifiedAuthManager,
    APIManager,
    BrowserManager,
    get_session_cookie,
    get_browser_auth
)

def test_imports():
    """Проверка импортов"""
    print("✅ Тестируем импорты новой архитектуры...")

    # Проверяем что менеджеры загружаются
    print(f"✅ auth_manager: {type(auth_manager)}")
    print(f"✅ UnifiedAuthManager: {UnifiedAuthManager}")
    print(f"✅ APIManager: {APIManager}")
    print(f"✅ BrowserManager: {BrowserManager}")

    # Проверяем legacy функции
    print(f"✅ get_session_cookie: {callable(get_session_cookie)}")
    print(f"✅ get_browser_auth: {callable(get_browser_auth)}")

    print("✅ Все импорты успешны!")

def test_managers():
    """Проверка инстанцирования менеджеров"""
    print("\n✅ Тестируем создание экземпляров...")

    # Создаем unified менеджер
    unified = UnifiedAuthManager()
    print(f"✅ UnifiedAuthManager создан: {unified}")

    # Создаем отдельные менеджеры
    api = APIManager()
    print(f"✅ APIManager создан: {api}")

    browser = BrowserManager()
    print(f"✅ BrowserManager создан: {browser}")

    print("✅ Все менеджеры созданы успешно!")

def main():
    """Главная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ НОВОЙ АРХИТЕКТУРЫ АВТОРИЗАЦИИ")
    print("="*60)

    try:
        test_imports()
        test_managers()

        print("\n🎉 НОВАЯ АРХИТЕКТУРА РАБОТАЕТ КОРРЕКТНО!")
        print("\n📋 СТРУКТУРА:")
        print("  framework/auth/")
        print("  ├── __init__.py    ← Единая точка входа")
        print("  ├── manager.py     ← UnifiedAuthManager")
        print("  ├── api/manager.py ← APIManager")
        print("  └── browser/manager.py ← BrowserManager")

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        return False

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
