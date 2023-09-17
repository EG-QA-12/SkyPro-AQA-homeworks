# test_calculator.py
import pytest
from selenium import webdriver
from calculator_page import CalculatorPage

@pytest.fixture
def driver():
    # Запускаем Firefox
    driver = webdriver.Firefox()
    yield driver
    # Закрываем браузер после завершения теста
    driver.quit()

def test_calculator(driver):
    # Создаем объект страницы
    calculator_page = CalculatorPage(driver)
    
    # Открываем страницу
    calculator_page.open_page("https://bonigarcia.dev/selenium-webdriver-java/slow-calculator.html")
    
    # Вводим значение 45 в поле #delay
    calculator_page.enter_delay_value("45")
    
    # Нажимаем на кнопки
    calculator_page.click_button("//span[@class='btn-outline-primary' and text()='7']")
    calculator_page.click_button("span.operator.btn.btn-outline-success:contains('+')")
    calculator_page.click_button("span.btn-outline-primary:contains('8')")
    calculator_page.click_button("span.btn-outline-warning:contains('=')")
    
    # Проверяем результат
    result = calculator_page.get_result_text()
    assert result == "15"