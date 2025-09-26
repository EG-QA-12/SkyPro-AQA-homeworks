#!/usr/bin/env python3
"""
Скрипт для диагностики правой колонки меню в headless режиме.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
import json
from pathlib import Path


def debug_right_column():
    """Диагностика правой колонки меню."""
    print("🔍 Диагностика правой колонки меню")
    print("=" * 50)
    
    # Загружаем cookies из существующего теста
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        from framework.utils.auth_cookie_provider import get_auth_cookies
        cookies = get_auth_cookies(role="admin")
        print("✅ Cookies загружены")
    except Exception as e:
        print(f"❌ Ошибка загрузки cookies: {e}")
        return
    
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
            
            # Проверяем конкретные элементы правой колонки
            right_column_elements = [
                "Мои данные",
                "Я эксперт", 
                "Настройка уведомлений",
                "Личный кабинет",
                "Бонусы",
                "Сообщения от модератора"
            ]
            
            print(f"\n📋 Проверка элементов правой колонки ({len(right_column_elements)} элементов):")
            print("-" * 50)
            
            working_elements = []
            hidden_elements = []
            not_found_elements = []
            
            for element_text in right_column_elements:
                print(f"\n🔍 Проверка элемента '{element_text}':")
                
                # Разные стратегии поиска
                strategies = [
                    f"a:has-text('{element_text}')",
                    f"a.menu_item_link:has-text('{element_text}')",
                    f".menu_item_link:has-text('{element_text}')",
                    f"a[href*='{element_text.lower().replace(' ', '')}')]"
                ]
                
                found = False
                for strategy in strategies:
                    try:
                        element = page.locator(strategy)
                        count = element.count()
                        if count > 0:
                            print(f"   📍 Найден по стратегии: {strategy} (найдено: {count})")
                            
                            # Проверяем видимость
                            try:
                                is_visible = element.is_visible()
                                href = element.get_attribute('href') or "нет href"
                                print(f"   👁️  Видимость: {is_visible}")
                                print(f"   🔗 href: {href}")
                                
                                if is_visible:
                                    working_elements.append(element_text)
                                    found = True
                                    break
                                else:
                                    hidden_elements.append(element_text)
                                    found = True
                                    break
                            except Exception as vis_error:
                                print(f"   ⚠️  Ошибка проверки видимости: {vis_error}")
                                hidden_elements.append(element_text)
                                found = True
                                break
                    except Exception as strat_error:
                        continue
                
                if not found:
                    print(f"   ❌ Не найден")
                    not_found_elements.append(element_text)
            
            # Выводим результаты
            print(f"\n📊 РЕЗУЛЬТАТЫ:")
            print("=" * 50)
            print(f"✅ Работающие элементы: {len(working_elements)}")
            print(f"⚠️  Скрытые элементы: {len(hidden_elements)}")
            print(f"❌ Ненайденные элементы: {len(not_found_elements)}")
            
            if working_elements:
                print(f"   Работающие: {', '.join(working_elements)}")
            if hidden_elements:
                print(f"   Скрытые: {', '.join(hidden_elements)}")
            if not_found_elements:
                print(f"   Ненайденные: {', '.join(not_found_elements)}")
            
            # JavaScript диагностика
            print(f"\n🔧 JAVASCRIPT ДИАГНОСТИКА:")
            print("-" * 30)
            
            js_result = page.evaluate("""
                // Ищем все ссылки меню
                const allLinks = document.querySelectorAll('a.menu_item_link');
                const rightColumnLinks = [];
                
                // Прокручиваем страницу вправо для диагностики
                window.scrollTo({ left: 1000, behavior: 'smooth' });
                
                // Ищем элементы правой колонки
                for (let i = 0; i < Math.min(allLinks.length, 30); i++) {
                    const link = allLinks[i];
                    const rect = link.getBoundingClientRect();
                    const text = link.textContent ? link.textContent.trim() : '';
                    const href = link.href || '';
                    const isVisible = link.offsetParent !== null;
                    const isInViewport = (
                        rect.top >= 0 &&
                        rect.left >= 0 &&
                        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                    );
                    
                    // Проверяем элементы, которые могут быть в правой колонке
                    if (text.includes('Мои') || text.includes('эксперт') || text.includes('уведомл') || 
                        text.includes('личн') || text.includes('бонус') || text.includes('модер')) {
                        rightColumnLinks.push({
                            index: i,
                            text: text,
                            href: href,
                            visible: isVisible,
                            inViewport: isInViewport,
                            rect: {
                                top: rect.top,
                                left: rect.left,
                                bottom: rect.bottom,
                                right: rect.right
                            }
                        });
                    }
                }
                
                return {
                    totalLinks: allLinks.length,
                    rightColumnLinks: rightColumnLinks,
                    scrollPosition: {
                        x: window.scrollX,
                        y: window.scrollY
                    }
                };
            """)
            
            print(f"   Всего ссылок меню: {js_result['totalLinks']}")
            print(f"   Позиция прокрутки: X={js_result['scrollPosition']['x']}, Y={js_result['scrollPosition']['y']}")
            
            if js_result['rightColumnLinks']:
                print(f"   Найденные элементы правой колонки:")
                for item in js_result['rightColumnLinks']:
                    status = "_VISIBLE_" if item['visible'] else "_HIDDEN_"
                    viewport = "_IN_VIEWPORT_" if item['inViewport'] else "_OUT_OF_VIEWPORT_"
                    print(f"     [{item['index']}] {status} {viewport} '{item['text']}' -> {item['href']}")
                    print(f"           Позиция: top={item['rect']['top']:.1f}, left={item['rect']['left']:.1f}")
            else:
                print("   Элементы правой колонки не найдены")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            page.close()
            browser.close()
            print(f"\n🏁 Диагностика завершена")


if __name__ == "__main__":
    debug_right_column()
