#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест для проверки конкретного файла с кукой
"""

from cookie_tester import CookieTester
from pathlib import Path

def test_specific_file(file_name: str):
    """Тестирует конкретный файл"""
    tester = CookieTester()
    
    # Находим файл
    file_path = tester.cookies_dir / file_name
    if not file_path.exists():
        print(f"❌ Файл {file_name} не найден")
        return
    
    print(f"🔍 Тестируем файл: {file_name}")
    
    # Извлекаем куку
    cookie_data = tester.extract_target_cookie(file_path)
    if cookie_data is None:
        print(f"⚠️  Кука 'test_joint_session' не найдена в файле {file_name}")
        return
    
    print(f"✅ Кука найдена, value: {cookie_data['value'][:50]}...")
    
    # Тестируем авторизацию
    is_success, details = tester.test_cookie_authorization(cookie_data, file_name)
    print(f"Результат: {details}")

if __name__ == "__main__":
    # Тестируем известный файл с кукой
    test_specific_file("test_user1_cookies.json")
    
    print("\n" + "="*60)
    
    # Тестируем файл без куки
    test_specific_file("admin_cookies.json")
