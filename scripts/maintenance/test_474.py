#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест файла 474_cookies.json
"""

from cookie_tester import CookieTester

def test_474_file():
    """Тестирует файл 474_cookies.json"""
    tester = CookieTester()
    file_name = "474_cookies.json"
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
    
    print(f"✅ Кука найдена")
    print(f"📋 Value: {cookie_data['value'][:100]}...")
    print(f"🌐 Domain: {cookie_data.get('domain', 'не указан')}")
    print(f"📁 Path: {cookie_data.get('path', 'не указан')}")
    print(f"🔒 HttpOnly: {cookie_data.get('httpOnly', 'не указан')}")
    print(f"🛡️  Secure: {cookie_data.get('secure', 'не указан')}")
    
    # Тестируем авторизацию
    print("\n🚀 Начинаем тестирование авторизации...")
    is_success, details = tester.test_cookie_authorization(cookie_data, file_name)
    print(f"🎯 Результат: {details}")
    
    if is_success:
        print("🎉 Успех! Кука работает!")
    else:
        print("❌ Кука не работает в автоматическом режиме")
        print("💡 Возможные причины:")
        print("   - Истек срок действия куки")
        print("   - Требуются дополнительные заголовки")
        print("   - Сайт проверяет User-Agent или другие параметры")
        print("   - Необходимы дополнительные куки для авторизации")
    
    return is_success

if __name__ == "__main__":
    test_474_file()
