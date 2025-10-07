#!/usr/bin/env python3
"""
Скрипт для массовой замены page.wait_for_timeout(500) на burger_menu.smart_wait_for_page_ready()

Заменяет жесткие ожидания на умные ожидания во всех тестах burger_menu_params.
"""

import os
import re
from pathlib import Path


def migrate_wait_timeout_to_smart(file_path: str) -> bool:
    """
    Заменяет page.wait_for_timeout(500) на burger_menu.smart_wait_for_page_ready()

    Args:
        file_path: Путь к файлу для обработки

    Returns:
        bool: True если файл был изменен
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Заменяем page.wait_for_timeout(500) на burger_menu.smart_wait_for_page_ready()
        # Ищем паттерн с учетом возможных пробелов и комментариев
        pattern = r'(\s+)page\.wait_for_timeout\(500\)(\s*(#.*)?)'
        replacement = r'\1burger_menu.smart_wait_for_page_ready()\2'

        content = re.sub(pattern, replacement, content)

        # Если файл изменился, сохраняем
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Обновлен: {file_path}")
            return True
        else:
            print(f"⏭️  Пропущен (нет изменений): {file_path}")
            return False

    except Exception as e:
        print(f"❌ Ошибка обработки {file_path}: {e}")
        return False


def find_and_migrate_files():
    """Находит и обновляет все тестовые файлы в burger_menu_params"""
    base_path = Path("tests/smoke/burger_menu_params")

    if not base_path.exists():
        print(f"❌ Папка {base_path} не найдена")
        return

    updated_count = 0
    total_count = 0

    # Обрабатываем все .py файлы в подпапках
    for py_file in base_path.rglob("*.py"):
        if py_file.is_file():
            total_count += 1
            if migrate_wait_timeout_to_smart(str(py_file)):
                updated_count += 1

    print(f"\n📊 Результаты миграции:")
    print(f"   Всего файлов: {total_count}")
    print(f"   Обновлено: {updated_count}")
    print(f"   Пропущено: {total_count - updated_count}")


if __name__ == "__main__":
    print("🚀 Начинаем миграцию wait_for_timeout на умные ожидания...")
    find_and_migrate_files()
    print("✅ Миграция завершена!")