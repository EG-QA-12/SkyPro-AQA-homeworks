#!/usr/bin/env python3
"""
Простой скрипт для диагностики меню в headless режиме.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
import json
from pathlib import Path


def debug_menu_simple():
    """Простая диагностика меню."""
    print("🔍 Простая диагностика меню")
    print("=" * 50)
    
    # Загружаем cookies
    try:
        from framework.utils.auth_cookie_provider import get_auth_cookies
        cookies = get_auth_cookies(role="admin")
        print("✅ Cookies загружены")
    except Exception as e:
        print(f"❌ Ошибка загрузки cookies: {e}")
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        if cookies:
            context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            print("\n🌐 Переход на главную страницу...")
            page.goto("https://bll.by/", wait_until="domcontentloaded", timeout=30000)
            print("✅ Главная страница загружена")
            
            # Открываем бургер-меню
            print("\n🍔 Открытие бургер-меню...")
            burger_button = page.locator("a.menu-btn.menu-btn_new")
            burger_button.wait_for(state="visible", timeout=10000)
            burger_button.click()
            print("✅ Бургер-меню открыто")
            
            # Ждем загрузки меню
            menu_container = page.locator(".new-menu.new-menu_main")
            menu_container.wait_for(state="visible", timeout=10000)
            print("✅ Меню загружено")
            
            # Прокручиваем вправо
            print("\n➡️  Прокрутка вправо...")
            page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
            page.wait_for_timeout(1000)
            
            # Проверяем элементы
            print("\n📋 ПРОВЕРКА ЭЛЕМЕНТОВ:")
            print("-" * 30)
            
            # Левая колонка
            try:
                news = page.locator("a:has-text('Новости')")
                print(f"Новости: найдено={news.count()}, видим={news.is_visible()}")
            except Exception as e:
                print(f"Новости: ошибка={e}")
            
            # Центральная колонка
            try:
                community = page.locator("a:has-text('Поиск в сообществе')")
                print(f"Поиск в сообществе: найдено={community.count()}, видим={community.is_visible()}")
            except Exception as e:
                print(f"Поиск в сообществе: ошибка={e}")
            
            # Правая колонка
            try:
                my_data = page.locator("a:has-text('Мои данные')")
                print(f"Мои данные: найдено={my_data.count()}, видим={my_data.is_visible()}")
                if my_data.count() > 0:
                    href = my_data.get_attribute('href')
                    print(f"  href: {href}")
            except Exception as e:
                print(f"Мои данные: ошибка={e}")
            
            try:
                expert = page.locator("a:has-text('Я эксперт')")
                print(f"Я эксперт: найдено={expert.count()}, видим={expert.is_visible()}")
                if expert.count() > 0:
                    href = expert.get_attribute('href')
                    print(f"  href: {href}")
            except Exception as e:
                print(f"Я эксперт: ошибка={e}")
            
            # Проверяем все ссылки
            print("\n🔗 ВСЕ ССЫЛКИ МЕНЮ:")
            print("-" * 20)
            try:
                all_links = page.locator("a.menu_item_link")
                count = all_links.count()
                print(f"Всего ссылок: {count}")
                
                for i in range(min(20, count)):
                    try:
                        link = all_links.nth(i)
                        text = link.text_content().strip() if link.text_content() else ""
                        href = link.get_attribute('href') or ""
                        visible = link.is_visible()
                        print(f"  [{i:2d}] {'_VISIBLE_' if visible else '_HIDDEN_'} '{text}' -> {href}")
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"Ошибка при проверке всех ссылок: {e}")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            page.close()
            browser.close()
            print(f"\n🏁 Диагностика завершена")


if __name__ == "__main__":
    debug_menu_simple()
