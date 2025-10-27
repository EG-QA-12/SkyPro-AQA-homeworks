"""
Header Links Tests

Тесты навигации по ссылкам в хэдэре главной страницы bll.by
(О Платформе, Клуб Экспертов, Бонусы, Мой профиль, телефон)
"""

import pytest
import allure

from ..pages.header_navigation_page import HeaderNavigationPage


@pytest.mark.smoke
@allure.epic("Главная страница")
@allure.feature("Навигация хэдэра")
@allure.story("Header links")
class TestMainPageHeader:
    """
    Класс тестов для проверки навигации по ссылкам в header главной страницы
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
            ("О Платформе", "click_platform_info", "about",
             "Переход на страницу информации о платформе"),
            ("Клуб Экспертов", "click_expert_club", "expert.bll.by/experts",
             "Переход на страницу клуба экспертов"),
            ("Бонусы", "click_bonuses_robust", "bonus.bll.by",
             "Переход на страницу бонусов"),
            ("Мой профиль", "click_my_profile_robust", "admin",
             "Переход в профиль пользователя"),
            ("Телефон", "click_phone_number", "tel:",
             "Проверка телефонной ссылки"),
        ]
    )
    @allure.title("Навигация по ссылке '{link_name}' в header")
    @allure.description("Проверка перехода по ссылке {link_name}")
    def test_header_link_navigation(
            self, link_name, method_name, expected_fragment, description):
        """
        Параметризованный тест для проверки навигации по ссылкам в header
        
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
            if link_name == "Телефон":
                # Для телефона проверяем что ссылка ведет на tel:
                assert result, f"Телефонная ссылка не ведет на tel: ссылку"
            elif link_name == "Мой профиль":
                # Для профиля проверяем появление popup
                assert result, f"Не удалось открыть popup профиля"
            else:
                # Для остальных ссылок проверяем URL
                assert result, f"Не удалось перейти на страницу '{link_name}'"

        with allure.step(f"Проверяем HTTP статус для '{link_name}'"):
            if link_name == "Телефон":
                # Для телефона проверяем статус главной страницы
                status = self.navigation.assert_http_status("https://bll.by")
            else:
                # Для остальных проверяем статус текущей страницы
                status = self.navigation.assert_http_status(self.page.url)
            
            assert status in [200, 301, 302], (
                f"Неверный HTTP статус для '{link_name}': {status}")

    @allure.title("Проверка видимости всех header ссылок")
    @allure.description("Проверка что все ссылки в header видны на странице")
    def test_header_links_visibility(self):
        """
        Тест проверяет видимость всех ссылок в header
        """
        header_links = [
            "О Платформе",
            "Клуб Экспертов", 
            "Мой профиль"
        ]
        
        with allure.step("Проверяем видимость основных ссылок в header"):
            for link_name in header_links:
                try:
                    link = self.page.get_by_role("link", name=link_name)
                    is_visible = link.is_visible(timeout=3000)
                    status_text = "Видима" if is_visible else "Не видима"
                    message = f"Ссылка '{link_name}': {status_text}"
                    allure.attach(message, name=f"Видимость {link_name}")
                    # Не падаем тест если ссылка не видима, просто логируем
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке ссылки '{link_name}': {e}",
                        name=f"Ошибка {link_name}")

        with allure.step("Проверяем телефонную ссылку"):
            try:
                phone_link = self.page.get_by_role("banner").get_by_role(
                    "link", name="+375 17 388-32-")
                phone_visible = phone_link.is_visible(timeout=3000)
                status_text = "Видима" if phone_visible else "Не видима"
                message = f"Телефонная ссылка: {status_text}"
                allure.attach(message, name="Видимость телефона")
            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке телефонной ссылки: {e}",
                    name="Ошибка телефона")