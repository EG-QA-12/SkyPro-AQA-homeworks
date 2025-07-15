#!/usr/bin/env python3
"""
Универсальный скрипт для запуска тестов авторизации.

Поддерживает различные режимы для разных сценариев использования:
- CI/CD: быстрые headless тесты только с admin
- Development: полные GUI тесты для отладки
- Production: гибридный подход
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_ci_mode():
    """
    Режим CI/CD - быстрые headless тесты только с admin.
    
    Идеально для пайплайнов - стабильно и быстро.
    """
    print("🚀 Запуск CI/CD режима (headless, только admin)")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/auth/test_single_user_creds_login_and_save_cookie.py",
        "-v", 
        "--tb=short",
        "-x"  # Остановиться на первой ошибке
    ]
    
    # Устанавливаем переменную для режима одного пользователя
    import os
    os.environ["AUTH_MODE"] = "one"
    
    return subprocess.run(cmd).returncode


def run_dev_mode():
    """
    Режим разработки - GUI авторизация для отладки UI.
    
    Видимый браузер, подробный вывод, одиночная авторизация для отладки.
    Для массовой авторизации используйте режим 'api'.
    """
    print("🔬 Запуск режима разработки (GUI, отладка UI)")
    
    cmd = [
        "python", "-m", "pytest", 
        "tests/auth/test_single_user_creds_login_and_save_cookie.py",
        "--headed",
        "-v", "-s",
        "--tb=long"
    ]
    
    return subprocess.run(cmd).returncode


def run_fast_mode():
    """
    Быстрый режим - тестирование авторизации из сохраненных кук.
    
    Проверяет что куки работают (самый быстрый тест).
    """
    print("⚡ Запуск быстрого режима (проверка кук)")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/auth/test_ui_login_and_session_save.py::test_visible_auth_from_saved_cookies", 
        "-v",
        "--tb=short"
    ]
    
    return subprocess.run(cmd).returncode


def run_parallel_mode():
    """
    Параллельный режим - массовая GUI авторизация с 3 потоками.
    
    Максимальная производительность для полного GUI тестирования.
    Для еще большей скорости используйте режим 'api'.
    """
    print("🚄 Запуск параллельного режима (GUI массовая авторизация, 3 потока)")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/auth/test_ui_login_and_session_save.py::test_visible_login_and_save_cookies",
        "--headed",
        "-n", "3", 
        "--dist", "worksteal",
        "-v"
    ]
    
    return subprocess.run(cmd).returncode


def run_stealth_mode():
    """
    Экспериментальный режим - антибот настройки для headless.
    
    Пытается обойти защиту сайта в headless режиме.
    """
    print("🥷 Запуск экспериментального режима (антибот headless)")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/auth/test_ui_login_and_session_save.py::test_stealth_headless_auth",
        "-v", "-s",
        "--tb=short"
    ]
    
    return subprocess.run(cmd).returncode


def run_api_mode():
    """
    Режим API - массовая авторизация через HTTP API.
    
    Самый быстрый и надежный способ без браузера.
    Обходит антибот защиту полностью.
    """
    print("📡 Запуск API режима (HTTP запросы, массовая авторизация)")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/auth/test_api_mass_authorization.py::test_api_mass_authorization",
        "-v", "-s",
        "--tb=short",
        "-m", "api"
    ]
    
    return subprocess.run(cmd).returncode


def run_api_turbo_mode():
    """
    Режим API TURBO - сверхбыстрая авторизация с 10 потоками.
    
    Максимальная производительность для массовой авторизации.
    Использует 10 параллельных потоков для экстремальной скорости.
    """
    print("🚀 Запуск API TURBO режима (HTTP запросы, 10 потоков)")
    
    # Устанавливаем переменную окружения для количества потоков
    import os
    os.environ["API_THREADS"] = "10"
    
    cmd = [
        "python", "-m", "pytest",
        "tests/auth/test_api_mass_authorization.py::test_api_mass_authorization",
        "-v", "-s",
        "--tb=short",
        "-m", "api"
    ]
    
    return subprocess.run(cmd).returncode


def main():
    parser = argparse.ArgumentParser(
        description="Универсальный запуск тестов авторизации",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Режимы запуска:
  ci          - CI/CD режим (headless, только admin, быстро)
  dev         - Отладка UI (GUI, одиночная авторизация, отладка)  
  fast        - Быстрая проверка (тест существующих кук)
  parallel    - GUI массовая авторизация (видимый браузер, 3 потока)
  stealth     - Экспериментальный (антибот headless)
  api         - API авторизация (HTTP запросы, 5 потоков)
  api-turbo   - API TURBO (HTTP запросы, 10 потоков, максимальная скорость)

Примеры:
  python scripts/run_auth_tests.py ci          # Для CI/CD
  python scripts/run_auth_tests.py dev         # Для отладки UI
  python scripts/run_auth_tests.py fast        # Быстрая проверка
  python scripts/run_auth_tests.py parallel    # GUI массовая авторизация
  python scripts/run_auth_tests.py api         # Быстрая массовая авторизация (5 потоков)
  python scripts/run_auth_tests.py api-turbo   # Максимальная скорость (10 потоков)
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["ci", "dev", "fast", "parallel", "stealth", "api", "api-turbo"],
        help="Режим запуска тестов"
    )
    
    args = parser.parse_args()
    
    print(f"📋 Запуск тестов авторизации в режиме: {args.mode}")
    print("="*60)
    
    # Проверяем что мы в правильной директории
    if not Path("tests/auth").exists():
        print("❌ Ошибка: запустите скрипт из корневой директории проекта")
        return 1
    
    # Выбираем функцию по режиму
    mode_functions = {
        "ci": run_ci_mode,
        "dev": run_dev_mode, 
        "fast": run_fast_mode,
        "parallel": run_parallel_mode,
        "stealth": run_stealth_mode,
        "api": run_api_mode,
        "api-turbo": run_api_turbo_mode
    }
    
    try:
        return mode_functions[args.mode]()
    except KeyboardInterrupt:
        print("\n⏹️  Тестирование прервано пользователем")
        return 1
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 