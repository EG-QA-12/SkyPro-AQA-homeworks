"""
Рефакторированные E2E тесты навигации бургер-меню.

Использует параметризацию для покрытия всех пунктов меню одним тестом.
Применяет паттерны Page Object и Data-Driven подход.
"""
import allure
import pytest
from playwright.sync_api import expect

from tests.e2e.pages.burger_menu_page import BurgerMenuPage
from tests.e2e.data.navigation_targets import NAVIGATION_TARGETS, NavigationTarget


@pytest.mark.parametrize("target", NAVIGATION_TARGETS, ids=lambda t: t.menu_text)
@pytest.mark.burger_menu
@pytest.mark.navigation
@pytest.mark.refactored
def test_burger_menu_navigation(page, target: NavigationTarget):
    """
    Параметризованный тест навигации по бургер-меню.

    Проверяет:
    - Открытие бургер-меню
    - Навигацию по пункту меню
    - Статус код ответа
    - Корректность URL перехода

    Args:
        page: Авторизованная страница браузера (фикстура)
        target: Цель навигации с параметрами проверки
    """
    # === Allure ===
    allure.dynamic.title(f"Навигация: {target.menu_text}")
    allure.dynamic.description(target.description)

    # === Тест ===
    burger_menu = BurgerMenuPage(page)

    # Открываем бургер-меню            # Добавляем небольшую паузу для избежания конфликтов
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

    # Навигация с ожиданием ответа
    with page.expect_response(target.expected_url_pattern) as response_info:
        success = burger_menu.navigate_to(target.menu_text)
        error_msg = f"Не удалось перейти по пункту меню: {target.menu_text}"
        assert success, error_msg

    # Проверка статус кода
    response = response_info.value
    assert response.status in target.status_codes, \
        f"Неверный статус код {response.status} для {target.menu_text}"

    # Проверка результата навигации
    burger_menu.assert_navigation_result(target)