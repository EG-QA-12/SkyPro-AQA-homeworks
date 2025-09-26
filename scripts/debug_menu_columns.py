#!/usr/bin/env python3
"""
Скрипт для диагностики элементов меню в разных колонках.

Проверяет, какие элементы видимы в headless режиме.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
import json


def load_cookies():
    """Загружает cookies из файла."""
    try:
        with open('cookies.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Файл cookies.json не найден")
        return None
    except Exception as e:
        print(f"❌ Ошибка загрузки cookies: {e}")
        return None


def debug_menu_columns():
    """Диагностика элементов меню в разных колонках."""
    print("🔍 Диагностика элементов меню в разных колонках")
    print("=" * 60)
    
    cookies = load_cookies()
    if not cookies:
        print("❌ Не удалось загрузить cookies")
        return
    
    with sync_playwright() as p:
        # Запускаем браузер в headless режиме
        browser = p.chromium.launch(headless=True)
        
        # Создаем контекст с cookies
        context = browser.new_context()
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        try:
            print("🌐 Переход на главную страницу...")
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
            
            # Проверяем элементы в разных колонках
            print("\n" + "=" * 60)
            print("ТЕСТИРОВАНИЕ ЭЛЕМЕНТОВ В РАЗНЫХ КОЛОНКАХ")
            print("=" * 60)
            
            # Тестовые элементы из каждой колонки
            test_elements = {
                "Левая колонка": [
                    "Новости",
                    "Справочная информация",
                    "Кодексы",
                    "Чек-листы"
                ],
                "Центральная колонка": [
                    "Поиск в базе документов",
                    "Поиск в сообществе",
                    "Проверка контрагента",
                    "Задать вопрос"
                ],
                "Правая колонка": [
                    "Мои данные",
                    "Я эксперт",
                    "Настройка уведомлений",
                    "Личный кабинет"
                ]
            }
            
            results = {}
            
            for column_name, elements in test_elements.items():
                print(f"\n📋 {column_name}:")
                print("-" * 40)
                
                results[column_name] = {
                    "working": [],
                    "hidden": [],
                    "not_found": []
                }
                
                # Прокручиваем к соответствующей колонке
                scroll_positions = {
                    "Левая колонка": 0,
                    "Центральная колонка": 500,
                    "Правая колонка": 1000
                }
                
                page.evaluate(f"window.scrollTo({{ left: {scroll_positions[column_name]}, behavior: 'smooth' }});")
                page.wait_for_timeout(500)
                
                for element_text in elements:
                    try:
                        # Ищем элемент разными способами
                        strategies = [
                            f"a:has-text('{element_text}')",
                            f"a.menu_item_link:has-text('{element_text}')",
                            f".menu_item_link:has-text('{element_text}')"
                        ]
                        
                        found = False
                        for strategy in strategies:
                            try:
                                element = page.locator(strategy)
                                if element.count() > 0:
                                    if element.is_visible():
                                        results[column_name]["working"].append(element_text)
                                        print(f"  ✓ '{element_text}' - видим")
                                    else:
                                        results[column_name]["hidden"].append(element_text)
                                        print(f"  ⚠ '{element_text}' - существует но скрыт")
                                    found = True
                                    break
                            except Exception:
                                continue
                        
                        if not found:
                            results[column_name]["not_found"].append(element_text)
                            print(f"  ✗ '{element_text}' - не найден")
                            
                    except Exception as e:
                        print(f"  ❌ '{element_text}' - ошибка: {e}")
            
            # Выводим сводку результатов
            print("\n" + "=" * 60)
            print("СВОДКА РЕЗУЛЬТАТОВ")
            print("=" * 60)
            
            for column_name, result in results.items():
                total = sum(len(v) for v in result.values())
                working = len(result["working"])
                hidden = len(result["hidden"])
                not_found = len(result["not_found"])
                
                print(f"\n📊 {column_name} (всего {total} элементов):")
                print(f"   ✅ Работающие: {working}")
                print(f"   ⚠ Скрытые: {hidden}")
                print(f"   ❌ Ненайденные: {not_found}")
                
                if result["working"]:
                    print(f"   Работающие элементы: {', '.join(result['working'])}")
                if result["hidden"]:
                    print(f"   Скрытые элементы: {', '.join(result['hidden'])}")
                if result["not_found"]:
                    print(f"   Ненайденные элементы: {', '.join(result['not_found'])}")
            
            # Подробная диагностика правой колонки
            print("\n" + "=" * 60)
            print("ПОДРОБНАЯ ДИАГНОСТИКА ПРАВОЙ КОЛОНКИ")
            print("=" * 60)
            
            page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
            page.wait_for_timeout(500)
            
            # JavaScript диагностика
            print("\n🔍 JavaScript диагностика всех ссылок:")
            js_result = page.evaluate("""
                const elements = document.querySelectorAll('a.menu_item_link');
                let result = [];
                for (let i = 0; i < Math.min(elements.length, 20); i++) {
                    const elem = elements[i];
                    const text = elem.textContent ? elem.textContent.trim() : '';
                    const href = elem.href || '';
                    const isVisible = elem.offsetParent !== null;
                    const isDisplayed = window.getComputedStyle(elem).display !== 'none';
                    
                    result.push({
                        index: i,
                        text: text,
                        href: href,
                        visible: isVisible,
                        displayed: isDisplayed,
                        offsetParent: elem.offsetParent ? elem.offsetParent.tagName : 'null'
                    });
                }
                return result;
            """)
            
            visible_count = sum(1 for item in js_result if item['visible'])
            print(f"   Всего ссылок найдено: {len(js_result)}")
            print(f"   Видимых ссылок: {visible_count}")
            
            print("\n   Подробная информация по ссылкам:")
            for item in js_result[:10]:  # Показываем первые 10
                status = "_VISIBLE_" if item['visible'] else "_HIDDEN_"
                print(f"     [{item['index']:2d}] {status} '{item['text']}' -> {item['href']}")
            
            # Поиск конкретного элемента "Мои данные"
            print("\n🔍 Поиск элемента 'Мои данные':")
            my_data_strategies = [
                "a:has-text('Мои данные')",
                "a[href*='ca.bll.by/user/profile']",
                "a.menu_item_link"
            ]
            
            for strategy in my_data_strategies:
                try:
                    elements = page.locator(strategy)
                    count = elements.count()
                    print(f"   Стратегия '{strategy}': найдено {count} элементов")
                    if count > 0:
                        for i in range(min(3, count)):
                            try:
                                elem = elements.nth(i)
                                text = elem.text_content().strip() if elem.text_content() else ""
                                href = elem.get_attribute('href') or ""
                                visible = elem.is_visible()
                                print(f"     [{i}] {'VISIBLE' if visible else 'HIDDEN'} '{text}' -> {href}")
                            except Exception as e:
                                print(f"     [{i}] Ошибка получения информации: {e}")
                except Exception as e:
                    print(f"   Стратегия '{strategy}' ошибка: {e}")
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            page.close()
            browser.close()
            print("\n🏁 Диагностика завершена")


if __name__ == "__main__":
    debug_menu_columns()
