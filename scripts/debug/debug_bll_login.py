#!/usr/bin/env python3
"""
Проверяем форму входа на основном сайте bll.by
"""

from playwright.sync_api import sync_playwright

def debug_bll_login():
    """Проверяем страницу входа на bll.by"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("🔍 Переходим на https://bll.by/login...")

            def handle_response(response):
                print(f"📡 {response.status} {response.url}")
                if response.status >= 300 and response.status < 400:
                    print(f"🔄 Редирект: {response.headers.get('location')}")

            page.on("response", handle_response)

            page.goto("https://bll.by/login", wait_until="domcontentloaded")

            print(f"🏁 Финальный URL: {page.url}")
            print(f"📄 Заголовок: {page.title()}")

            # Ищем элементы входа
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

            print("\n🔍 Проверяем элементы входа:")
            for selector in login_indicators:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"  ✅ {selector}: {len(elements)} элементов")
                    for i, el in enumerate(elements[:2]):
                        attrs = {}
                        if hasattr(el, 'get_attribute'):
                            for attr in ['name', 'id', 'placeholder', 'type', 'class']:
                                val = el.get_attribute(attr)
                                if val:
                                    attrs[attr] = val
                        text = el.inner_text() or "без текста"
                        print(f"    {i+1}. '{text}' {attrs}")
                else:
                    print(f"  ❌ {selector}: не найдено")

            # Проверяем текст на странице
            body_text = page.locator("body").inner_text().lower()
            login_keywords = ['логин', 'login', 'вход', 'signin', 'авторизация', 'auth', 'пароль', 'password']
            found_keywords = [kw for kw in login_keywords if kw in body_text]
            print(f"🔍 Найденные ключевые слова: {found_keywords}")

            # Скриншот
            page.screenshot(path="bll_login_screenshot.png")
            print("📸 Скриншот сохранен: bll_login_screenshot.png")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    debug_bll_login()
