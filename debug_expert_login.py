#!/usr/bin/env python3
"""
Отладка формы входа на expert.bll.by
"""

import asyncio
from rebrowser_playwright.async_api import async_playwright
from config.secrets_manager import SecretsManager

async def debug_expert_login_form():
    print("=== АНАЛИЗ ФОРМЫ ВХОДА EXPERT.BLL.BY ===\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible для анализа
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        try:
            print("Загружаем expert.bll.by/login...")
            await page.goto("https://expert.bll.by/login", wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)

            print("Анализируем страницу...")

            # Получаем все input поля формы
            inputs = await page.query_selector_all('input')

            print(f"Найдено {len(inputs)} полей ввода:")

            for i, input_elem in enumerate(inputs, 1):
                input_type = await input_elem.get_attribute('type') or 'text'
                name = await input_elem.get_attribute('name') or 'no-name'
                id_attr = await input_elem.get_attribute('id') or 'no-id'
                placeholder = await input_elem.get_attribute('placeholder') or ''

                print(f"  {i}. Тип: {input_type}, Name: {name}, ID: {id_attr}, Placeholder: {placeholder}")

            # Проверяем submit кнопку
            submit_buttons = await page.query_selector_all('input[type="submit"], button[type="submit"]')
            print(f"\nНайдено {len(submit_buttons)} submit кнопок:")
            for i, btn in enumerate(submit_buttons, 1):
                text = await btn.inner_text() or ''
                value = await btn.get_attribute('value') or ''
                print(f"  {i}. Текст: '{text}', Value: '{value}'")

            # Сохраняем screenshot для анализа
            await page.screenshot(path="expert_login_form.png")
            print("\n✅ Screenshot сохранен: expert_login_form.png")

        except Exception as e:
            print(f"❌ Ошибка: {e}")

        finally:
            await browser.close()

    print("\n=== КОНЕЦ АНАЛИЗА ===")

if __name__ == "__main__":
    asyncio.run(debug_expert_login_form())
