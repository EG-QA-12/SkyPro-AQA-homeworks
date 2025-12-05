#!/usr/bin/env python3
"""
Скрипт для реальной проверки страницы входа expert.bll.by
"""

from playwright.sync_api import sync_playwright

def debug_login_page_real():
    """Проверяет реальную страницу входа с логированием"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("🔍 Переходим на https://expert.bll.by/login...")

            # Слушаем редиректы
            def handle_response(response):
                print(f"📡 {response.status} {response.url}")
                if response.status >= 300 and response.status < 400:
                    print(f"🔄 Редирект: {response.headers.get('location')}")

            page.on("response", handle_response)

            page.goto("https://expert.bll.by/login", wait_until="domcontentloaded")

            print(f"🏁 Финальный URL: {page.url}")

            # Проверяем, есть ли элементы входа
            login_indicators = [
                'input[type="email"]',
                'input[type="text"]',
                'input[name*="login"]',
                'input[name*="email"]',
                'input[placeholder*="логин" i]',
                'input[placeholder*="email" i]',
                'form',
                '.login-form',
                '#login-form',
                'button:has-text("войти")',
                'button:has-text("login")',
                'input[type="submit"]'
            ]

            print("\n🔍 Проверяем индикаторы формы входа:")
            for selector in login_indicators:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"  ✅ {selector}: {len(elements)} элементов")
                    for i, el in enumerate(elements[:3]):  # Показываем первые 3
                        text = el.inner_text() or el.get_attribute("placeholder") or "без текста"
                        print(f"    {i+1}. '{text}'")
                else:
                    print(f"  ❌ {selector}: не найдено")

            print(f"\n📄 Заголовок страницы: {page.title()}")
            print(f"📄 URL: {page.url}")

            # Проверяем наличие текста о входе
            page_text = page.inner_text().lower()
            login_keywords = ['логин', 'login', 'вход', 'signin', 'авторизация', 'auth']
            found_keywords = [kw for kw in login_keywords if kw in page_text]
            print(f"🔍 Ключевые слова входа на странице: {found_keywords}")

            # Делаем скриншот для анализа
            page.screenshot(path="login_page_screenshot.png")
            print("📸 Скриншот сохранен: login_page_screenshot.png")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    debug_login_page_real()
