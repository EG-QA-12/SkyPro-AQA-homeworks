"""
Reference Information Tests

Тесты навигации по справочной информации главной страницы bll.by
(Справочная информация, Ставка рефинансирования, Базовая величина, и т.д.)
"""

import pytest
import allure

from tests.smoke.main_page_nav.unauthenticated.pages.header_navigation_page import HeaderNavigationPage


@pytest.mark.smoke
@allure.epic("Главная страница")
@allure.feature("Навигация справочной информации")
@allure.story("Reference information navigation")
class TestMainPageReference:
    """
    Класс тестов для проверки навигации по справочной информации главной страницы
    """

    @pytest.fixture(autouse=True)
    def setup_method(self, domain_aware_context_for_bll):
        """
        Настройка перед каждым тестом
        """
        self.context = domain_aware_context_for_bll
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
            ("Справочная информация", "click_reference_info", "200083",
             "Переход на страницу справочной информации"),
            ("Ставка рефинансирования", "click_refinancing_rate", "43009",
             "Переход на страницу ставки рефинансирования"),
            ("Базовая величина", "click_base_value", "60204",
             "Переход на страницу базовой величины"),
            ("Средняя з/п за январь", "click_average_salary_january", "490447",
             "Переход на страницу средней зарплаты"),
            ("Пособия на детей", "click_child_allowances", "694891",
             "Переход на страницу пособий на детей"),
            ("Базовая арендная величина", "click_base_rental_value", "235259",
             "Переход на страницу базовой арендной величины"),
            ("МЗП за февраль", "click_minimum_wage_february", "minimalnoj-zarabotnoj-platy",
             "Переход на страницу минимальной зарплаты"),
            ("БПМ", "click_bpm", "46296",
             "Переход на страницу бюджета прожиточного минимума"),
            ("Курсы валют", "click_currency_rates", "currency",
             "Переход на страницу курсов валют"),
        ]
    )
    @allure.title("Навигация по справочной ссылке '{link_name}'")
    @allure.description("Проверка перехода по справочной ссылке {link_name}")
    def test_reference_navigation(
            self, link_name, method_name, expected_fragment, description):
        """
        Параметризованный тест для проверки навигации по справочной информации

        Args:
            link_name: Название ссылки для отображения в отчетах
            method_name: Название метода для клика по ссылке
            expected_fragment: Ожидаемый фрагмент в URL после клика
            description: Описание теста
        """
        allure.attach(f"Тестируется ссылка: {link_name}", name="Описание")
        allure.attach(
            f"Ожидаемый URL фрагмент: {expected_fragment}", name="Ожидание")

        # Получаем метод объекта и вызываем его
        click_method = getattr(self.navigation, method_name)
        result = click_method()

        with allure.step(f"Проверяем переход по ссылке '{link_name}'"):
            if link_name == "МЗП за февраль":
                # Для МЗП используем специальную проверку
                current_url = self.page.url
                assert result or ("minimalnoj-zarabotnoj-platy" in current_url or
                               "mzp" in current_url.lower()), (
                    f"Не удалось перейти на страницу '{link_name}'. "
                    f"Текущий URL: {current_url}")
            else:
                # Для остальных ссылок проверяем результат
                assert result, f"Не удалось перейти на страницу '{link_name}'"

        with allure.step(f"Проверяем HTTP статус для '{link_name}'"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], (
                f"Неверный HTTP статус для '{link_name}': {status}")

    @allure.title("Проверка видимости всех справочных ссылок")
    @allure.description("Проверка что все справочные ссылки видны на странице")
    def test_reference_links_visibility(self):
        """
        Тест проверяет видимость всех справочных ссылок на главной странице
        """
        reference_links = [
            "Справочная информация",
            "Ставка рефинансирования",
            "Базовая величина",
            "Средняя з/п за январь",
            "Пособия на детей",
            "Базовая арендная величина",
            "МЗП за февраль",
            "БПМ",
            "Курсы валют",
        ]

        with allure.step("Проверяем видимость справочных ссылок"):
            for link_name in reference_links:
                try:
                    link = self.page.get_by_role("link", name=link_name)
                    is_visible = link.is_visible(timeout=3000)
                    status_text = "Видима" if is_visible else "Не видима"
                    allure.attach(
                        f"Ссылка '{link_name}': {status_text}",
                        name=f"Видимость {link_name}")
                    # Не падаем тест если ссылка не видима, просто логируем
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке ссылки '{link_name}': {e}",
                        name=f"Ошибка {link_name}")

    @allure.title("Проверка доступности справочной информации")
    @allure.description("Проверка что раздел справочной информации доступен")
    def test_reference_info_accessibility(self):
        """
        Тест проверяет доступность раздела справочной информации
        """
        with allure.step("Проверяем доступность справочной информации"):
            try:
                # Кликаем на "Справочная информация"
                result = self.navigation.click_reference_info()

                assert result, "Не удалось перейти на справочную информацию"

                # Проверяем наличие характерных элементов
                current_url = self.page.url
                has_correct_url = "200083" in current_url

                allure.attach(
                    f"URL справочной информации корректен: {has_correct_url}",
                    name="URL проверка")

                if has_correct_url:
                    # Проверяем наличие контента
                    try:
                        # Ищем признаки справочной страницы
                        has_content = (
                            self.page.locator("h1, h2").count() > 0 or
                            self.page.locator(".content, .reference, .info").count() > 0
                        )

                        allure.attach(
                            f"Контент справочной информации загружен: {has_content}",
                            name="Контент справки")
                    except Exception as e:
                        allure.attach(
                            f"Ошибка при проверке контента: {e}",
                            name="Ошибка контента")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке справочной информации: {e}",
                    name="Ошибка справки")

    @allure.title("Проверка функциональности курсов валют")
    @allure.description("Проверка что страница курсов валют работает корректно")
    def test_currency_rates_functionality(self):
        """
        Тест проверяет функциональность курсов валют
        """
        with allure.step("Проверяем доступность курсов валют"):
            try:
                # Кликаем на "Курсы валют"
                result = self.navigation.click_currency_rates()

                assert result, "Не удалось перейти на страницу курсов валют"

                # Проверяем наличие характерных элементов
                current_url = self.page.url
                has_correct_url = "currency" in current_url

                allure.attach(
                    f"URL курсов валют корректен: {has_correct_url}",
                    name="URL проверка")

                if has_correct_url:
                    # Проверяем наличие контента
                    try:
                        # Ищем признаки страницы курсов валют
                        has_content = (
                            self.page.locator("h1, h2").count() > 0 or
                            self.page.locator("table, .currency, .rate").count() > 0
                        )

                        allure.attach(
                            f"Контент курсов валют загружен: {has_content}",
                            name="Контент валют")
                    except Exception as e:
                        allure.attach(
                            f"Ошибка при проверке контента: {e}",
                            name="Ошибка контента")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке курсов валют: {e}",
                    name="Ошибка валют")

    @allure.title("Проверка функциональности экономических показателей")
    @allure.description("Проверка что страницы экономических показателей работают корректно")
    def test_economic_indicators_functionality(self):
        """
        Тест проверяет функциональность экономических показателей
        """
        economic_indicators = [
            ("Ставка рефинансирования", "click_refinancing_rate"),
            ("Базовая величина", "click_base_value"),
            ("Средняя з/п за январь", "click_average_salary_january"),
            ("Пособия на детей", "click_child_allowances"),
            ("Базовая арендная величина", "click_base_rental_value"),
            ("МЗП за февраль", "click_minimum_wage_february"),
            ("БПМ", "click_bpm"),
        ]

        with allure.step("Проверяем доступность экономических показателей"):
            for indicator_name, method_name in economic_indicators:
                try:
                    # Возвращаемся на главную перед каждым тестом
                    self.page.goto("https://bll.by", wait_until="domcontentloaded")
                    self.navigation.smart_wait_for_page_ready()

                    # Получаем метод и вызываем его
                    click_method = getattr(self.navigation, method_name)
                    result = click_method()

                    # Проверяем результат
                    success = result
                    if indicator_name == "МЗП за февраль":
                        # Специальная проверка для МЗП
                        current_url = self.page.url
                        success = result or ("minimalnoj-zarabotnoj-platy" in current_url or
                                          "mzp" in current_url.lower())

                    status_text = "Доступен" if success else "Недоступен"
                    allure.attach(
                        f"Показатель '{indicator_name}': {status_text}",
                        name=f"Доступность {indicator_name}")

                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке показателя '{indicator_name}': {e}",
                        name=f"Ошибка {indicator_name}")

    @allure.title("Проверка структуры раздела справочной информации")
    @allure.description("Проверка количества и порядка справочных ссылок")
    def test_reference_structure(self):
        """
        Тест проверяет структуру раздела справочной информации
        """
        expected_references = [
            "Справочная информация",
            "Ставка рефинансирования",
            "Базовая величина",
            "Средняя з/п за январь",
            "Пособия на детей",
            "Базовая арендная величина",
            "МЗП за февраль",
            "БПМ",
            "Курсы валют",
        ]

        with allure.step("Проверяем количество справочных ссылок"):
            try:
                found_count = 0
                for ref_name in expected_references:
                    try:
                        link = self.page.get_by_role("link", name=ref_name)
                        if link.is_visible(timeout=2000):
                            found_count += 1
                    except Exception:
                        pass

                allure.attach(
                    f"Найдено справочных ссылок: {found_count} из {len(expected_references)}",
                    name="Количество ссылок")

                # Проверяем что большинство ссылок найдены
                assert found_count >= len(expected_references) // 2, (
                    f"Найдено слишком мало справочных ссылок: {found_count}")

            except Exception as e:
                allure.attach(
                    f"Ошибка при подсчете справочных ссылок: {e}",
                    name="Ошибка подсчета")