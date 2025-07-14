#!/usr/bin/env python3
"""
Упрощенный запуск теста массовой авторизации из CSV в GUI-режиме.

Этот скрипт позволяет легко запустить тест, который:
- Читает пользователей из CSV-файла
- Авторизует их в видимом браузере с замедленными действиями
- Сохраняет куки в соответствующие папки

Использование:
    python scripts/maintenance/run_csv_auth_gui.py
    python scripts/maintenance/run_csv_auth_gui.py --slow 2000
    python scripts/maintenance/run_csv_auth_gui.py --browser firefox
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def setup_environment() -> None:
    """Настраивает окружение для корректного запуска теста."""
    project_root = Path(__file__).parent.parent.parent
    os.environ["PYTHONPATH"] = str(project_root)
    os.chdir(project_root)


def run_csv_auth_test(slowmo: int = 1500, browser: str = "chromium", verbose: bool = True) -> int:
    """
    Запускает тест массовой авторизации из CSV в GUI-режиме.
    
    Args:
        slowmo: Замедление действий в миллисекундах (по умолчанию 1500)
        browser: Браузер для запуска (chromium, firefox, webkit)
        verbose: Подробный вывод
        
    Returns:
        Код завершения pytest
    """
    # Определяем путь к тесту
    test_path = "tests/auth/test_ui_login_and_session_save.py::test_visible_login_and_save_cookies"
    
    # Формируем команду pytest
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "--headed",
        f"--browser={browser}",
        f"--slowmo={slowmo}",
        "-s"  # Показывать print-ы
    ]
    
    if verbose:
        cmd.append("-v")
    
    print("🎯 Запуск массовой авторизации из CSV в GUI-режиме")
    print("=" * 60)
    print(f"📱 Браузер: {browser}")
    print(f"⏰ Замедление: {slowmo}ms")
    print(f"📂 Тест: {test_path}")
    print("=" * 60)
    print()
    
    # Запускаем команду
    result = subprocess.run(cmd)
    
    print()
    if result.returncode == 0:
        print("✅ Массовая авторизация завершена успешно!")
    else:
        print("❌ Произошли ошибки во время авторизации")
    
    return result.returncode


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(
        description="Запуск массовой авторизации из CSV в GUI-режиме",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python scripts/maintenance/run_csv_auth_gui.py
  python scripts/maintenance/run_csv_auth_gui.py --slow 2000
  python scripts/maintenance/run_csv_auth_gui.py --browser firefox --slow 1000
  python scripts/maintenance/run_csv_auth_gui.py --quiet
        """
    )
    
    parser.add_argument(
        "--slow", "--slowmo",
        type=int,
        default=1500,
        help="Замедление действий в миллисекундах (по умолчанию: 1500)"
    )
    
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="Браузер для запуска (по умолчанию: chromium)"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Менее подробный вывод"
    )
    
    args = parser.parse_args()
    
    # Настраиваем окружение
    setup_environment()
    
    # Запускаем тест
    exit_code = run_csv_auth_test(
        slowmo=args.slow,
        browser=args.browser,
        verbose=not args.quiet
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 