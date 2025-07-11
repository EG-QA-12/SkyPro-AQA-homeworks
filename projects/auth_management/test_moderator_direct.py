#!/usr/bin/env python3
"""
Прямой запуск теста авторизации через куки для модератора.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.integration.test_cookie_auth import test_cookie_authentication
from src.config import config

def main():
    """Основная функция для запуска теста модератора."""
    
    print("🔐 Прямой запуск теста авторизации через куки")
    print("=" * 60)
    
    # Проверяем доступные файлы кук для модераторов
    data_dir = config.COOKIES_PATH.parent
    moderator_cookies = [
        "EvgenQA_cookies.json",
        "moderator_user_cookies.json", 
        "moderator_cookies.json"
    ]
    
    selected_moderator = None
    for cookie_file in moderator_cookies:
        if (data_dir / cookie_file).exists():
            selected_moderator = cookie_file.replace("_cookies.json", "")
            print(f"✅ Используем модератора: {selected_moderator}")
            print(f"📁 Файл кук: {cookie_file}")
            break
    
    if not selected_moderator:
        print("❌ Не найдены файлы кук для модератора")
        print("💡 Доступные файлы кук:")
        for file in data_dir.glob("*_cookies.json"):
            print(f"   - {file.name}")
        return False
    
    print("="*60)
    
    try:
        # Запускаем тест напрямую с headless=False для визуального контроля
        success = test_cookie_authentication(user_login=selected_moderator, headless=False)
        
        if success:
            print(f"\n🎉 Тест модератора {selected_moderator} завершен успешно!")
            print("✅ Авторизация через куки работает корректно!")
            return True
        else:
            print(f"\n❌ Тест модератора {selected_moderator} провален!")
            print("⚠️ Обнаружены проблемы с авторизацией через куки")
            return False
            
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении теста: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
