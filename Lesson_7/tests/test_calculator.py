# 2_test_calculator.py
from selenium import webdriver
from pages.calculator_page import CalculatorPage
import pytest


@pytest.fixture
def driver():
    driver = webdriver.Firefox()
    yield driver
    driver.quit()


def test_calculator(driver):
    calculator_page = CalculatorPage(driver)
    calculator_page.open_page("https://bonigarcia.dev/selenium-webdriver-java/slow-calculator.html")
    calculator_page.enter_delay_value("45")
    calculator_page.click_button("7")
    calculator_page.click_operator_button("+")
    calculator_page.click_button("8")
    calculator_page.click_equals_button()

    # Добавить ожидание перед извлечением результата
    result = calculator_page.get_result_text()
    assert eval(result) == 15  # Используйте eval для вычисления результата выражения

