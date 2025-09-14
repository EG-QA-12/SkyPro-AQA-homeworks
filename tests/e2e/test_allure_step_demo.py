import allure
from typing import Tuple
from playwright.sync_api import BrowserContext, Page


@allure.title("Демонстрация работы allure_step")
def test_allure_step_demo(isolated_context: Tuple[BrowserContext, Page], allure_step) -> None:
    """
    Демонстрационный тест для проверки работы allure_step fixture.
    
    Этот тест показывает правильное использование allure_step 
    fixture для создания шагов в Allure отчете.
    
    Args:
        isolated_context: Кортеж из изолированного BrowserContext и Page
        allure_step: Fixture для создания шагов в Allure отчете
    """
    context, page = isolated_context
    
    with allure_step("Шаг 1: Открытие страницы"):
        page.goto("https://example.com")
    
    with allure_step("Шаг 2: Проверка заголовка страницы"):
        title = page.title()
        assert "Example" in title
    
    with allure_step("Шаг 3: Проверка наличия контента"):
        content = page.text_content("h1")
        assert content is not None
        assert len(content) > 0
    
    print("Allure step demo test passed!")
