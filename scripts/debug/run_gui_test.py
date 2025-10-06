"""
Простой скрипт для запуска GUI браузера.

Цель: Проверить, что GUI режим работает корректно.
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Запускаем браузер в GUI режиме
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Переходим на сайт
    page.goto("https://bll.by")
    
    # Ждем ввода пользователя для закрытия браузера
    input("GUI режим активирован! Нажмите Enter для закрытия...")
    
    # Закрываем браузер
    browser.close()
