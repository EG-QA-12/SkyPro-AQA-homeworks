import sys
import json
import csv
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

COOKIES_PATH = Path("cookies/admin_cookies.json")
OUTPUT_DIR = Path("scripts/data")
OUTPUT_FILE = OUTPUT_DIR / "burger_menu_links_admin.csv"
TARGET_URL = "https://bll.by/"
BURGER_SELECTOR = "a.menu-btn.menu-btn_new"
MENU_LINKS_SELECTOR = (
    "a.menu_item_link, a.menu_bl_ttl-main, a.menu_bl_ttl-events, a.menu-tel-lnk"
)


def load_admin_cookies():
    if not COOKIES_PATH.exists():
        print(f"❌ Не найден файл куки: {COOKIES_PATH}")
        sys.exit(1)
    with open(COOKIES_PATH, encoding="utf-8") as f:
        cookies = json.load(f)
    return cookies


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cookies = load_admin_cookies()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        print(f"🌐 Открываю {TARGET_URL}")
        page.goto(TARGET_URL)
        print(f"🔎 Кликаю по бургер-меню: {BURGER_SELECTOR}")
        try:
            page.click(BURGER_SELECTOR)
        except PlaywrightTimeoutError:
            print(f"❌ Не удалось найти бургер-меню по селектору: {BURGER_SELECTOR}")
            browser.close()
            return
        page.wait_for_timeout(1000)  # Ждём анимацию меню
        # Собираем все ссылки
        links = page.query_selector_all(MENU_LINKS_SELECTOR)
        print(f"🔗 Найдено ссылок: {len(links)}")
        result = []
        for link in links:
            href = link.get_attribute("href")
            text = link.inner_text().strip().replace("\n", " ")
            print(f"  - {text} -> {href}")
            if href and text:
                result.append((text, href))
        # Сохраняем в CSV
        with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Текст ссылки", "URL"])
            writer.writerows(result)
        print(f"✅ Собрано {len(result)} ссылок. Сохранено в {OUTPUT_FILE}")
        print("⏳ Оставляю браузер открытым для ручной проверки. Закройте окно для завершения.")
        browser.close()

if __name__ == "__main__":
    main() 