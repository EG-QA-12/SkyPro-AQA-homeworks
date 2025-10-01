"""
Тесты навигации правой колонки бургер-меню.

Эти тесты проверяют навигацию по правой колонке меню.
Правая колонка часто содержит элементы, которые могут быть скрыты
или требовать специальной обработки (force click).
"""

import allure
import pytest

from tests.smoke.burger_menu.base_burger_menu_test import BaseBurgerMenuNavigationTest


class TestRightColumnNavigation(BaseBurgerMenuNavigationTest):
    """
    Тесты навигации по правой колонке бургер-меню.

    Включает тесты для элементов правой колонки, которые могут быть
    нестабильными из-за особенностей UI (скрытые элементы, прокрутка).
    """

    @allure.title("Навигация: Напоминания")
    @allure.description("Проверка перехода в Напоминания - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_reminders_navigation(self, burger_menu_page):
        """
        Проверка навигации в раздел "Напоминания".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/reminders
        """
        self._navigate_and_validate_right_column(
            burger_menu_page,
            "Напоминания",
            "https://ca.bll.by/notification/reminder"
        )

    @allure.title("Навигация: Закладки")
    @allure.description("Проверка перехода в Закладки - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_bookmarks_navigation(self, burger_menu_page):
        """
        Проверка навигации в раздел "Закладки".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/favorites
        """
        self._navigate_and_validate_right_column(
            burger_menu_page,
            "Закладки",
            "https://bll.by/favorites"
        )

    @allure.title("Навигация: Мои данные")
    @allure.description("Проверка перехода в Мои данные - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_my_data_navigation(self, burger_menu_page):
        """
        Проверка навигации в раздел "Мои данные".

        Проверяет:
        - Статус код: 200
        - URL: https://ca.bll.by/user/profile
        """
        self._navigate_and_validate_right_column(
            burger_menu_page,
            "Мои данные",
            "https://ca.bll.by/user/profile"
        )

    @allure.title("Навигация: Личный кабинет")
    @allure.description("Проверка перехода в Личный кабинет - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_personal_account_navigation(self, burger_menu_page):
        """
        Проверка навигации в раздел "Личный кабинет".

        Проверяет:
        - Статус код: 200
        - URL: https://business-info.by/pc
        """
        self._navigate_and_validate_right_column(
            burger_menu_page,
            "Личный кабинет",
            "https://business-info.by/pc"
        )

    @allure.title("Навигация: Новые документы")
    @allure.description("Проверка перехода в Новые документы - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_new_documents_navigation(self, burger_menu_page):
        """
        Проверка навигации в раздел "Новые документы".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/docs/new
        """
        self._navigate_and_validate_right_column(
            burger_menu_page,
            "Новые документы",
            "https://bll.by/docs/new"
        )

    @allure.title("Навигация: Настройки уведомлений")
    @allure.description("Проверка перехода в Настройки уведомлений - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_notification_settings_navigation(self, burger_menu_page):
        """
        Проверка навигации в раздел "Настройки уведомлений".

        Проверяет:
        - Статус код: 200
        - URL: https://ca.bll.by/notification/settings
        """
        self._navigate_and_validate_right_column(
            burger_menu_page,
            "Настройка уведомлений",
            "https://ca.bll.by/notification/settings"
        )

    @allure.title("Навигация: Я эксперт")
    @allure.description("Проверка перехода в Я эксперт - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_expert_profile_navigation(self, burger_menu_page):
        """
        Проверка навигации в раздел "Я эксперт".

        Проверяет:
        - Статус код: 200
        - URL: https://expert.bll.by/user/expert
        """
        self._navigate_and_validate_right_column(
            burger_menu_page,
            "Я эксперт",
            "https://expert.bll.by/user/expert"
        )

    @allure.title("Навигация: Бонусы")
    @allure.description("Проверка перехода в Бонусы - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_bonuses_navigation(self, burger_menu_page):
        """
        Проверка навигации в раздел "Бонусы".

        Проверяет:
        - Статус код: 200
        - URL: https://bonus.bll.by/bonus
        """
        self._navigate_and_validate_right_column(
            burger_menu_page,
            "Бонусы",
            "https://bonus.bll.by/bonus"
        )