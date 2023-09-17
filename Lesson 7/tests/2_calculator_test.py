import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pages.calculator_page import CalculatorPage

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")  # Запуск браузера в фоновом режиме (без отображения окна)
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def test_calculator(driver):
    calculator_page = CalculatorPage(driver)
    calculator_page.open()

    calculator_page.enter_value("45")
    calculator_page.click_button_7()
    calculator_page.click_button_plus()
    calculator_page.click_button_8()
    calculator_page.click_button_equal()

    result = calculator_page.get_result()
    assert result == "15"