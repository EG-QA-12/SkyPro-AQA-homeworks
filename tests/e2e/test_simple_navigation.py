"""
Простой тест для проверки работы рефакторинга бургер-меню
"""
import pytest
from tests.e2e.pages.burger_menu_page import BurgerMenuPage


def test_simple_burger_menu_open(page):
    """Простой тест открытия бургер-меню"""
    burger_menu = BurgerMenuPage(page)

    # Проверяем, что можем открыть меню
    result = burger_menu.open_menu()
    assert result, "Не удалось открыть бургер-меню"

    # Проверяем, что меню открыто
    is_open = burger_menu.is_menu_open()
    assert is_open, "Меню не открыто после попытки открытия"


def test_simple_navigation(page):
    """Простой тест навигации по меню"""
    burger_menu = BurgerMenuPage(page)

    # Открываем меню            # Добавляем небольшую паузу для избежания конфликтов
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

    # Пробуем перейти в "Новости"
    success = burger_menu.navigate_to("Новости")
    assert success, "Не удалось перейти в Новости"