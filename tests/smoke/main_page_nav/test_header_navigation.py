"""
Header Navigation Tests

Тесты навигации хэдэра главной страницы bll.by
"""

import pytest
import allure

from .pages.header_navigation_page import HeaderNavigationPage


@pytest.mark.smoke
@allure.epic("Главная страница")
@allure.feature("Навигация хэдэра")
@allure.story("Header navigation")
class TestHeaderNavigation:
    """
    Класс тестов для проверки навигации в header главной страницы
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

    @allure.title("Клик по логотипу Бизнес-Инфо")
    @allure.description("Проверка что логотип ведет на главную страницу")
    def test_main_logo_click(self):
        """Тест клика по логотипу"""
        allure.attach("Тестируется кликовыйсть логотипа 'Бизнес-Инфо'", name="Описание")

        result = self.navigation.click_logo_business_info()

        with allure.step("Проверяем что остались на главной странице"):
            assert result, "Логотип не ведет на главную страницу"

        with allure.step("Проверяем HTTP статус главной страницы"):
            status = self.navigation.assert_http_status("https://bll.by")
            assert status in [200, 301, 302], f"Неверный HTTP статус главной страницы: {status}"

    @allure.title("Клик по телефону в header")
    @allure.description("Проверка что телефон ведет на tel: ссылку")
    def test_phone_link_click(self):
        """Тест клика по телефону"""
        allure.attach("Тестируется телефонная ссылка +375 17 388-32-52", name="Описание")

        result = self.navigation.click_phone_number()

        with allure.step("Проверяем что ссылка ведет на tel:"):
            assert result, "Телефон не ведет на tel: ссылку"

        with allure.step("Проверяем HTTP статус главной страницы"):
            status = self.navigation.assert_http_status("https://bll.by")
            assert status in [200, 301, 302], f"Неверный HTTP статус главной страницы: {status}"

    @allure.title("Навигация 'О платформе'")
    @allure.description("Проверка перехода на страницу информации о платформе")
    def test_platform_info_navigation(self):
        """Тест клика по 'О платформе'"""
        allure.attach("Тестируется переход на https://bll.by/about", name="Описание")

        result = self.navigation.click_platform_info()

        with allure.step("Проверяем переход на страницу about"):
            assert result, "Не удалось перейти на страницу 'О платформе'"

        with allure.step("Проверяем HTTP статус страницы about"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы about: {status}"

    @allure.title("Навигация 'Клуб экспертов'")
    @allure.description("Проверка перехода на страницу клуба экспертов")
    def test_expert_club_navigation(self):
        """Тест клика по 'Клуб экспертов'"""
        allure.attach("Тестируется переход на https://expert.bll.by/experts", name="Описание")

        result = self.navigation.click_expert_club()

        with allure.step("Проверяем переход на expert.bll.by/experts"):
            assert result, "Не удалось перейти на страницу клуба экспертов"

        with allure.step("Проверяем HTTP статус страницы экспертов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы экспертов: {status}"

    @allure.title("Навигация 'Бонусы'")
    @allure.description("Проверка перехода на страницу бонусов с учетом SSO")
    def test_bonuses_navigation(self):
        """Тест клика по 'Бонусы'"""
        allure.attach("Тестируется переход на bonus.bll.by с учетом SSO логина", name="Описание")

        result = self.navigation.click_bonuses()

        with allure.step("Проверяем переход на бонусы или SSO редирект"):
            assert result, "Не удалось перейти на страницу бонусов"

        with allure.step("Проверяем HTTP статус финальной страницы"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы бонусов: {status}"

    @allure.title("Popup профиля пользователя")
    @allure.description("Проверка появления popup профиля с ссылкой на админку")
    def test_my_profile_popup(self):
        """Тест клика по профилю с popup"""
        allure.attach("Тестируется popup профиля с ссылкой на админку", name="Описание")

        result = self.navigation.click_my_profile()

        with allure.step("Проверяем появление popup с админкой"):
            assert result, "Popup профиля с админкой не появился"
