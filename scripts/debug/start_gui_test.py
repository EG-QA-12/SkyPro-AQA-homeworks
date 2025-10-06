#!/usr/bin/env python3
"""Скрипт для запуска GUI тестов с visible браузером."""


import os
import subprocess


# Устанавливаем переменные окружения
os.environ['BROWSER_HEADLESS'] = 'false'


def run_gui_test():
    """Запуск GUI теста с видимым браузером для всех доменов."""
    print("🚀 Запуск GUI тестов с visible браузерами для всех доменов...")

    cmd = [
        "pytest",
        "-n 2",  # 2 параллельных потока для GUI
        "-v",
        "--headed",  # Явно visible
        "--slow-mo=500",  # Замедляем действия чтобы увидеть
        ("tests/smoke/burger_menu_params/left_column/"
         "test_ask_question_navigation.py")  # Весь файл для всех доменов
    ]

    print(f"Выполняем: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, cwd="D:\\Bll_tests")
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n🛑 Тест остановлен пользователем")
        return False


if __name__ == "__main__":
    success = run_gui_test()
    message = ("\n✅ GUI тест активирован!" if success
               else "\n❌ Тест завершился с ошибками")
    print(message)
    input("Нажми Enter для выхода...")
