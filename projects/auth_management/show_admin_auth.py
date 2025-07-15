#!/usr/bin/env python3
"""
Визуальная демонстрация авторизации через куки для админа.
"""
import sys
import os
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright
from projects.auth_management.config import config
from projects.auth_management.auth import load_cookies
from scripts.auth_integration import AuthIntegration
from framework.utils.url_utils import add_allow_session_param, is_headless

def show_admin_auth():
    """Показывает авторизацию админа через куки."""
    print("🍪 Демонстрация авторизации админа через куки")
    
    login = "admin"
    cookies_file = config.COOKIES_PATH.parent / f"{login}_cookies.json"
    
    if not cookies_file.exists():
        print(f"❌ Файл кук для пользователя {login} не найден: {cookies_file}")
        return
        
    print(f"✅ Найден файл кук: {cookies_file}")
    
    with sync_playwright() as p:
        # Запускаем браузер видимо
        print("🌐 Запуск браузера...")
        browser = p.chromium.launch(headless=False)
        
        # 1. Сначала показываем обычную страницу без авторизации
        print("\n📋 Шаг 1: Переход на сайт без авторизации")
        context_no_auth = browser.new_context()
        page_no_auth = context_no_auth.new_page()
        
        # Переходим на целевую страницу
        page_no_auth.goto(add_allow_session_param(config.TARGET_URL, is_headless()), timeout=30000)
        print(f"   🔗 URL без авторизации: {page_no_auth.url}")
        
        # Ждем 3 секунды, чтобы пользователь увидел страницу логина
        print("   ⏱️ Ожидание 3 секунды для демонстрации страницы логина...")
        page_no_auth.wait_for_timeout(3000)
        
        # Закрываем контекст
        context_no_auth.close()
        
        # 2. Потом показываем страницу с авторизацией через куки
        print("\n📋 Шаг 2: Переход на сайт с авторизацией через куки")
        
        # Создаем новый контекст
        context_with_auth = browser.new_context()
        
        # Подставляем куки в контекст
        AuthIntegration().setup_authenticated_context(context_with_auth, login)
        
        # Открываем новую страницу
        page_with_auth = context_with_auth.new_page()
        
        # Переходим на целевую страницу
        print(f"   🔗 Переход на целевую страницу: {config.TARGET_URL}")
        page_with_auth.goto(add_allow_session_param(config.TARGET_URL, is_headless()), timeout=30000)
        print(f"   🔗 URL с авторизацией: {page_with_auth.url}")
        
        # Проверяем наличие элементов, подтверждающих авторизацию
        if page_with_auth.locator("text=Выход").count() > 0:
            print("   ✅ Найден элемент 'Выход' - пользователь авторизован")
        elif page_with_auth.locator("text=Профиль").count() > 0:
            print("   ✅ Найден элемент 'Профиль' - пользователь авторизован")
        else:
            print("   ⚠️ Элементы авторизации не найдены")
            
        # Ждем 10 секунд, чтобы пользователь мог исследовать страницу
        print("   ⏱️ Ожидание 10 секунд для исследования страницы...")
        page_with_auth.wait_for_timeout(10000)
        
        # Закрываем браузер
        browser.close()
        
        print("\n🎉 Демонстрация завершена! Вы увидели разницу между неавторизованной сессией и сессией с куками.")
        
if __name__ == "__main__":
    show_admin_auth()
