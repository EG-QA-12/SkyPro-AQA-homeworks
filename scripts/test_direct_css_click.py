#!/usr/bin/env python3
"""
Скрипт для тестирования прямого CSS клика по элементам правой колонки.
Использует точные CSS селекторы из отладочной информации.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright


def test_direct_css_click():
    """Тест прямого CSS клика по элементам правой колонки."""
    print("🔍 Тест прямого CSS клика по элементам правой колонки")
    print("=" * 60)
    
    # Загружаем cookies
    try:
        from framework.utils.auth_cookie_provider import get_auth_cookies
        cookies = get_auth_cookies(role="admin")
        print("✅ Cookies загружены")
    except Exception as e:
        print(f"❌ Ошибка загрузки cookies: {e}")
        return False
    
    with sync_playwright() as p:
        # Запускаем браузер в headless режиме
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        # Добавляем cookies
        if cookies:
            context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            print("\n🌐 Переход на главную страницу...")
            page.goto("https://bll.by/", wait_until="domcontentloaded", timeout=30000)
            print("✅ Главная страница загружена")
            
            # Открываем бургер-меню
            print("\n🍔 Открытие бургер-меню...")
            burger_button = page.locator("a.menu-btn.menu-btn_new")
            burger_button.wait_for(state="visible", timeout=10000)
            burger_button.click()
            print("✅ Бургер-меню открыто")
            
            # Ждем загрузки меню
            menu_container = page.locator(".new-menu.new-menu_main")
            menu_container.wait_for(state="visible", timeout=10000)
            print("✅ Меню загружено")
            
            # Прокручиваем вправо для отображения правых колонок
            print("\n➡️  Прокрутка вправо для отображения правых колонок...")
            page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
            page.wait_for_timeout(1000)
            
            # Точ

[Response interrupted by user]
