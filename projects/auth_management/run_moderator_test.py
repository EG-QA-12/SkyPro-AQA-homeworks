#!/usr/bin/env python3
"""
Скрипт для запуска теста авторизации через куки для модератора.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_moderator_cookie_test():
    """Запускает тест авторизации через куки для модератора."""
    
    # Переходим в корневую директорию проекта
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🔐 Запуск теста авторизации через куки для модератора")
    print("=" * 60)
    
    # Проверяем доступные файлы кук для модераторов
    data_dir = project_root / "data"
    moderator_cookies = [
        "EvgenQA_cookies.json",
        "moderator_user_cookies.json",
        "moderator_cookies.json"
    ]
    
    available_moderator = None
    for cookie_file in moderator_cookies:
        if (data_dir / cookie_file).exists():
            available_moderator = cookie_file.replace("_cookies.json", "")
            print(f"✅ Найдены куки модератора: {cookie_file}")
            break
    
    if not available_moderator:
        print("❌ Не найдены файлы кук для модератора")
        print("💡 Доступные файлы кук:")
        for file in data_dir.glob("*cookies.json"):
            print(f"   - {file.name}")
        return False
    
    # Команда для запуска pytest с указанием конкретного пользователя
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/test_cookie_auth.py::test_cookie_authentication",
        "-v", "-s",  # verbose и показать print'ы
        f"--user-login={available_moderator}",
        "--tb=short"  # короткий traceback
    ]
    
    print(f"🚀 Запускаем команду: {' '.join(cmd)}")
    print(f"👤 Пользователь: {available_moderator}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ошибка при запуске теста: {e}")
        return False

if __name__ == "__main__":
    success = run_moderator_cookie_test()
    if success:
        print("\n🎉 Тест модератора завершен успешно!")
    else:
        print("\n❌ Тест модератора завершен с ошибками!")
    sys.exit(0 if success else 1)
