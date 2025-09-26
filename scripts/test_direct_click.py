#!/usr/bin/env python3
"""
Простой скрипт для прямого тестирования клика по элементам правой колонки.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
from framework.utils.auth_cookie_provider import get_auth_cookies


def test_direct_click():
    """Тест прямого клика по элементам правой колонки."""
    print("🔍 Тест прямого клика по элементам правой колонки")
    print("=" * 60)
    
    # Загружаем cookies
    try:
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
            
            # Тест прямого CSS селектора для "Мои данные"
            print("\n🧪 Тест прямого CSS селектора для 'Мои данные':")
            try:
                # Используем точный CSS селектор из отладки
                css_selector = "body > div.layout.layout--docs > header > div > div > div.menu-gumb_new.menu-mobile.active > div.new-menu.new-menu_main > div > div:nth-child(2) > div:nth-child(4) > div.menu_bl_list > div:nth-child(1) > a"
                my_data_link = page.locator(css_selector).first
                
                if my_data_link.count() > 0:
                    print(f"   ✅ Элемент найден по CSS селектору")
                    print(f"   Текст: '{my_data_link.text_content().strip()}'")
                    print(f"   href: {my_data_link.get_attribute('href')}")
                    print(f"   Видим: {my_data_link.is_visible()}")
                    
                    # Пробуем кликнуть через JavaScript для скрытых элементов
                    try:
                        # Используем JavaScript для клика по скрытому элементу
                        js_result = page.evaluate(f"""
                            const element = document.querySelector('{css_selector}');
                            if (element) {{
                                // Прокручиваем элемент в видимую область
                                element.scrollIntoView({{ behavior: 'smooth', block: 'center', inline: 'center' }});
                                
                                // Ждем немного для прокрутки
                                setTimeout(() => {{
                                    try {{
                                        // Пробуем обычный клик
                                        element.click();
                                        console.log('JavaScript click successful');
                                        return true;
                                    }} catch (clickError) {{
                                        console.log('Regular click failed:', clickError);
                                        try {{
                                            // Пробуем dispatchEvent
                                            const event = new MouseEvent('click', {{
                                                bubbles: true,
                                                cancelable: true,
                                                view: window
                                            }});
                                            element.dispatchEvent(event);
                                            console.log('dispatchEvent successful');
                                            return true;
                                        }} catch (eventError) {{
                                            console.log('dispatchEvent failed:', eventError);
                                            return false;
                                        }}
                                    }}
                                }}, 1000);
                                
                                return true;
                            }}
                            return false;
                        """)
                        
                        if js_result:
                            print("   ✅ JavaScript клик успешен")
                            page.wait_for_timeout(3000)
                            print(f"   Текущий URL: {page.url}")
                        else:
                            print("   ❌ JavaScript клик не удался")
                    except Exception as js_error:
                        print(f"   ❌ JavaScript клик не удался: {js_error}")
                else:
                    print("   ❌ Элемент не найден по CSS селектору")
                    
            except Exception as e:
                print(f"   ❌ Ошибка при тестировании CSS селектора: {e}")
            
            # Тест ARIA роли для "Бонусы" (который работает)
            print("\n🧪 Тест ARIA роли для 'Бонусы' (работающий элемент):")
            try:
                bonus_link = page.get_by_role("link", name="Бонусы")
                if bonus_link.count() > 0:
                    print(f"   ✅ Элемент найден по ARIA роли")
                    print(f"   Текст: '{bonus_link.text_content().strip()}'")
                    print(f"   href: {bonus_link.get_attribute('href')}")
                    print(f"   Видим: {bonus_link.is_visible()}")
                    
                    # Пробуем кликнуть
                    try:
                        bonus_link.click(force=True)
                        print("   ✅ Клик успешен")
                        page.wait_for_timeout(2000)
                        print(f"   Текущий URL: {page.url}")
                    except Exception as click_error:
                        print(f"   ❌ Клик не удался: {click_error}")
                else:
                    print("   ❌ Элемент не найден по ARIA роли")
                    
            except Exception as e:
                print(f"   ❌ Ошибка при тестировании ARIA роли: {e}")
            
            # Тест поиска по тексту для всех элементов
            print("\n🧪 Тест поиска по тексту для всех элементов правой колонки:")
            right_column_elements = [
                "Мои данные",
                "Я эксперт",
                "Настройка уведомлений", 
                "Личный кабинет",
                "Бонусы",
                "Сообщения от модератора"
            ]
            
            for element_text in right_column_elements:
                print(f"\n   🔍 '{element_text}':")
                try:
                    text_link = page.locator(f"a:has-text('{element_text}')").first
                    if text_link.count() > 0:
                        print(f"     ✅ Найден - видим: {text_link.is_visible()}")
                        print(f"     href: {text_link.get_attribute('href')}")
                        
                        # Проверяем координаты элемента
                        bounding_box = text_link.bounding_box()
                        if bounding_box:
                            print(f"     Координаты: x={bounding_box['x']:.1f}, y={bounding_box['y']:.1f}, ширина={bounding_box['width']:.1f}, высота={bounding_box['height']:.1f}")
                        else:
                            print(f"     ❌ Нет координат (элемент вне viewport)")
                    else:
                        print(f"     ❌ Не найден")
                except Exception as e:
                    print(f"     ❌ Ошибка: {e}")
            
            print(f"\n🏁 Тестирование завершено")
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            page.close()
            browser.close()


if __name__ == "__main__":
    success = test_direct_click()
    sys.exit(0 if success else 1)
