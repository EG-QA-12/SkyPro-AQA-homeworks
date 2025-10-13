"""
Burger Menu Params Pages - Локальная конфигурация.

Локальный conftest.py для пакета pages в burger_menu_params.
Содержит фикстуры и настройки специфичные для Page Objects burger menu.
"""

import pytest
from .burger_menu_page import BurgerMenuPage


@pytest.fixture(scope="function")
def burger_menu_page(page):
    """
    Фикстура для создания экземпляра BurgerMenuPage.

    Args:
        page: Playwright page instance

    Returns:
        BurgerMenuPage: Экземпляр page object для работы с burger menu
    """
    return BurgerMenuPage(page)