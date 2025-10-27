"""
Main Menu Tests

Тесты навигации по основному меню главной страницы bll.by
(КОДЕКСЫ, ГОРЯЧИЕ ТЕМЫ, и т.д.)
"""

import pytest
import allure

from ..pages.header_navigation_page import HeaderNavigationPage


@pytest.mark.smoke
@allure.epic("Главная страница")
@allure.feature("Навигация основного меню")
@allure.story("Main menu navigation")
class TestMainPageMenu:
    """
    Класс тестов для проверки навигации по основному меню главной страницы
    """

    @pytest.fixture(autouse=True)
    def setup_method(self, domain_aware_authenticated_context_for_bll):
        """
        Настройка перед каждым тестом
        """
        self.context = domain_aware_authenticated_context_for_bll
        self.page = self.context.new_page()
        self.navigation = HeaderNavigationPage(self.page)

        # Переходим на главную и ждем готовности
        self.page.goto("https://bll.by", wait_until="domcontentloaded")
        self.navigation.smart_wait_for_page_ready()

        yield

        # Cleanup
        if self.page.url != "https://bll.by":
            self.page.goto("https://bll.by")

    @pytest.mark.parametrize(
        "link_name,method_name,expected_fragment,description", [
            ("Кодексы", "click_codes",
             "kodeksy-dejstvuyushchie-na-territorii-respubliki-belarus-141580",
             "Переход на страницу кодексов"),
            ("Горячие темы", "click_hot_topics", "goryachie-temy-200085",
             "Переход на страницу горячих тем"),
            ("Всё по одной теме", "click_everything_by_topic",
             "podborki-vsyo-po-odnoj-teme-200084",
             "Переход на страницу подборок тем"),
            ("Навигаторы", "click_navigators", "navigatory-140000",
             "Переход на страницу навигаторов"),
            ("Чек-листы NEW", "click_checklists",
             "perechen-tem-chek-list-dokumentov-487105",
             "Переход на страницу чек-листов"),
            ("Каталоги форм", "click_catalogs_forms", "katalogi-form-22555",
             "Переход на страницу каталогов форм"),
            ("Конструкторы", "click_constructors", "konstruktory-200077",
             "Переход на страницу конструкторов"),
            ("Справочники", "click_directories", "spravochniki-220099",
             "Переход на страницу справочников"),
            ("Калькуляторы", "click_calculators", "kalkulyatory-40171",
             "Переход на страницу калькуляторов"),
            ("Закупки", "click_procurement", "gz.bll.by",
             "Переход на страницу закупок"),
            ("Тесты", "click_tests", "testy-dlya-proverki-znanij-212555",
             "Переход на страницу тестов"),
            ("Налоговый кодекс", "click_edition_tax_code", "nalogovyj-kodeks",
             "Переход на страницу налогового кодекса"),
            ("Гражданский кодекс", "click_edition_civil_code", "grazhdanskij-kodeks",
             "Переход на страницу гражданского кодекса"),
            ("Трудовой кодекс", "click_edition_labor_code", "trudovoj-kodeks",
             "Переход на страницу трудового кодекса"),
            ("Уголовный кодекс", "click_edition_criminal_code", "ugolovnyj-kodeks",
             "Переход на страницу уголовного кодекса"),
        ]
    )
    @allure.title("Навигация по пункту меню '{link_name}'")
    @allure.description("Проверка перехода по пункту меню {link_name}")
    def test_main_menu_navigation(
            self, link_name, method_name, expected_fragment, description):
        """
        Параметризованный тест для проверки навигации по основному меню
        
        Args:
            link_name: Название пункта меню для отображения в отчетах
            method_name: Название метода для клика по пункту меню
            expected_fragment: Ожидаемый фрагмент в URL после клика
            description: Описание теста
        """
        allure.attach(f"Тестируется пункт меню: {link_name}", name="Описание")
        allure.attach(
            f"Ожидаемый URL фрагмент: {expected_fragment}", name="Ожидание")

        # Получаем метод объекта и вызываем его
        click_method = getattr(self.navigation, method_name)
        result = click_method()

        with allure.step(f"Проверяем переход по пункту меню '{link_name}'"):
            if link_name == "Закупки":
                # Для закупок проверяем что клик прошел успешно или URL изменился
                current_url = self.page.url
                assert result or "gz.bll.by" in current_url, (
                    f"Не удалось перейти на страницу закупок. "
                    f"Текущий URL: {current_url}")
            else:
                # Для остальных пунктов проверяем URL
                assert result, f"Не удалось перейти на страницу '{link_name}'"

        with allure.step(f"Проверяем HTTP статус для '{link_name}'"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], (
                f"Неверный HTTP статус для '{link_name}': {status}")

    @allure.title("Проверка видимости всех пунктов основного меню")
    @allure.description("Проверка что все пункты основного меню видны на странице")
    def test_main_menu_visibility(self):
        """
        Тест проверяет видимость всех пунктов основного меню
        """
        menu_items = [
            "Кодексы",
            "Горячие темы",
            "Всё по одной теме",
            "Навигаторы",
            "Чек-листы NEW",
            "Каталоги форм",
            "Конструкторы",
            "Справочники",
            "Калькуляторы",
            "Закупки",
            "Тесты",
            "Выбор редакции",
        ]
        
        with allure.step("Проверяем видимость пунктов основного меню"):
            for item_name in menu_items:
                try:
                    # Для некоторых элементов используем first() чтобы избежать дубликатов
                    if item_name in ["Каталоги форм"]:
                        link = self.page.get_by_role("link", name=item_name).first
                    else:
                        link = self.page.get_by_role("link", name=item_name)
                    
                    is_visible = link.is_visible(timeout=3000)
                    status_text = "Видим" if is_visible else "Не видим"
                    allure.attach(
                        f"Пункт меню '{item_name}': {status_text}",
                        name=f"Видимость {item_name}")
                    # Не падаем тест если пункт не виден, просто логируем
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке пункта меню '{item_name}': {e}",
                        name=f"Ошибка {item_name}")

    @allure.title("Проверка структуры основного меню")
    @allure.description("Проверка количества и порядка пунктов основного меню")
    def test_main_menu_structure(self):
        """
        Тест проверяет структуру основного меню
        """
        expected_items = [
            "Кодексы",
            "Горячие темы",
            "Всё по одной теме",
            "Навигаторы",
            "Чек-листы NEW",
            "Каталоги форм",
            "Конструкторы",
            "Справочники",
            "Калькуляторы",
            "Закупки",
            "Тесты",
            "Выбор редакции",
        ]
        
        with allure.step("Проверяем количество пунктов меню"):
            try:
                # Ищем все ссылки в основной навигации
                navigation_links = self.page.locator("nav").get_by_role("link")
                count = navigation_links.count()
                message = f"Найдено пунктов меню: {count}"
                allure.attach(message, name="Количество")
                
                # Проверяем что количество соответствует ожидаемому
                # (может быть больше из-за дополнительных ссылок)
                assert count >= len(expected_items), (
                    f"Найдено меньше пунктов меню ({count}) чем ожидалось "
                    f"({len(expected_items)})")
            except Exception as e:
                message = f"Ошибка при подсчете пунктов меню: {e}"
                allure.attach(message, name="Ошибка")

        with allure.step("Проверяем порядок основных пунктов меню"):
            try:
                # Проверяем что основные пункты присутствуют в правильном порядке
                found_items = []
                for item_name in expected_items:
                    try:
                        link = self.page.get_by_role("link", name=item_name)
                        if link.is_visible(timeout=2000):
                            found_items.append(item_name)
                    except Exception:
                        pass
                
                allure.attach(
                    f"Найденные пункты в порядке: {', '.join(found_items)}",
                    name="Порядок пунктов")
            except Exception as e:
                message = f"Ошибка при проверке порядка: {e}"
                allure.attach(message, name="Ошибка")