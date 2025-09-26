#!/usr/bin/env python3
"""
Скрипт для проверки видимости элементов меню в разных режимах.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
import json
from pathlib import Path


def check_menu_visibility():
    """Проверяет видимость элементов меню в разных режимах."""
    print("🔍 Проверка видимости элементов меню")
    print("=" * 60)
    
    # Загружаем cookies
    try:
        from framework.utils.auth_cookie_provider import get_auth_cookies
        cookies = get_auth_cookies(role="admin")
        print("✅ Cookies загружены")
    except Exception as e:
        print(f"❌ Ошибка загрузки cookies: {e}")
        return
    
    # Тестируем в обоих режимах
    modes = [True, False]  # headless, gui
    mode_names = ["headless", "gui"]
    
    for headless_mode, mode_name in zip(modes, mode_names):
        print(f"\n{'='*20} РЕЖИМ: {mode_name.upper()} {'='*20}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless_mode)
            context = browser.new_context()
            
            if cookies:
                context.add_cookies(cookies)
            
            page = context.new_page()
            
            try:
                print(f"\n🌐 Переход на главную страницу ({mode_name})...")
                page.goto("https://bll.by/", wait_until="domcontentloaded", timeout=30000)
                print(f"✅ Главная страница загружена ({mode_name})")
                
                # Открываем бургер-меню
                print(f"\n🍔 Открытие бургер-меню ({mode_name})...")
                burger_button = page.locator("a.menu-btn.menu-btn_new")
                burger_button.wait_for(state="visible", timeout=10000)
                burger_button.click()
                print(f"✅ Бургер-меню открыто ({mode_name})")
                
                # Ждем загрузки меню
                menu_container = page.locator(".new-menu.new-menu_main")
                menu_container.wait_for(state="visible", timeout=10000)
                print(f"✅ Меню загружено ({mode_name})")
                
                # Прокручиваем вправо
                print(f"\n➡️  Прокрутка вправо ({mode_name})...")
                page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
                page.wait_for_timeout(1000)
                
                # Проверяем элементы разных колонок
                print(f"\n📋 ПРОВЕРКА ЭЛЕМЕНТОВ ({mode_name}):")
                print("-" * 40)
                
                # Элементы разных колонок
                test_elements = [
                    ("Левая колонка", "Новости"),
                    ("Центральная колонка", "Поиск в сообществе"),
                    ("Правая колонка", "Мои данные"),
                    ("Правая колонка", "Я эксперт")
                ]
                
                for column_name, element_text in test_elements:
                    try:
                        # Ищем элемент
                        element = page.locator(f"a:has-text('{element_text}')").first
                        count = element.count()
                        
                        if count > 0:
                            is_visible = element.is_visible()
                            href = element.get_attribute('href') or ""
                            print(f"  {column_name} - '{element_text}':")
                            print(f"    Найдено: {count}")
                            print(f"    Видим: {'✅' if is_visible else '❌'}")
                            print(f"    href: {href}")
                        else:
                            print(f"  {column_name} - '{element_text}': ❌ Не найден")
                            
                    except Exception as e:
                        print(f"  {column_name} - '{element_text}': ❌ Ошибка: {e}")
                
                # Проверяем все ссылки меню
                print(f"\n🔗 ВСЕ ССЫЛКИ МЕНЮ ({mode_name}):")
                print("-" * 30)
                try:
                    all_links = page.locator("a.menu_item_link")
                    total_count = all_links.count()
                    visible_count = 0
                    
                    for i in range(min(20, total_count)):
                        try:
                            link = all_links.nth(i)
                            if link.is_visible():
                                visible_count += 1
                                text = link.text_content().strip() if link.text_content() else ""
                                href = link.get_attribute('href') or ""
                                print(f"  [{i:2d}] ✅ '{text}' -> {href}")
                        except Exception:
                            continue
                    
                    print(f"  Всего ссылок: {total_count}")
                    print(f"  Видимых ссылок: {visible_count}")
                    
                except Exception as e:
                    print(f"  ❌ Ошибка при проверке всех ссылок: {e}")
                
            except Exception as e:
                print(f"❌ Ошибка в режиме {mode_name}: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                page.close()
                browser.close()
    
    print(f"\n🏁 Проверка видимости завершена")


if __name__ == "__main__":
    check_menu_visibility()
