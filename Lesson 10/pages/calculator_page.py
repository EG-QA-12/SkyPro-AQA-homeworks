"""Page Object класс для страницы калькулятора."""

from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure

from .base_page import BasePage


class CalculatorPage(BasePage):
    """
    Класс для работы со страницей калькулятора.
    
    Предоставляет методы для взаимодействия с элементами калькулятора:
    ввод задержки, нажатие кнопок, получение результата.
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализация страницы калькулятора.
        
        Args:
            driver (WebDriver): Экземпляр веб-драйвера Selenium
        """
        super().__init__(driver)
        self.delay_input_locator = (By.CSS_SELECTOR, "#delay")
        self.screen_locator = (By.CSS_SELECTOR, "div.screen")
        self.button_locator_template = "//span[contains(@class, 'btn-outline-primary') and text()='{button_text}']"
        self.operator_locator_template = "//span[contains(@class, 'operator') and text()='{operator}']"
        self.equals_locator = "//span[contains(@class, 'btn-outline-warning') and text()='=']"
    
    @allure.step("Ввести значение задержки: {delay_value}")
    def enter_delay_value(self, delay_value: str) -> None:
        """
        Ввести значение задержки в поле ввода.
        
        Args:
            delay_value (str): Значение задержки для ввода
        """
        delay_input = self.wait_for_element_visible(self.delay_input_locator)
        delay_input.clear()
        delay_input.send_keys(delay_value)
    
    @allure.step("Нажать кнопку: {button_text}")
    def click_button(self, button_text: str) -> None:
        """
        Нажать кнопку с указанным текстом.
        
        Args:
            button_text (str): Текст на кнопке для нажатия
        """
        button_locator = (By.XPATH, self.button_locator_template.format(button_text=button_text))
        button = self.wait_for_element_clickable(button_locator)
        button.click()
    
    @allure.step("Нажать кнопку оператора: {operator}")
    def click_operator_button(self, operator: str) -> None:
        """
        Нажать кнопку оператора (+, -, *, /).
        
        Args:
            operator (str): Символ оператора
        """
        operator_locator = (By.XPATH, self.operator_locator_template.format(operator=operator))
        operator_button = self.wait_for_element_clickable(operator_locator)
        operator_button.click()
    
    @allure.step("Нажать кнопку равно")
    def click_equals_button(self) -> None:
        """
        Нажать кнопку равно (=) для вычисления результата.
        """
        equals_locator = (By.XPATH, self.equals_locator)
        equals_button = self.wait_for_element_clickable(equals_locator)
        equals_button.click()
    
    @allure.step("Получить текст результата")
    def get_result_text(self) -> str:
        """
        Получить текст из поля результата.
        
        Returns:
            str: Текст результата вычисления
        """
        result_element = self.wait_for_element_visible(self.screen_locator)
        return result_element.text
    
    @allure.step("Ожидать появления результата: {expected_result}")
    def wait_for_result(self, expected_result: str, timeout: int = 45) -> str:
        """
        Ожидать появления указанного результата.
        
        Args:
            expected_result (str): Ожидаемый результат
            timeout (int): Таймаут ожидания в секундах
            
        Returns:
            str: Фактический результат
        """
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.text_to_be_present_in_element(self.screen_locator, expected_result))
        return self.get_result_text()
