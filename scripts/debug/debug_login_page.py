#!/usr/bin/env python3
"""
Скрипт для отладки страницы входа expert.bll.by
"""

import asyncio
from playwright.sync_api import sync_playwright

def debug_login_page():
    """Анализирует страницу входа и выводит доступные поля"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("🔍 Переходим на страницу входа...")
            page.goto("https://expert.bll.by/login", wait_until="domcontentloaded")

            print("📋 Ищем все input поля...")
            inputs = page.query_selector_all("input")
            print(f"Найдено {len(inputs)} input полей:")

            for i, inp in enumerate(inputs):
                input_type = inp.get_attribute("type") or "text"
                name = inp.get_attribute("name") or "без name"
                id_attr = inp.get_attribute("id") or "без id"
                placeholder = inp.get_attribute("placeholder") or "без placeholder"
                class_attr = inp.get_attribute("class") or "без class"

                print(f"  {i+1}. Type: {input_type}, Name: {name}, ID: {id_attr}")
                print(f"      Placeholder: {placeholder}, Class: {class_attr}")

            print("\n🔍 Ищем формы...")
            forms = page.query_selector_all("form")
            print(f"Найдено {len(forms)} форм")

            for i, form in enumerate(forms):
                action = form.get_attribute("action") or "без action"
                method = form.get_attribute("method") or "без method"
                print(f"  Форма {i+1}: action={action}, method={method}")

            print("\n🔍 Ищем кнопки...")
            buttons = page.query_selector_all("button, input[type='submit']")
            print(f"Найдено {len(buttons)} кнопок:")

            for i, btn in enumerate(buttons):
                tag = btn.evaluate("el => el.tagName")
                text = btn.inner_text() or btn.get_attribute("value") or "без текста"
                btn_type = btn.get_attribute("type") or "без type"
                name = btn.get_attribute("name") or "без name"
                print(f"  {i+1}. {tag}: '{text}', type={btn_type}, name={name}")

            print("\n📄 HTML формы входа:")
            form_html = page.query_selector("form")
            if form_html:
                print(form_html.inner_html()[:1000])
            else:
                print("Форма не найдена")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    debug_login_page()
