"""
Тест для проверки работы элементов меню в headless режиме.

Проверяем разные группы элементов:
1. Левая колонка (документы, справочники и т.д.)
2. Центральная колонка (сообщество, эксперты и т.д.)  
3. Правая колонка (мои данные, настройки и т.д.)
"""
import allure
import pytest
from playwright.sync_api import expect

from tests.e2e.pages.burger_menu_page import BurgerMenuPage


class TestMenuHeadlessCheck:
    """Тесты для проверки работы элементов меню в headless режиме."""

    @allure.title("Проверка элементов левой колонки меню")
    @pytest.mark.burger_menu
    @pytest.mark.ui
    def test_left_column_elements(self, authenticated_burger_context):
        """Проверка элементов левой колонки меню."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")            # Добавляем небольшую паузу для избежания конфликтов
            page.wait_for_timeout(500)

            
            # Добавляем retry механизм для открытия меню
            
            max_retries = 3
            
            for attempt in range(max_retries):
            
                if burger_menu.open_menu():
            
                    break
            
                if attempt < max_retries - 1:
            
                    page.wait_for_timeout(1000)
            
                    page.reload()
            
                else:
            
                    assert False, "Не удалось открыть бургер-меню после нескольких попыток"

            # Проверяем несколько элементов из левой колонки
            left_column_elements = [
                "Новости",
                "Справочная информация", 
                "Кодексы",
                "Чек-листы",
                "Каталоги форм",
                "Словарь"
            ]

            working_elements = []
            failed_elements = []

            for element_text in left_column_elements:
                try:
                    # Прокручиваем влево для отображения левых колонок
                    page.evaluate("window.scrollTo({ left: 0, behavior: 'smooth' });")
                    page.wait_for_timeout(100)
                    
                    element = page.locator(f"a:has-text('{element_text}')")
                    if element.count() > 0 and element.is_visible():
                        working_elements.append(element_text)
                        print(f"✓ Элемент '{element_text}' видим")
                    else:
                        failed_elements.append(element_text)
                        print(f"✗ Элемент '{element_text}' не видим")
                except Exception as e:
                    failed_elements.append(element_text)
                    print(f"✗ Элемент '{element_text}' ошибка: {e}")

            print(f"Работающие элементы левой колонки: {working_elements}")
            print(f"Неработающие элементы левой колонки: {failed_elements}")

            # Проверяем, что хотя бы половина элементов работает
            assert len(working_elements) >= len(left_column_elements) // 2, \
                f"Слишком много неработающих элементов в левой колонке: {failed_elements}"

        finally:
            page.close()

    @allure.title("Проверка элементов центральной колонки меню")
    @pytest.mark.burger_menu
    @pytest.mark.ui
    def test_center_column_elements(self, authenticated_burger_context):
        """Проверка элементов центральной колонки меню."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")            # Добавляем небольшую паузу для избежания конфликтов
            page.wait_for_timeout(500)

            
            # Добавляем retry механизм для открытия меню
            
            max_retries = 3
            
            for attempt in range(max_retries):
            
                if burger_menu.open_menu():
            
                    break
            
                if attempt < max_retries - 1:
            
                    page.wait_for_timeout(1000)
            
                    page.reload()
            
                else:
            
                    assert False, "Не удалось открыть бургер-меню после нескольких попыток"

            # Проверяем элементы из центральной колонки
            center_column_elements = [
                "Поиск в базе документов",
                "Поиск в сообществе", 
                "Проверка контрагента",
                "Задать вопрос",
                "Мои вопросы и ответы",
                "Топики на контроле"
            ]

            working_elements = []
            failed_elements = []

            for element_text in center_column_elements:
                try:
                    # Прокручиваем в центр для отображения центральных колонок
                    page.evaluate("window.scrollTo({ left: 500, behavior: 'smooth' });")
                    page.wait_for_timeout(100)
                    
                    element = page.locator(f"a:has-text('{element_text}')")
                    if element.count() > 0 and element.is_visible():
                        working_elements.append(element_text)
                        print(f"✓ Элемент '{element_text}' видим")
                    else:
                        failed_elements.append(element_text)
                        print(f"✗ Элемент '{element_text}' не видим")
                except Exception as e:
                    failed_elements.append(element_text)
                    print(f"✗ Элемент '{element_text}' ошибка: {e}")

            print(f"Работающие элементы центральной колонки: {working_elements}")
            print(f"Неработающие элементы центральной колонки: {failed_elements}")

            # Проверяем, что хотя бы половина элементов работает
            assert len(working_elements) >= len(center_column_elements) // 2, \
                f"Слишком много неработающих элементов в центральной колонке: {failed_elements}"

        finally:
            page.close()

    @allure.title("Проверка элементов правой колонки меню")
    @pytest.mark.burger_menu
    @pytest.mark.ui
    def test_right_column_elements(self, authenticated_burger_context):
        """Проверка элементов правой колонки меню."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")            # Добавляем небольшую паузу для избежания конфликтов
            page.wait_for_timeout(500)

            
            # Добавляем retry механизм для открытия меню
            
            max_retries = 3
            
            for attempt in range(max_retries):
            
                if burger_menu.open_menu():
            
                    break
            
                if attempt < max_retries - 1:
            
                    page.wait_for_timeout(1000)
            
                    page.reload()
            
                else:
            
                    assert False, "Не удалось открыть бургер-меню после нескольких попыток"

            # Проверяем элементы из правой колонки
            right_column_elements = [
                "Мои данные",
                "Я эксперт",
                "Настройка уведомлений",
                "Личный кабинет",
                "Бонусы",
                "Сообщения от модератора"
            ]

            working_elements = []
            failed_elements = []

            for element_text in right_column_elements:
                try:
                    # Прокручиваем вправо для отображения правых колонок
                    page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
                    page.wait_for_timeout(100)
                    
                    element = page.locator(f"a:has-text('{element_text}')")
                    if element.count() > 0 and element.is_visible():
                        working_elements.append(element_text)
                        print(f"✓ Элемент '{element_text}' видим")
                    else:
                        failed_elements.append(element_text)
                        print(f"✗ Элемент '{element_text}' не видим")
                except Exception as e:
                    failed_elements.append(element_text)
                    print(f"✗ Элемент '{element_text}' ошибка: {e}")

            print(f"Работающие элементы правой колонки: {working_elements}")
            print(f"Неработающие элементы правой колонки: {failed_elements}")

            # Проверяем, что хотя бы половина элементов работает
            assert len(working_elements) >= len(right_column_elements) // 2, \
                f"Слишком много неработающих элементов в правой колонке: {failed_elements}"

        finally:
            page.close()

    @allure.title("Проверка конкретных элементов из каждой группы")
    @pytest.mark.burger_menu
    @pytest.mark.ui
    def test_specific_elements_from_each_group(self, authenticated_burger_context):
        """Проверка конкретных элементов из каждой группы."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")            # Добавляем небольшую паузу для избежания конфликтов
            page.wait_for_timeout(500)

            
            # Добавляем retry механизм для открытия меню
            
            max_retries = 3
            
            for attempt in range(max_retries):
            
                if burger_menu.open_menu():
            
                    break
            
                if attempt < max_retries - 1:
            
                    page.wait_for_timeout(1000)
            
                    page.reload()
            
                else:
            
                    assert False, "Не удалось открыть бургер-меню после нескольких попыток"

            # Тестовые элементы из каждой группы
            test_elements = {
                "Левая колонка - Поиск в базе документов": "Поиск в базе документов",
                "Центральная колонка - Поиск в сообществе": "Поиск в сообществе", 
                "Правая колонка - Мои данные": "Мои данные"
            }

            results = {}

            for group_name, element_text in test_elements.items():
                try:
                    print(f"\nПроверяем элемент '{element_text}' из группы '{group_name}'")
                    
                    # Разные стратегии прокрутки для разных групп
                    if "Левая" in group_name:
                        page.evaluate("window.scrollTo({ left: 0, behavior: 'smooth' });")
                    elif "Центральная" in group_name:
                        page.evaluate("window.scrollTo({ left: 500, behavior: 'smooth' });")
                    else:  # Правая колонка
                        page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
                    
                    page.wait_for_timeout(100)
                    
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
                                print(f"  Найден элемент по стратегии: {strategy}")
                                if element.is_visible():
                                    results[group_name] = {"status": "working", "strategy": strategy}
                                    found = True
                                    print(f"  ✓ Элемент видим")
                                    break
                                else:
                                    results[group_name] = {"status": "exists_but_hidden", "strategy": strategy}
                                    print(f"  ⚠ Элемент существует но скрыт")
                                    found = True
                                    break
                        except Exception:
                            continue
                    
                    if not found:
                        results[group_name] = {"status": "not_found", "strategy": "all"}
                        print(f"  ✗ Элемент не найден")
                        
                except Exception as e:
                    results[group_name] = {"status": "error", "error": str(e)}
                    print(f"  ✗ Ошибка при проверке: {e}")

            # Выводим результаты
            print("\n" + "="*50)
            print("РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
            print("="*50)
            
            working_count = sum(1 for r in results.values() if r["status"] == "working")
            hidden_count = sum(1 for r in results.values() if r["status"] == "exists_but_hidden")
            not_found_count = sum(1 for r in results.values() if r["status"] in ["not_found", "error"])
            
            print(f"Работающие элементы: {working_count}")
            print(f"Скрытые элементы: {hidden_count}")  
            print(f"Ненайденные/ошибочные элементы: {not_found_count}")
            
            for group, result in results.items():
                status_symbol = {
                    "working": "✓",
                    "exists_but_hidden": "⚠", 
                    "not_found": "✗",
                    "error": "❌"
                }.get(result["status"], "?")
                print(f"  {status_symbol} {group}: {result['status']}")
                
            print("="*50)

        finally:
            page.close()

    @allure.title("Подробная диагностика правой колонки")
    @pytest.mark.burger_menu
    @pytest.mark.ui
    def test_right_column_detailed_diagnostic(self, authenticated_burger_context):
        """Подробная диагностика элементов правой колонки."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")            # Добавляем небольшую паузу для избежания конфликтов
            page.wait_for_timeout(500)

            
            # Добавляем retry механизм для открытия меню
            
            max_retries = 3
            
            for attempt in range(max_retries):
            
                if burger_menu.open_menu():
            
                    break
            
                if attempt < max_retries - 1:
            
                    page.wait_for_timeout(1000)
            
                    page.reload()
            
                else:
            
                    assert False, "Не удалось открыть бургер-меню после нескольких попыток"

            print("\n=== ДЕТАЛЬНАЯ ДИАГНОСТИКА ПРАВОЙ КОЛОНКИ ===")
            
            # Прокручиваем вправо
            page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
            page.wait_for_timeout(500)
            
            # Проверяем конкретный элемент "Мои данные"
            print("\n1. Проверка элемента 'Мои данные':")
            
            # Стратегия 1: Поиск по точному тексту
            try:
                my_data_exact = page.locator("a:has-text('Мои данные')")
                print(f"   Поиск по точному тексту: найдено {my_data_exact.count()} элементов")
                if my_data_exact.count() > 0:
                    print(f"   Видимость: {my_data_exact.is_visible()}")
                    print(f"   href: {my_data_exact.get_attribute('href')}")
            except Exception as e:
                print(f"   Ошибка поиска по точному тексту: {e}")
            
            # Стратегия 2: Поиск по частичному тексту
            try:
                my_data_partial = page.locator("a:has-text('Мои')")
                print(f"   Поиск по частичному тексту: найдено {my_data_partial.count()} элементов")
            except Exception as e:
                print(f"   Ошибка поиска по частичному тексту: {e}")
            
            # Стратегия 3: Поиск по href
            try:
                my_data_href = page.locator("a[href*='ca.bll.by/user/profile']")
                print(f"   Поиск по href: найдено {my_data_href.count()} элементов")
                if my_data_href.count() > 0:
                    print(f"   Видимость: {my_data_href.is_visible()}")
                    print(f"   Текст: {my_data_href.text_content()}")
            except Exception as e:
                print(f"   Ошибка поиска по href: {e}")
            
            # Стратегия 4: Поиск по классу
            try:
                my_data_class = page.locator("a.menu_item_link")
                print(f"   Поиск по классу menu_item_link: найдено {my_data_class.count()} элементов")
            except Exception as e:
                print(f"   Ошибка поиска по классу: {e}")
            
            # Стратегия 5: JavaScript поиск
            try:
                js_result = page.evaluate("""
                    const elements = document.querySelectorAll('a');
                    let found = [];
                    for (let elem of elements) {
                        const text = elem.textContent || '';
                        const href = elem.href || '';
                        if (text.includes('Мои данные') || href.includes('ca.bll.by/user/profile')) {
                            found.push({
                                text: text.trim(),
                                href: href,
                                visible: elem.offsetParent !== null
                            });
                        }
                    }
                    return found;
                """)
                print(f"   JavaScript поиск нашел {len(js_result)} элементов:")
                for item in js_result:
                    print(f"     - Текст: '{item['text']}', href: '{item['href']}', видим: {item['visible']}")
            except Exception as e:
                print(f"   Ошибка JavaScript поиска: {e}")

            # Проверяем всю структуру меню
            print("\n2. Структура всего меню:")
            try:
                all_links = page.locator("a.menu_item_link")
                total_count = all_links.count()
                print(f"   Всего ссылок с классом menu_item_link: {total_count}")
                
                visible_count = 0
                for i in range(min(10, total_count)):  # Проверяем первые 10 элементов
                    try:
                        link = all_links.nth(i)
                        if link.is_visible():
                            visible_count += 1
                            text = link.text_content().strip()
                            href = link.get_attribute('href')
                            print(f"     [{i}] '{text}' -> {href}")
                    except Exception:
                        continue
                        
                print(f"   Видимых ссылок: {visible_count}")
                
            except Exception as e:
                print(f"   Ошибка при проверке структуры: {e}")

        finally:
            page.close()
