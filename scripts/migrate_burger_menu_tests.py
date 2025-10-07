#!/usr/bin/env python3
"""
Скрипт для массового обновления тестов burger_menu_params.

Заменяет ручную авторизацию через SmartAuthManager на использование
домен-зависимой фикстуры domain_aware_authenticated_context.
"""

import os
import re
from pathlib import Path


def update_test_file(file_path: Path) -> bool:
    """
    Обновляет один тестовый файл для использования domain_aware_authenticated_context.

    Args:
        file_path: Путь к тестовому файлу

    Returns:
        bool: True если файл был обновлен
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Шаблоны для замены
        patterns = [
            # Удаляем импорт SmartAuthManager если он есть
            (r'from framework\.utils\.smart_auth_manager import SmartAuthManager\n', ''),

            # Удаляем импорт requests если он есть (используется только для проверки URL)
            (r'import requests\n', ''),

            # Удаляем фикстуру fx_auth_manager
            (r'@pytest\.fixture\n\s*def fx_auth_manager\(\):\n\s*"""Инициализация умного менеджера авторизации"""\n\s*return SmartAuthManager\(\)\n\n', ''),

            # Заменяем параметры тестового метода
            (r'def test_\w+\(self, multi_domain_context, browser, fx_auth_manager\):',
             lambda m: m.group(0).replace(', browser, fx_auth_manager', ', domain_aware_authenticated_context')),

            # Удаляем создание контекста браузера
            (r'\s*# SSO-aware domain-specific browser settings\n\s*context = browser\.new_context\(\n\s*user_agent="Mozilla/5\.0 \(Windows NT 10\.0; Win64; x64\) AppleWebKit/537\.36 \(KHTML, like Gecko\) Chrome/120\.0\.0\.0 Safari/537\.36",\n\s*viewport=\{"width": 1920, "height": 1080\},\n\s*ignore_https_errors=True\n\s*\)\n\n\s*if domain_name in \[\'ca\', \'bonus\', \'cp\'\]:\n\s*context\.set_default_timeout\(30000\)\n\s*else:\n\s*context\.set_default_timeout\(25000\)\n\n\s*# Используем SmartAuthManager для умной авторизации\n\s*cookie_info = fx_auth_manager\.get_valid_session_cookie\(role="admin"\)\n\s*assert cookie_info, "Не удалось получить валидную куку через SmartAuthManager"\n\n\s*# Устанавливаем полную информацию о куке \(name, value, domain, sameSite\)\n\s*context\.add_cookies\(\[cookie_info\]\)\n\n\s*# БЕЗОПАСНАЯ ДИАГНОСТИКА: НЕ РАСКРЫВАЕМ ПОЛНУЮ КУКУ!\s*\n\s*print\(f"✅ Кука получена: \{cookie_info\[\'name\'\]\} \(длина значения: \{len\(cookie_info\[\'value\'\]\)} символов\)"\)\n\n\s*', '        # Используем домен-зависимую авторизацию\n'),

            # Заменяем создание страницы
            (r'page = context\.new_page\(\)', 'page = domain_aware_authenticated_context.new_page()'),

            # Удаляем finally блок с закрытием контекста
            (r'\s*finally:\n\s*page\.close\(\)\n\s*context\.close\(\)', '        finally:\n            page.close()'),
        ]

        # Применяем все паттерны
        for pattern, replacement in patterns:
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                content = re.sub(pattern, replacement, content)

        # Дополнительная очистка - удаляем оставшиеся старые переменные
        # Удаляем строки с browser.new_context и последующие блоки авторизации
        content = re.sub(
            r'\s*# SSO-aware domain-specific browser settings\n\s*context = browser\.new_context\(\n.*?\n\s*\)\n\n\s*if domain_name in \[.*?\]:\n\s*context\.set_default_timeout\(\d+\)\n\s*else:\n\s*context\.set_default_timeout\(\d+\)\n\n\s*# Используем SmartAuthManager для умной авторизации\n\s*cookie_info = fx_auth_manager\.get_valid_session_cookie\(role="admin"\)\n\s*assert cookie_info.*?\n\n\s*# Устанавливаем полную информацию о куке.*?\n\s*context\.add_cookies\(\[cookie_info\]\)\n\s*# БЕЗОПАСНАЯ ДИАГНОСТИКА.*?\n\s*print\(.*?\)\n\n\s*',
            '        # Используем домен-зависимую авторизацию\n',
            content,
            flags=re.DOTALL
        )

        # Удаляем пустые строки после импортов
        content = re.sub(r'(\n\s*\n){3,}', '\n\n', content)

        # Если контент изменился, сохраняем файл
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Обновлен: {file_path}")
            return True
        else:
            print(f"⚪ Без изменений: {file_path}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при обработке {file_path}: {e}")
        return False


def main():
    """Основная функция скрипта."""
    print("🚀 Начинаем массовое обновление тестов burger_menu_params...")

    # Пути к директориям с тестами
    test_dirs = [
        Path("tests/smoke/burger_menu_params/left_column"),
        Path("tests/smoke/burger_menu_params/right_column")
    ]

    total_files = 0
    updated_files = 0

    for test_dir in test_dirs:
        if not test_dir.exists():
            print(f"⚠️ Директория не найдена: {test_dir}")
            continue

        print(f"\n📁 Обрабатываем директорию: {test_dir}")

        # Находим все тестовые файлы
        test_files = list(test_dir.glob("test_*.py"))

        for test_file in test_files:
            total_files += 1
            if update_test_file(test_file):
                updated_files += 1

    print("\n📊 Результаты:")
    print(f"   Всего файлов: {total_files}")
    print(f"   Обновлено: {updated_files}")
    print(f"   Без изменений: {total_files - updated_files}")

    if updated_files > 0:
        print("\n✅ Рекомендуется запустить тесты для проверки работоспособности:")
        print("   pytest tests/smoke/burger_menu_params/ -v --tb=short")


if __name__ == "__main__":
    main()