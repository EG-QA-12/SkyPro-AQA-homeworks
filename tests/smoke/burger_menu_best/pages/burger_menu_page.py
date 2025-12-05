"""
Оптимизированный Page Object для бургер-меню.

Простые и надежные методы для навигации по бургер-меню.
"""

import allure
from playwright.sync_api import Page, expect


class BurgerMenuPage:
    """
    Оптимизированный Page Object для работы с бургер-меню.

    Использует проверенные селекторы из рабочего baseline.
    """

    def __init__(self, page: Page):
        self.page = page

    def open_menu(self) -> None:
        """
        Открыть бургер-меню.

        Использует проверенный селектор для стабильной работы.
        """
        with allure.step("Открытие бургер-меню"):
            menu_button = self.page.get_by_role("button", name="меню")
            menu_button.click()
            self.page.wait_for_timeout(500)

    def click_link_by_text(self, link_text: str) -> None:
        """
        Клик по ссылке в бургер-меню по тексту.

        Args:
            link_text: Текст ссылки для клика
        """
        with allure.step(f"Клик по ссылке '{link_text}'"):
            # Используем get_by_role для стабильной работы
            link = self.page.get_by_role("link", name=link_text)
            link.click()
            self.page.wait_for_timeout(500)

    def verify_navigation(self, expected_url_contains: str) -> bool:
        """
        Проверить корректность навигации.

        Args:
            expected_url_contains: Ожидаемая подстрока в URL

        Returns:
            bool: True если URL соответствует ожиданию
        """
        with allure.step("Проверка корректности навигации"):
            current_url = self.page.url
            allure.attach(
                current_url,
                name="Current URL",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # Простая проверка без сложной логики
            return expected_url_contains.lower() in current_url.lower()

    def is_menu_open(self) -> bool:
        """
        Проверить открыто ли бургер-меню.

        Returns:
            bool: True если меню открыто
        """
        with allure.step("Проверка открытия бургер-меню"):
            menu_element = self.page.locator(".menu_bl")
            return menu_element.is_visible()
