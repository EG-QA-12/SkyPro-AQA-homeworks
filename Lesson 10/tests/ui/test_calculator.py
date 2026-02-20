"""Тесты для калькулятора с Allure разметкой."""

import pytest
import allure
from selenium import webdriver

from pages.calculator_page import CalculatorPage
from data.test_data import CALCULATOR_TEST_DATA


@allure.epic("SkyPro QA Homework")
@allure.feature("Calculator Tests")
@allure.story("Calculator Operations")
class TestCalculator:
    """
    Класс для тестирования функциональности калькулятора.
    
    Тестирует базовые арифметические операции с различными задержками.
    """
    
    @allure.title("Тест сложения чисел")
    @allure.description("Проверка операции сложения двух чисел с задержкой")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "regression")
    @pytest.mark.ui
    @pytest.mark.parametrize("test_data", CALCULATOR_TEST_DATA, ids=["addition_45s", "subtraction_30s", "multiplication_20s"])
    def test_calculator_operations(self, driver: webdriver.Remote, test_data: dict) -> None:
        """
        Тест различных операций калькулятора.
        
        Args:
            driver (webdriver.Remote): Экземпляр веб-драйвера
            test_data (dict): Тестовые данные для операции
        """
        calculator_page = CalculatorPage(driver)
        
        with allure.step("Открыть страницу калькулятора"):
            calculator_page.open_page("https://bonigarcia.dev/selenium-webdriver-java/slow-calculator.html")
        
        with allure.step(f"Ввести задержку: {test_data['delay']} секунд"):
            calculator_page.enter_delay_value(test_data['delay'])
        
        with allure.step(f"Ввести первое число: {test_data['first_number']}"):
            calculator_page.click_button(test_data['first_number'])
        
        with allure.step(f"Нажать оператор: {test_data['operator']}"):
            calculator_page.click_operator_button(test_data['operator'])
        
        with allure.step(f"Ввести второе число: {test_data['second_number']}"):
            calculator_page.click_button(test_data['second_number'])
        
        with allure.step("Нажать кнопку равно"):
            calculator_page.click_equals_button()
        
        with allure.step("Проверить результат вычисления"):
            result = calculator_page.wait_for_result(test_data['expected_result'])
            
            with allure.step(f"Проверить что результат равен '{test_data['expected_result']}'"):
                assert result == test_data['expected_result'], \
                    f"Ожидаемый результат: {test_data['expected_result']}, фактический: {result}"
    
    @allure.title("Тест калькулятора с нулевой задержкой")
    @allure.description("Проверка работы калькулятора без задержки")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_calculator_zero_delay(self, driver: webdriver.Remote) -> None:
        """
        Тест калькулятора с минимальной задержкой.
        
        Args:
            driver (webdriver.Remote): Экземпляр веб-драйвера
        """
        calculator_page = CalculatorPage(driver)
        
        with allure.step("Открыть страницу калькулятора"):
            calculator_page.open_page("https://bonigarcia.dev/selenium-webdriver-java/slow-calculator.html")
        
        with allure.step("Ввести задержку: 0 секунд"):
            calculator_page.enter_delay_value("0")
        
        with allure.step("Выполнить операцию 5 + 3"):
            calculator_page.click_button("5")
            calculator_page.click_operator_button("+")
            calculator_page.click_button("3")
            calculator_page.click_equals_button()
        
        with allure.step("Проверить быстрый результат"):
            result = calculator_page.wait_for_result("8", timeout=5)
            
            with allure.step("Проверить что результат равен '8'"):
                assert result == "8", f"Ожидаемый результат: 8, фактический: {result}"
    
    @allure.title("Проверка элементов калькулятора")
    @allure.description("Проверка наличия всех необходимых элементов на странице")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.ui
    def test_calculator_elements(self, driver: webdriver.Remote) -> None:
        """
        Тест наличия всех элементов интерфейса калькулятора.
        
        Args:
            driver (webdriver.Remote): Экземпляр веб-драйвера
        """
        from selenium.webdriver.common.by import By
        
        calculator_page = CalculatorPage(driver)
        
        with allure.step("Открыть страницу калькулятора"):
            calculator_page.open_page("https://bonigarcia.dev/selenium-webdriver-java/slow-calculator.html")
        
        with allure.step("Проверить наличие поля для задержки"):
            delay_input = calculator_page.wait_for_element_visible(calculator_page.delay_input_locator)
            assert delay_input.is_displayed(), "Поле для задержки не отображается"
        
        with allure.step("Проверить наличие экрана результата"):
            screen = calculator_page.wait_for_element_visible(calculator_page.screen_locator)
            assert screen.is_displayed(), "Экран результата не отображается"
        
        with allure.step("Проверить наличие кнопок цифр"):
            for digit in ["7", "8", "5"]:
                button_locator = (By.XPATH, calculator_page.button_locator_template.format(button_text=digit))
                button = calculator_page.wait_for_element_visible(button_locator)
                assert button.is_displayed(), f"Кнопка '{digit}' не отображается"
        
        with allure.step("Проверить наличие кнопки равно"):
            equals_locator = (By.XPATH, calculator_page.equals_locator)
            equals_button = calculator_page.wait_for_element_visible(equals_locator)
            assert equals_button.is_displayed(), "Кнопка равно не отображается"