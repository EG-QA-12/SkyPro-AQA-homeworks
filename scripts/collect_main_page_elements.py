#!/usr/bin/env python3
"""
Скрипт для сбора всех тестируемых элементов главной страницы в авторизованном виде
"""

import csv
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright
from framework.utils.auth_cookie_provider import get_auth_cookies

COOKIES_PATH = Path("cookies/admin_cookies.json")
OUTPUT_DIR = Path("scripts/data")
OUTPUT_FILE = OUTPUT_DIR / "main_page_elements_admin.csv"
TARGET_URL = "https://bll.by/"
WAIT_TIMEOUT = 5000

# Селекторы для основных элементов главной страницы
MAIN_PAGE_SELECTORS = {
    # Верхняя навигация
    "header_links": [
        "a:has-text('О Платформе')",
        "a:has-text('Клуб Экспертов')",
        "a:has-text('Купить')",
        "a:has-text('Войти')",
    ],
    
    # Поиск
    "search_elements": [
        "textbox[placeholder*='Искать']",
        "button:has-text('Submit')",
    ],
    
    # Основные разделы
    "main_sections": [
        "a:has-text('Интервью')",
        "a:has-text('Мероприятия')",
        "a:has-text('Видеоответы')",
        "a:has-text('Кодексы')",
        "a:has-text('Горячие темы')",
        "a:has-text('Всё по одной теме')",
        "a:has-text('Навигаторы')",
        "a:has-text('Чек-листы')",
        "a:has-text('Каталоги форм')",
        "a:has-text('Конструкторы')",
        "a:has-text('Справочники')",
        "a:has-text('Калькуляторы')",
        "a:has-text('Закупки')",
        "a:has-text('Тесты')",
    ],
    
    # Сообщество
    "community_links": [
        "a:has-text('Сообщество')",
        "a:has-text('Задать вопрос')",
        "a:has-text('Все вопросы')",
        "a:has-text('Поиск в сообществе')",
    ],
    
    # Клуб экспертов
    "experts_links": [
        "a:has-text('Клуб Экспертов')",
    ],
    
    # Все интервью
    "interview_links": [
        "a:has-text('Все интервью')",
    ],
    
    # Справочная информация
    "reference_links": [
        "a:has-text('Справочная информация')",
        "a:has-text('Ставка рефинансирования')",
        "a:has-text('Базовая величина')",
        "a:has-text('Средняя з/п за январь')",
        "a:has-text('Пособия на детей')",
        "a:has-text('Базовая арендная величина')",
        "a:has-text('МЗП за февраль')",
        "a:has-text('БПМ')",
        "a:has-text('Смотреть еще')",
    ],
    
    # Сервисы
    "services_links": [
        "a:has-text('Система обмена электронными накладными')",
        "a:has-text('Проверка контрагентов СтатусПро')",
        "a:has-text('Курсы валют')",
        "a:has-text('Все курсы')",
    ],
    
    # Формы документов
    "forms_links": [
        "a:has-text('Формы документов')",
        "a:has-text('Каталоги форм')",
    ],
    
    # Выбор редакции
    "edition_links": [
        "a:has-text('Выбор редакции')",
        "a:has-text('Законодательство')",
        "a:has-text('Бухгалтеру')",
        "a:has-text('Экономисту')",
        "a:has-text('Юристу')",
        "a:has-text('Кадровику')",
        "a:has-text('Секретарю')",
        "a:has-text('Строительство')",
        "a:has-text('Охрана труда')",
        "a:has-text('Экологу')",
    ],
    
    # Обзоры и подписки
    "reviews_links": [
        "a:has-text('Обзоры и подписки')",
        "a:has-text('Обзоры законодательства России и Казахстана')",
        "a:has-text('Отраслевые обзоры')",
        "a:has-text('Информационные каналы')",
        "a:has-text('Подписаться')",
    ],
    
    # Новости
    "news_links": [
        "a:has-text('Новости')",
        "a:has-text('Читать все новости')",
    ],
    
    # Актуальные темы
    "hot_topics_links": [
        "a:has-text('Актуальные темы')",
    ],
    
    # Самое читаемое
    "popular_links": [
        "a:has-text('Самое читаемое')",
        "a:has-text('Читать все')",
    ],
    
    # Ваш личный юрист
    "lawyer_links": [
        "a:has-text('Ваш личный юрист')",
        "a:has-text('Читать все')",
    ],
    
    # Футер
    "footer_links": [
        "a:has-text('Политика Оператора')",
        "a:has-text('Договор присоединения')",
        "a:has-text('Руководство пользователя')",
        "a:has-text('Программа лояльности')",
        "a:has-text('Скачать ярлык на рабочий стол')",
        "a:has-text('Cкачать сравнение текстов')",
        "a[href='mailto:client@business-info.by']",
        "a[href='tel:+375173883252']",
        "a[href='mailto:director@business-info.by']",
        "a[href='mailto:redactor@business-info.by']",
        "a:has-text('www.business-info.by')",
        "a:has-text('Личный кабинет')",
    ]
}

def add_allow_session_param(url: str) -> str:
    """Добавляет параметр allow-session=2 к URL"""
    if "allow-session" not in url:
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}allow-session=2"
    return url

def collect_main_page_elements():
    """Собирает все тестируемые элементы главной страницы"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        
        # Создаем контекст с авторизацией
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ru-RU",
            timezone_id="Europe/Minsk",
            ignore_https_errors=True
        )
        
        # Добавляем заголовки
        context.set_extra_http_headers({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document", 
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        })
        
        # Добавляем куки авторизации
        cookies = get_auth_cookies(role="admin")
        if cookies:
            context.add_cookies(cookies)
            print("✅ Куки авторизации добавлены")
        else:
            print("❌ Не удалось получить куки авторизации")
            browser.close()
            return
        
        page = context.new_page()
        
        # Переход на главную страницу с параметром
        main_url = add_allow_session_param(TARGET_URL)
        print(f"🌐 Открываю {main_url}")
        page.goto(main_url)
        
        # Ждем загрузки страницы
        page.wait_for_timeout(2000)
        
        # Собираем все элементы
        all_elements = []
        
        for category, selectors in MAIN_PAGE_SELECTORS.items():
            print(f"\n🔍 Проверяю категорию: {category}")
            
            for selector in selectors:
                try:
                    elements = page.locator(selector)
                    count = elements.count()
                    
                    if count > 0:
                        for i in range(min(count, 5)):  # Ограничиваем 5 элементами на селектор
                            element = elements.nth(i)
                            if element.is_visible():
                                href = element.get_attribute("href") or ""
                                text = element.inner_text().strip().replace("\n", " ")[:100]
                                
                                if href or text:
                                    all_elements.append({
                                        "category": category,
                                        "selector": selector,
                                        "text": text,
                                        "href": href,
                                        "index": i
                                    })
                                    print(f"  + [{category}] {text} -> {href}")
                    else:
                        print(f"  - Нет элементов для селектора: {selector}")
                        
                except Exception as e:
                    print(f"  ⚠️  Ошибка при обработке селектора {selector}: {e}")
        
        # Сохраняем в CSV
        with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Категория", "Селектор", "Текст", "URL", "Индекс"])
            for element in all_elements:
                writer.writerow([
                    element["category"],
                    element["selector"],
                    element["text"],
                    element["href"],
                    element["index"]
                ])
        
        print(f"\n✅ Собрано {len(all_elements)} элементов. Сохранено в {OUTPUT_FILE}")
        print("⏳ Оставляю браузер открытым для ручной проверки. Закройте окно для завершения.")
        
        browser.close()

if __name__ == "__main__":
    collect_main_page_elements()
