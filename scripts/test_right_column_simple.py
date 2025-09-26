#!/usr/bin/env python3
"""
Простой тест для проверки элементов правой колонки меню.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
import json
from pathlib import Path


def test_right_column_elements():
    """Тест элементов правой колонки меню."""
    print("🔍 Тест элементов правой колонки меню")
    print("=" * 50)
    
    # Загружаем cookies
    try:
        from framework.utils.auth_cookie_provider import get_auth_cookies
        cookies = get_auth_cookies(role="admin")
        print("✅ Cookies загружены")
    except Exception as e:
        print(f"❌ Ошибка загрузки cookies: {e}")
        return False
    
    with sync_playwright() as p:
        # Запускаем браузер в headless режиме
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        # Добавляем cookies
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
            
            # Прокручиваем вправо для отображения правых колонок
            print("\n➡️  Прокрутка вправо для отображения правых колонок...")
            page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
            page.wait_for_timeout(1000)
            
            # Тестовые элементы правой колонки
            right_column_elements = [
                "Мои данные",
                "Я эксперт", 
                "Настройка уведомлений",
                "Личный кабинет",
                "Бонусы"
            ]
            
            print(f"\n📋 Тестирование элементов правой колонки ({len(right_column_elements)} элементов):")
            print("-" * 50)
            
            results = {}
            
            for element_text in right_column_elements:
                print(f"\n🔍 Тест элемента '{element_text}':")
                
                try:
                    # Создаем Page Object
                    from tests.e2e.pages.burger_menu_page import BurgerMenuPage
                    burger_menu = BurgerMenuPage(page)
                    
                    # Используем разные стратегии клика
                    strategies = [
                        ("click_link_by_text", lambda: burger_menu.click_link_by_text(element_text)),
                        ("click_link_by_role", lambda: burger_menu.click_link_by_role(element_text)),
                        ("click_link_by_text_and_class", lambda: burger_menu.click_link_by_text_and_class(element_text)),
                        ("click_link_by_href", lambda: burger_menu.click_link_by_href(element_text.lower().replace(' ', '-'))),
                    ]
                    
                    success = False
                    for strategy_name, strategy_func in strategies:
                        try:
                            print(f"   🔄 Пробуем стратегию: {strategy_name}")
                            result = strategy_func()
                            if result:
                                success = True
                                print(f"   ✅ Успешно с помощью {strategy_name}")
                                results[element_text] = {"status": "success", "strategy": strategy_name}
                                break
                            else:
                                print(f"   ⚠️  Неудача с {strategy_name}")
                        except Exception as strategy_error:
                            print(f"   ❌ Ошибка в {strategy_name}: {strategy_error}")
                            continue
                    
                    if not success:
                        print(f"   ❌ Все стратегии не сработали для '{element_text}'")
                        results[element_text] = {"status": "failed", "strategy": "all"}
                        
                except Exception as e:
                    print(f"   ❌ Ошибка при тестировании '{element_text}': {e}")
                    results[element_text] = {"status": "error", "error": str(e)}
            
            # Выводим результаты
            print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
            print("=" * 50)
            
            success_count = sum(1 for r in results.values() if r["status"] == "success")
            failed_count = sum(1 for r in results.values() if r["status"] == "failed")
            error_count = sum(1 for r in results.values() if r["status"] == "error")
            
            print(f"✅ Успешные: {success_count}")
            print(f"❌ Неудачные: {failed_count}")
            print(f"💥 Ошибки: {error_count}")
            print(f"📊 Всего: {len(results)}")
            
            for element, result in results.items():
                status_symbol = {
                    "success": "✅",
                    "failed": "❌", 
                    "error": "💥"
                }.get(result["status"], "?")
                strategy_info = f" ({result.get('strategy', 'N/A')})" if result["status"] != "error" else f" ({result.get('error', 'N/A')})"
                print(f"   {status_symbol} {element}{strategy_info}")
            
            # Подробная диагностика для неудачных элементов
            print(f"\n🔧 ПОДРОБНАЯ ДИАГНОСТИКА НЕУДАЧНЫХ ЭЛЕМЕНТОВ:")
            print("-" * 50)
            
            for element_text, result in results.items():
                if result["status"] in ["failed", "error"]:
                    print(f"\n🔍 Диагностика '{element_text}':")
                    
                    # Поиск элемента разными способами
                    search_strategies = [
                        f"a:has-text('{element_text}')",
                        f"a.menu_item_link:has-text('{element_text}')",
                        f".menu_item_link:has-text('{element_text}')",
                        f"a[href*='{element_text.lower().replace(' ', '-')}]"
                    ]
                    
                    for strategy in search_strategies:
                        try:
                            elements = page.locator(strategy).all()
                            print(f"   Стратегия '{strategy}': найдено {len(elements)} элементов")
                            for i, elem in enumerate(elements[:3]):  # Показываем первые 3
                                try:
                                    text = elem.text_content().strip() if elem.text_content() else ""
                                    href = elem.get_attribute('href') or ""
                                    visible = elem.is_visible()
                                    print(f"     [{i}] {'VISIBLE' if visible else 'HIDDEN'} '{text}' -> {href}")
                                except Exception:
                                    print(f"     [{i}] Ошибка получения информации")
                        except Exception as search_error:
                            print(f"   Стратегия '{strategy}' ошибка: {search_error}")
            
            return success_count > 0  # Возвращаем True если хотя бы один элемент сработал
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            page.close()
            browser.close()
            print(f"\n🏁 Тестирование завершено")


if __name__ == "__main__":
    success = test_right_column_elements()
    sys.exit(0 if success else 1)
