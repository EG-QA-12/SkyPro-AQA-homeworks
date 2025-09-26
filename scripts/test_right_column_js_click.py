#!/usr/bin/env python3
"""
Скрипт для тестирования JavaScript клика по элементам правой колонки меню.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
import json
from pathlib import Path


def test_right_column_js_click():
    """Тест JavaScript клика по элементам правой колонки меню."""
    print("🔍 Тест JavaScript клика по элементам правой колонки меню")
    print("=" * 60)
    
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
                {"name": "Мои данные", "expected_url": "https://ca.bll.by/user/profile"},
                {"name": "Я эксперт", "expected_url": "https://expert.bll.by/user/expert"},
                {"name": "Настройка уведомлений", "expected_url": "https://ca.bll.by/notification/settings"},
                {"name": "Личный кабинет", "expected_url": "https://business-info.by/pc"},
                {"name": "Бонусы", "expected_url": "https://bonus.bll.by"},
                {"name": "Сообщения от модератора", "expected_url": "https://expert.bll.by/moderator/messages"}
            ]
            
            print(f"\n📋 Тестирование элементов правой колонки ({len(right_column_elements)} элементов):")
            print("-" * 50)
            
            results = {}
            
            for element_info in right_column_elements:
                element_name = element_info["name"]
                expected_url = element_info["expected_url"]
                
                print(f"\n🔍 Тест элемента '{element_name}':")
                print(f"   Ожидаемый URL: {expected_url}")
                
                try:
                    # Используем JavaScript для поиска и клика по элементу
                    js_result = page.evaluate(f"""
                        // Ищем элемент по тексту в правой колонке
                        const elements = document.querySelectorAll('a.menu_item_link');
                        let clicked = false;
                        let found_element = null;
                        
                        // Прокручиваем вправо для отображения правых колонок
                        window.scrollTo({{ left: 1000, behavior: 'smooth' }});
                        
                        // Ищем элемент по тексту
                        for (let elem of elements) {{
                            const text = elem.textContent || '';
                            if (text.includes('{element_name}')) {{
                                found_element = elem;
                                console.log('Найден элемент:', text, elem.href);
                                break;
                            }}
                        }}
                        
                        if (found_element) {{
                            // Прокручиваем элемент в видимую область
                            found_element.scrollIntoView({{ behavior: 'smooth', block: 'center', inline: 'center' }});
                            
                            // Ждем немного для прокрутки
                            setTimeout(() => {{
                                try {{
                                    // Пробуем обычный клик
                                    found_element.click();
                                    clicked = true;
                                    console.log('Обычный клик успешен');
                                }} catch (clickError) {{
                                    console.log('Обычный клик не удался:', clickError);
                                    try {{
                                        // Пробуем dispatchEvent
                                        const event = new MouseEvent('click', {{
                                            bubbles: true,
                                            cancelable: true,
                                            view: window
                                        }});
                                        found_element.dispatchEvent(event);
                                        clicked = true;
                                        console.log('dispatchEvent успешен');
                                    }} catch (eventError) {{
                                        console.log('dispatchEvent не удался:', eventError);
                                    }}
                                }}
                            }}, 1000);
                            
                            clicked;
                        }} else {{
                            console.log('Элемент не найден');
                            clicked = false;
                        }}
                        
                        clicked;
                    """)
                    
                    page.wait_for_timeout(2000)  # Ждем переход
                    
                    if js_result:
                        current_url = page.url
                        print(f"   ✅ JavaScript клик успешен!")
                        print(f"   Текущий URL: {current_url}")
                        
                        # Проверяем, что переход произошел
                        if expected_url.split('//')[1].split('/')[0] in current_url:
                            results[element_name] = {"status": "success", "url": current_url}
                            print(f"   🎯 URL содержит ожидаемый домен")
                        else:
                            results[element_name] = {"status": "partial", "url": current_url, "expected": expected_url}
                            print(f"   ⚠️  URL не содержит ожидаемый домен")
                    else:
                        results[element_name] = {"status": "failed", "error": "JavaScript клик не удался"}
                        print(f"   ❌ JavaScript клик не удался")
                        
                except Exception as e:
                    print(f"   ❌ Ошибка JavaScript клика: {e}")
                    results[element_name] = {"status": "error", "error": str(e)}
                
                # Возвращаемся на главную для следующего теста
                try:
                    page.goto("https://bll.by/", wait_until="domcontentloaded", timeout=30000)
                    
                    # Открываем бургер-меню заново
                    burger_button = page.locator("a.menu-btn.menu-btn_new")
                    burger_button.wait_for(state="visible", timeout=10000)
                    burger_button.click()
                    
                    # Ждем загрузки меню
                    menu_container = page.locator(".new-menu.new-menu_main")
                    menu_container.wait_for(state="visible", timeout=10000)
                    
                    # Прокручиваем вправо снова
                    page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
                    page.wait_for_timeout(1000)
                except Exception as reset_error:
                    print(f"   ⚠️  Ошибка сброса страницы: {reset_error}")
            
            # Выводим результаты
            print(f"\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
            print("=" * 50)
            
            success_count = sum(1 for r in results.values() if r["status"] == "success")
            partial_count = sum(1 for r in results.values() if r["status"] == "partial")
            failed_count = sum(1 for r in results.values() if r["status"] in ["failed", "error"])
            
            print(f"✅ Успешные: {success_count}")
            print(f"⚠️  Частичные: {partial_count}")
            print(f"❌ Неудачные: {failed_count}")
            print(f"📊 Всего: {len(results)}")
            
            for element_name, result in results.items():
                status_symbol = {
                    "success": "✅",
                    "partial": "⚠️", 
                    "failed": "❌",
                    "error": "💥"
                }.get(result["status"], "?")
                
                if result["status"] == "success":
                    print(f"   {status_symbol} {element_name} -> {result['url']}")
                elif result["status"] == "partial":
                    print(f"   {status_symbol} {element_name} -> {result['url']} (ожидалось: {result['expected']})")
                else:
                    print(f"   {status_symbol} {element_name} -> {result.get('error', 'N/A')}")
            
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
    success = test_right_column_js_click()
    sys.exit(0 if success else 1)
