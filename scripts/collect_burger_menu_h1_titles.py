"""
Скрипт для сбора всех <h1> (текст и класс) с целевых URL бургер-меню.
Авторизация через куки (роль admin). Результат сохраняется в CSV.

Usage:
    python scripts/collect_burger_menu_h1_titles.py
"""
import csv
from typing import List
from playwright.sync_api import sync_playwright
from framework.utils.auth_cookie_provider import get_auth_cookies

# TODO: Замените на актуальный способ получения ссылок (например, из файла)
links: List[str] = [
    "https://bll.by/news",
    "https://bll.by/docs/spravochnaya-informatsiya-200083",
    "https://bll.by/docs/kodeksy-dejstvuyushchie-na-territorii-respubliki-belarus-141580",
    # ... добавьте остальные ссылки ...
]

def main():
    admin_cookies = get_auth_cookies(role="admin")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(admin_cookies)
        page = context.new_page()
        with open("scripts/data/burger_menu_h1_titles.csv", "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["url", "h1_text", "h1_class"])
            for url in links:
                try:
                    page.goto(url, timeout=20000)
                    h1s = page.locator("h1")
                    count = h1s.count()
                    if count == 0:
                        writer.writerow([url, "", ""])
                    else:
                        for i in range(count):
                            h1_text = h1s.nth(i).inner_text().strip()
                            h1_class = h1s.nth(i).get_attribute("class") or ""
                            writer.writerow([url, h1_text, h1_class])
                except Exception as e:
                    writer.writerow([url, f"ERROR: {e}", ""])
        browser.close()

if __name__ == "__main__":
    main() 