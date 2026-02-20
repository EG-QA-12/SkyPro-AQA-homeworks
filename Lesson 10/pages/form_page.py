"""Page Object класс для страницы с формой."""

from typing import Dict, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure

from .base_page import BasePage


class FormPage(BasePage):
    """
    Класс для работы со страницей с формой ввода данных.
    
    Предоставляет методы для заполнения формы, отправки данных,
    проверки подсветки полей и валидации.
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализация страницы формы.
        
        Args:
            driver (WebDriver): Экземпляр веб-драйвера Selenium
        """
        super().__init__(driver)
        self.wait = WebDriverWait(driver, 10)
        
        # Локаторы полей формы
        self.form_fields: Dict[str, Tuple[str, str]] = {
            "first_name": (By.CSS_SELECTOR, "input[type='text'][name='first-name']"),
            "last_name": (By.CSS_SELECTOR, "input[type='text'][name='last-name']"),
            "address": (By.CSS_SELECTOR, "input[type='text'][name='address']"),
            "zip_code": (By.CSS_SELECTOR, "input[type='text'][name='zip-code']"),
            "city": (By.CSS_SELECTOR, "input[type='text'][name='city']"),
            "country": (By.CSS_SELECTOR, "input[type='text'][name='country']"),
            "email": (By.CSS_SELECTOR, "input[type='email'][name='e-mail']"),
            "phone": (By.CSS_SELECTOR, "input[type='text'][name='phone']"),
            "job_position": (By.CSS_SELECTOR, "input[type='text'][name='job-position']"),
            "company": (By.CSS_SELECTOR, "input[type='text'][name='company']"),
        }
        
        # Локаторы кнопок и элементов
        self.submit_button_locator = (By.XPATH, "//button[@type='submit']")
        self.zip_code_alert_locator = (By.ID, "zip-code")
        self.success_alerts_locator = (By.CSS_SELECTOR, "div.alert.py-2.alert-success")
    
    @allure.step("Заполнить поле '{field_name}' значением '{value}'")
    def fill_form(self, field_name: str, value: str) -> None:
        """
        Заполнить указанное поле формы значением.
        
        Args:
            field_name (str): Имя поля формы
            value (str): Значение для ввода в поле
        """
        field_locator = self.form_fields.get(field_name.lower())
        if field_locator:
            field_element = self.wait.until(EC.visibility_of_element_located(field_locator))
            field_element.send_keys(value)
    
    @allure.step("Отправить форму")
    def submit_form(self) -> None:
        """
        Отправить форму нажатием кнопки Submit.
        """
        submit_button = self.wait.until(EC.element_to_be_clickable(self.submit_button_locator))
        submit_button.click()
    
    @allure.step("Получить цвет подсветки поля zip code")
    def get_zip_code_highlight_color(self) -> str:
        """
        Получить цвет фона поля zip code.
        
        Returns:
            str: CSS цвет фона в формате rgb()
        """
        zip_code_alert = self.wait.until(
            EC.visibility_of_element_located(self.zip_code_alert_locator)
        )
        return zip_code_alert.value_of_css_property("background-color")
    
    @allure.step("Получить цвет подсветки поля '{field_id}'")
    def get_field_highlight_color(self, field_id: str) -> str:
        """
        Получить цвет фона указанного поля формы.
        
        Args:
            field_id (str): ID поля для проверки
            
        Returns:
            str: CSS цвет фона в формате rgb()
        """
        field_locator = (
            By.XPATH,
            f"//div[@class='alert py-2 alert-success' and @id='{field_id}']"
        )
        field = self.wait.until(EC.visibility_of_element_located(field_locator))
        return field.value_of_css_property("background-color")
    
    @allure.step("Заполнить форму тестовыми данными")
    def fill_form_with_data(self, form_data: Dict[str, str]) -> None:
        """
        Заполнить все поля формы данными из словаря.
        
        Args:
            form_data (Dict[str, str]): Словарь с данными для формы
        """
        for field_name, value in form_data.items():
            self.fill_form(field_name, value)
