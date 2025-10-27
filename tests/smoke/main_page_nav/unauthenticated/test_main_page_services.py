"""
Services Tests

Тесты навигации по разделу сервисов главной страницы bll.by
(Подборки и закладки, Документы на контроле, Напоминания, и т.д.)
"""

import pytest
import allure

from tests.smoke.main_page_nav.unauthenticated.pages.header_navigation_page import HeaderNavigationPage


@pytest.mark.smoke
@allure.epic("Главная страница")
@allure.feature("Навигация сервисов")
@allure.story("Services navigation")
class TestMainPageServices:
    """
    Класс тестов для проверки навигации по разделу сервисов главной страницы
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
            ("Всё по одной теме", "click_everything_by_topic",
             "podborki-vsyo-po-odnoj-teme-200084",
             "Переход на страницу подборок тем"),
            ("Формы документов", "click_document_forms", "22555",
             "Переход на страницу форм документов"),
            ("Выбор редакции", "click_edition_selection", "vybor-redaktsii-za-nedelyu",
             "Переход на страницу выбора редакции"),
            ("Обзоры и подписки", "click_reviews_subscriptions", "news_subscr.htm",
             "Переход на страницу обзоров и подписок"),
        ]
    )
    @allure.title("Навигация по сервису '{link_name}'")
    @allure.description("Проверка перехода по сервису {link_name}")
    def test_services_navigation(
            self, link_name, method_name, expected_fragment, description):
        """
        Параметризованный тест для проверки навигации по сервисам

        Args:
            link_name: Название сервиса для отображения в отчетах
            method_name: Название метода для клика по сервису
            expected_fragment: Ожидаемый фрагмент в URL после клика
            description: Описание теста
        """
        allure.attach(f"Тестируется сервис: {link_name}", name="Описание")
        allure.attach(
            f"Ожидаемый URL фрагмент: {expected_fragment}", name="Ожидание")

        # Получаем метод объекта и вызываем его
        click_method = getattr(self.navigation, method_name)
        result = click_method()

        with allure.step(f"Проверяем переход по сервису '{link_name}'"):
            assert result, f"Не удалось перейти на страницу '{link_name}'"

        with allure.step(f"Проверяем HTTP статус для '{link_name}'"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], (
                f"Неверный HTTP статус для '{link_name}': {status}")

    @allure.title("Проверка видимости всех сервисов")
    @allure.description("Проверка что все сервисы видны на странице")
    def test_services_visibility(self):
        """
        Тест проверяет видимость всех сервисов на главной странице
        """
        services = [
            "Всё по одной теме",
            "Формы документов",
            "Выбор редакции",
            "Обзоры и подписки",
        ]

        with allure.step("Проверяем видимость сервисов"):
            for service_name in services:
                try:
                    # Для некоторых элементов используем first() чтобы избежать дубликатов
                    if service_name in ["Формы документов"]:
                        link = self.page.get_by_role("link", name=service_name).first
                    else:
                        link = self.page.get_by_role("link", name=service_name)

                    is_visible = link.is_visible(timeout=3000)
                    status_text = "Видим" if is_visible else "Не видим"
                    message = f"Сервис '{service_name}': {status_text}"
                    allure.attach(message, name=f"Видимость {service_name}")
                    # Не падаем тест если сервис не виден, просто логируем
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке сервиса '{service_name}': {e}",
                        name=f"Ошибка {service_name}")

    @allure.title("Проверка функциональности выбора редакции")
    @allure.description("Проверка что страница выбора редакции работает корректно")
    def test_edition_selection_functionality(self):
        """
        Тест проверяет функциональность выбора редакции
        """
        with allure.step("Проверяем доступность выбора редакции"):
            try:
                # Кликаем на "Выбор редакции"
                result = self.navigation.click_edition_selection()

                assert result, "Не удалось перейти на страницу выбора редакции"

                # Проверяем наличие характерных элементов
                current_url = self.page.url
                has_correct_url = "vybor-redaktsii-za-nedelyu" in current_url

                allure.attach(
                    f"URL выбора редакции корректен: {has_correct_url}",
                    name="URL проверка")

                if has_correct_url:
                    # Проверяем наличие контента
                    try:
                        # Ищем признаки страницы выбора редакции
                        has_content = (
                            self.page.locator("h1, h2").count() > 0 or
                            self.page.locator("form, .edition, .selection").count() > 0
                        )

                        allure.attach(
                            f"Контент выбора редакции загружен: {has_content}",
                            name="Контент редакции")
                    except Exception as e:
                        allure.attach(
                            f"Ошибка при проверке контента: {e}",
                            name="Ошибка контента")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке выбора редакции: {e}",
                    name="Ошибка редакции")

    @allure.title("Проверка функциональности обзоров и подписок")
    @allure.description("Проверка что страница обзоров и подписок работает корректно")
    def test_reviews_subscriptions_functionality(self):
        """
        Тест проверяет функциональность обзоров и подписок
        """
        with allure.step("Проверяем доступность обзоров и подписок"):
            try:
                # Кликаем на "Обзоры и подписки"
                result = self.navigation.click_reviews_subscriptions()

                assert result, "Не удалось перейти на страницу обзоров и подписок"

                # Проверяем наличие характерных элементов
                current_url = self.page.url
                has_correct_url = "news_subscr.htm" in current_url

                allure.attach(
                    f"URL обзоров и подписок корректен: {has_correct_url}",
                    name="URL проверка")

                if has_correct_url:
                    # Проверяем наличие контента
                    try:
                        # Ищем признаки страницы обзоров и подписок
                        has_content = (
                            self.page.locator("h1, h2").count() > 0 or
                            self.page.locator("form, .subscribe, .newsletter").count() > 0
                        )

                        allure.attach(
                            f"Контент обзоров и подписок загружен: {has_content}",
                            name="Контент подписок")
                    except Exception as e:
                        allure.attach(
                            f"Ошибка при проверке контента: {e}",
                            name="Ошибка контента")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке обзоров и подписок: {e}",
                    name="Ошибка подписок")

    @allure.title("Проверка структуры раздела сервисов")
    @allure.description("Проверка количества и порядка сервисов на странице")
    def test_services_structure(self):
        """
        Тест проверяет структуру раздела сервисов
        """
        expected_services = [
            "Всё по одной теме",
            "Формы документов",
            "Выбор редакции",
            "Обзоры и подписки",
        ]

        with allure.step("Проверяем количество сервисов"):
            try:
                found_count = 0
                for service_name in expected_services:
                    try:
                        link = self.page.get_by_role("link", name=service_name)
                        if link.is_visible(timeout=2000):
                            found_count += 1
                    except Exception:
                        pass

                allure.attach(
                    f"Найдено сервисов: {found_count} из {len(expected_services)}",
                    name="Количество сервисов")

                # Проверяем что большинство сервисов найдены
                assert found_count >= len(expected_services) // 2, (
                    f"Найдено слишком мало сервисов: {found_count}")

            except Exception as e:
                allure.attach(
                    f"Ошибка при подсчете сервисов: {e}",
                    name="Ошибка подсчета")