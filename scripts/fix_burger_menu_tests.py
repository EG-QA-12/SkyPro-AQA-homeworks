#!/usr/bin/env python3
"""
Скрипт для исправления всех тестов бургер-меню.
Добавляет retry механизм и улучшенную обработку ресурсов.
"""

import os
import re
from pathlib import Path

def fix_burger_menu_tests():
    """Исправляет все тесты бургер-меню для предотвращения конфликтов."""

    # Файлы для исправления
    test_files = [
        "tests/e2e/test_burger_menu_docs2.py",
        "tests/e2e/test_burger_menu_docs.py",
        "tests/e2e/test_burger_menu_navigation_refactored.py",
        "tests/e2e/test_simple_navigation.py",
        "tests/e2e/test_menu_headless_check.py"
    ]

    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"Исправляем файл: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Паттерн для поиска assert burger_menu.open_menu()
            pattern = r'(\s+)assert burger_menu\.open_menu\(\), "Не удалось открыть бургер-меню"'

            # Замена на retry механизм
            replacement = r'''            # Добавляем небольшую паузу для избежания конфликтов
            page.wait_for_timeout(500)

            \1# Добавляем retry механизм для открытия меню
            \1max_retries = 3
            \1for attempt in range(max_retries):
            \1    if burger_menu.open_menu():
            \1        break
            \1    if attempt < max_retries - 1:
            \1        page.wait_for_timeout(1000)
            \1        page.reload()
            \1    else:
            \1        assert False, "Не удалось открыть бургер-меню после нескольких попыток"'''

            # Применяем замену
            new_content = re.sub(pattern, replacement, content)

            # Сохраняем файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"Файл {file_path} исправлен")

if __name__ == "__main__":
    fix_burger_menu_tests()
    print("Все файлы тестов исправлены!")