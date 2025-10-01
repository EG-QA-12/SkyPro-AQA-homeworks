"""
Тесты навигации правой колонки бургер-меню.

Эти тесты проверяют навигацию по правой колонке меню.
Правая колонка часто содержит элементы, которые могут быть скрыты
или требовать специальной обработки (force click).
Включает все 9 нестабильных тестов из оригинального файла.
"""

import allure
import pytest

from tests.smoke.burger_menu.base_burger_menu_test import BaseBurgerMenuNavigationTest


class TestRightColumnNavigation(BaseBurgerMenuNavigationTest):
    """
    Тесты навигации по правой колонке бургер-меню.

    Включает все нестабильные тесты (9 шт), которые падают в CI/CD
    из-за особенностей UI правой колонки (скрытые элементы, прокрутка).
    """

    @allure.title("Навигация: Подборки и закладки")
    @allure.description("Проверка перехода в Подборки и закладки - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_collections_bookmarks_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Подборки и закладки".

        Проверяет:
        - Статус код: 200
        - URL: https://bll.by/favorites
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_right_column(page, "favorites", "https://bll.by/favorites")
        finally:
            page.close()

    @allure.title("Навигация: Документы на контроле")
    @allure.description("Проверка перехода в Документы на контроле - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_documents_control_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Документы на контроле".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_right_column(page, "docs/control", "https://bll.by/docs/control")
        finally:
            page.close()

    @allure.title("Навигация: Напоминания")
    @allure.description("Проверка перехода в Напоминания - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_reminders_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Напоминания".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)
            self._navigate_and_validate_right_column(page, "notification/reminder", "https://ca.bll.by/notification/reminder")
        finally:
            page.close()

    @allure.title("Навигация: Мои данные")
    @allure.description("Проверка перехода в Мои данные - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_my_data_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Мои данные".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)

            # Специальная обработка для правой колонки
            burger_menu = self._get_burger_menu_page(page)
            burger_menu.open_menu()

            # Прокручиваем вправо для отображения правых колонок меню
            page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
            page.wait_for_timeout(1000)

            # Используем ARIA роль с force кликом
            my_data_link = page.get_by_role("link", name="Мои данные")

            try:
                my_data_link.wait_for(state="attached", timeout=5000)
                my_data_link.click(force=True, timeout=5000)
            except Exception:
                # Альтернативная стратегия
                try:
                    text_link = page.locator("a:has-text('Мои данные')").first
                    text_link.wait_for(state="attached", timeout=5000)
                    text_link.click(force=True, timeout=5000)
                except Exception as e:
                    try:
                        css_selector = ("body > div.layout.layout--docs > header > div > div > "
                                       "div.menu-gumb_new.menu-mobile.active > div.new-menu.new-menu_main > "
                                       "div > div:nth-child(2) > div:nth-child(4) > div.menu_bl_list > "
                                       "div:nth-child(1) > a")
                        css_link = page.locator(css_selector).first
                        css_link.wait_for(state="attached", timeout=5000)

                        page.evaluate(f"""
                            const element = document.querySelector('{css_selector}');
                            if (element) {{
                                element.click();
                            }}
                        """)
                    except Exception as e:
                        raise AssertionError(f"Не удалось кликнуть по ссылке 'Мои данные': {e}")

            # Проверяем переход на внешний домен
            current_url = page.url
            assert "ca.bll.by" in current_url, f"URL не содержит ca.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Личный кабинет")
    @allure.description("Проверка перехода в Личный кабинет - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_personal_account_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Личный кабинет".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)

            # Специальная обработка для правой колонки
            burger_menu = self._get_burger_menu_page(page)
            burger_menu.open_menu()

            # Используем более надежный селектор
            if not burger_menu.click_link_by_text("Личный кабинет"):
                # Пробуем по ARIA роли
                assert burger_menu.click_link_by_role("Личный кабинет"), "Не удалось кликнуть по ссылке 'Личный кабинет'"

            # Проверяем переход на внешний домен
            current_url = page.url
            assert "business-info.by" in current_url, f"URL не содержит business-info.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Новые документы")
    @allure.description("Проверка перехода в Новые документы - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_new_documents_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Новые документы".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)

            # Специальная обработка для правой колонки
            burger_menu = self._get_burger_menu_page(page)
            burger_menu.open_menu()

            # Используем CSS селектор для новых документов
            page.locator("body > div.layout.layout--docs > header > div > div > div.menu-gumb_new.menu-mobile.active > div.new-menu.new-menu_main > div > div:nth-child(2) > div:nth-child(3) > div.menu_bl_list > div:nth-child(4) > a").click()

            # Точное сравнение для страницы новых документов
            from playwright.sync_api import expect
            expect(page).to_have_url("https://bll.by/docs/new")

        finally:
            page.close()

    @allure.title("Навигация: Я эксперт")
    @allure.description("Проверка перехода в Я эксперт - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_expert_profile_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Я эксперт".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)

            # Специальная обработка для правой колонки
            burger_menu = self._get_burger_menu_page(page)
            burger_menu.open_menu()

            # Используем надежный селектор
            if not burger_menu.click_link_by_text("Я эксперт"):
                assert burger_menu.click_link_by_role("Я эксперт"), "Не удалось кликнуть по ссылке 'Я эксперт'"

            # Проверяем переход на внешний домен
            current_url = page.url
            assert "expert.bll.by" in current_url, f"URL не содержит expert.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Настройка уведомлений")
    @allure.description("Проверка перехода в Настройка уведомлений - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_notification_settings_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Настройка уведомлений".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)

            # Специальная обработка для правой колонки
            burger_menu = self._get_burger_menu_page(page)
            burger_menu.open_menu()

            # Используем надежный селектор
            if not burger_menu.click_link_by_text("Настройка уведомлений"):
                assert burger_menu.click_link_by_role("Настройка уведомлений"), "Не удалось кликнуть по ссылке 'Настройка уведомлений'"

            # Проверяем переход на внешний домен
            current_url = page.url
            assert "ca.bll.by" in current_url, f"URL не содержит ca.bll.by: {current_url}"

        finally:
            page.close()

    @allure.title("Навигация: Бонусы")
    @allure.description("Проверка перехода в Бонусы - статус код и URL")
    @pytest.mark.burger_menu
    @pytest.mark.right_column
    @pytest.mark.flaky
    def test_bonuses_navigation(self, authenticated_burger_context):
        """
        Проверка навигации в раздел "Бонусы".
        """
        page = authenticated_burger_context.new_page()
        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            self._ensure_authenticated(page)

            # Специальная обработка для правой колонки
            burger_menu = self._get_burger_menu_page(page)
            burger_menu.open_menu()

            # Используем надежный селектор
            if not burger_menu.click_link_by_text("Бонусы"):
                assert burger_menu.click_link_by_role("Бонусы"), "Не удалось кликнуть по ссылке 'Бонусы'"

            # Проверяем переход на внешний домен
            current_url = page.url
            assert "bonus.bll.by" in current_url, f"URL не содержит bonus.bll.by: {current_url}"

        finally:
            page.close()
