"""
Отладочный скрипт для проверки доступности элементов формы на странице bii.by/buy.
Поможет выяснить, почему форма не заполняется.
"""
from playwright.sync_api import sync_playwright
import time

def debug_page_elements():
    """
    Открывает страницу и проверяет доступность всех элементов формы.
    Выводит подробную информацию о каждом элементе для диагностики.
    """
    with sync_playwright() as p:
        # Запускаем браузер с теми же настройками, что и в тестах
        browser = p.chromium.launch(
            headless=False,  # Видимый режим для наблюдения
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-automation",
                "--no-sandbox"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()
        
        print("🔍 Открываем страницу bii.by/buy...")
        
        # Пробуем несколько стратегий загрузки страницы
        page_loaded = False
        strategies = [
            ('load', 60000),
            ('domcontentloaded', 45000),
            ('commit', 30000)
        ]
        
        for wait_until, timeout in strategies:
            try:
                print(f"  Попытка загрузки с wait_until='{wait_until}', timeout={timeout}ms...")
                page.goto("https://bii.by/buy#buy-form", wait_until=wait_until, timeout=timeout)
                page_loaded = True
                print(f"  ✅ Страница загружена с настройкой '{wait_until}'")
                break
            except Exception as e:
                print(f"  ⚠️ Попытка с '{wait_until}' не удалась: {e}")
                continue
        
        if not page_loaded:
            print("  ❌ Все попытки загрузки не удались. Завершаем отладку.")
            browser.close()
            return
        
        # Ждем дополнительное время для полной загрузки контента
        print("  ⏳ Ждем полную загрузку контента...")
        time.sleep(5)
        
        print(f"✅ Страница загружена: {page.url}")
        
        # Проверяем каждый элемент формы
        selectors_to_check = {
            "ФИО": "#request_fio",
            "Телефон": "#request_phone", 
            "Компания": "#request_company",
            "Должность": "#request_position",
            "Email": "#request_mail",
            "Промокод": "#request_promo",
            "Согласие": "#request_agree",
            "Политика": "#request_agree_pol",
            "Кнопка отправки": "#request-send"
        }
        
        print("\n🔍 Проверяем элементы формы:")
        
        for field_name, selector in selectors_to_check.items():
            try:
                element = page.locator(selector)
                is_visible = element.is_visible()
                is_enabled = element.is_enabled() if is_visible else False
                count = element.count()
                
                status = "✅" if is_visible and is_enabled else "❌"
                print(f"  {status} {field_name:12} ({selector:20}): visible={is_visible}, enabled={is_enabled}, count={count}")
                
                if count == 0:
                    print(f"      ⚠️  Элемент не найден! Попробуем альтернативные селекторы...")
                    # Попробуем найти похожие элементы
                    field_lower = field_name.lower()
                    alt_selectors = [
                        f"input[name*='{field_lower}']",
                        f"input[id*='{field_lower}']",
                        f"input[placeholder*='{field_name}']"
                    ]
                    
                    for alt_selector in alt_selectors:
                        alt_count = page.locator(alt_selector).count()
                        if alt_count > 0:
                            print(f"      🔍 Найден альтернативный селектор: {alt_selector} (count={alt_count})")
                            break
                            
            except Exception as e:
                print(f"  ❌ {field_name:12}: ОШИБКА - {e}")
        
        # Дополнительно проверим все формы на странице
        print("\n🔍 Все формы на странице:")
        forms = page.locator("form").all()
        for i, form in enumerate(forms):
            form_id = form.get_attribute("id") or "без id"
            form_class = form.get_attribute("class") or "без класса"
            print(f"  Форма {i+1}: id='{form_id}', class='{form_class}'")
        
        # Проверим все инпуты на странице
        print("\n🔍 Все поля ввода на странице:")
        inputs = page.locator("input").all()
        for i, inp in enumerate(inputs[:10]):  # Показываем первые 10
            inp_id = inp.get_attribute("id") or "без id"
            inp_name = inp.get_attribute("name") or "без name"
            inp_type = inp.get_attribute("type") or "text"
            inp_placeholder = inp.get_attribute("placeholder") or "без placeholder"
            print(f"  Поле {i+1}: id='{inp_id}', name='{inp_name}', type='{inp_type}', placeholder='{inp_placeholder}'")
        
        print("\n⏳ Оставляем браузер открытым на 30 секунд для ручной проверки...")
        time.sleep(30)
        
        browser.close()
        print("\n✅ Отладка завершена")

if __name__ == "__main__":
    debug_page_elements()
