#!/usr/bin/env python3
"""
Скрипт для анализа поведения сайта после авторизации.
Помогает понять, как определить успешную авторизацию.
"""

from playwright.sync_api import sync_playwright
from src.config import config
import time

def analyze_auth_behavior():
    """Анализирует поведение сайта после авторизации."""
    
    print("=== Анализ поведения сайта после авторизации ===")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print(f"Переход на страницу логина: {config.LOGIN_URL}")
            page.goto(config.LOGIN_URL)
            
            print(f"Текущий URL: {page.url}")
            print(f"Заголовок страницы: {page.title()}")
            
            # Заполняем форму авторизации
            print("\n=== Заполнение формы авторизации ===")
            page.fill('#login', config.ADMIN_LOGIN)
            page.fill('#password', config.ADMIN_PASS)
            
            print(f"Логин: {config.ADMIN_LOGIN}")
            print("Пароль: [скрыт]")
            print("Отправка формы...")
            
            # Отправляем форму и ждем навигации
            with page.expect_navigation(timeout=30000):
                page.click('input[type="submit"][value="Войти"]')
            
            print(f"\n=== Результат авторизации ===")
            print(f"URL после авторизации: {page.url}")
            print(f"Заголовок после авторизации: {page.title()}")
            
            # Проверяем наличие элементов, указывающих на авторизацию
            print("\n=== Поиск элементов авторизованного пользователя ===")
            
            selectors_to_check = [
                ('a[href*="logout"]', 'Ссылка выхода'),
                ('a[href*="profile"]', 'Ссылка профиля'), 
                ('.user-menu', 'Меню пользователя'),
                ('.user-name', 'Имя пользователя'),
                ('[data-testid="user-menu"]', 'Меню пользователя (data-testid)'),
                ('.logout', 'Кнопка выхода'),
                ('[class*="user"]', 'Элементы с классом user'),
                ('#user', 'Элемент с ID user'),
                ('.header-user', 'Пользователь в шапке'),
                ('.nav-user', 'Пользователь в навигации'),
                ('nav a', 'Ссылки навигации'),
                ('.main-nav a', 'Главная навигация'),
                ('header a', 'Ссылки в шапке')
            ]
            
            found_elements = []
            
            for selector, description in selectors_to_check:
                try:
                    elements = page.locator(selector).all()
                    for i, element in enumerate(elements):
                        if element.is_visible(timeout=1000):
                            text = element.text_content() or ''
                            href = element.get_attribute('href') or ''
                            print(f"✅ {description} [{i}]: {selector}")
                            print(f"   Текст: \"{text.strip()[:100]}\"")
                            if href:
                                print(f"   Ссылка: {href}")
                            found_elements.append((selector, text.strip(), href))
                            print()
                except Exception as e:
                    print(f"❌ Ошибка при поиске {description}: {e}")
            
            print(f"\n=== Анализ содержимого страницы ===")
            
            # Проверяем содержимое страницы
            page_content = page.content()
            keywords_to_check = [
                'logout', 'выход', 'выйти',
                'профиль', 'profile', 
                config.ADMIN_LOGIN.lower(),
                'dashboard', 'панель',
                'admin', 'администратор'
            ]
            
            found_keywords = []
            for keyword in keywords_to_check:
                if keyword in page_content.lower():
                    print(f"✅ Найдено ключевое слово: \"{keyword}\"")
                    found_keywords.append(keyword)
                else:
                    print(f"❌ Не найдено: \"{keyword}\"")
            
            # Проверяем куки
            print(f"\n=== Анализ куков ===")
            cookies = context.cookies()
            print(f"Количество кук: {len(cookies)}")
            
            for cookie in cookies:
                print(f"  {cookie['name']}: {cookie['value'][:50]}...")
            
            # Проверяем возможность перехода на защищенные страницы
            print(f"\n=== Проверка доступа к защищенным страницам ===")
            
            protected_urls = [
                f"{config.BASE_URL}/user/profile",
                f"{config.BASE_URL}/admin",
                f"{config.BASE_URL}/dashboard"
            ]
            
            for test_url in protected_urls:
                try:
                    page.goto(test_url, timeout=10000)
                    if "login" not in page.url.lower():
                        print(f"✅ Доступ к {test_url}: РАЗРЕШЕН")
                        print(f"   Перенаправлен на: {page.url}")
                    else:
                        print(f"❌ Доступ к {test_url}: ЗАБЛОКИРОВАН (перенаправление на логин)")
                except Exception as e:
                    print(f"❌ Ошибка доступа к {test_url}: {e}")
            
            print(f"\n=== Рекомендации для проверки авторизации ===")
            
            if found_elements:
                print("Для проверки авторизации рекомендуется использовать:")
                for selector, text, href in found_elements[:3]:  # Топ-3
                    print(f"  - {selector} (текст: \"{text[:30]}\")")
            
            if found_keywords:
                print(f"Ключевые слова в содержимом: {', '.join(found_keywords[:5])}")
            
            if len(cookies) > 0:
                print(f"Проверка кук: найдено {len(cookies)} куков")
            
            print("\nАнализ завершен. Нажмите Enter для закрытия браузера...")
            input()
            
        except Exception as e:
            print(f"Ошибка во время анализа: {e}")
            input("Нажмите Enter для закрытия браузера...")
        finally:
            browser.close()

if __name__ == "__main__":
    analyze_auth_behavior()
