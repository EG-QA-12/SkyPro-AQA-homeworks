"""Базовый класс для всех Page Object классов."""

from typing import Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure


class BasePage:
    """
    Базовый класс для всех Page Object классов.
    
    Содержит общие методы и атрибуты для работы с веб-страницами.
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализация базовой страницы.
        
        Args:
            driver (WebDriver): Экземпляр веб-драйвера Selenium
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    @allure.step("Открыть страницу: {url}")
    def open_page(self, url: str) -> None:
        """
        Открыть указанную страницу.
        
        Args:
            url (str): URL страницы для открытия
        """
        self.driver.get(url)
    
    @allure.step("Получить текущий URL")
    def get_current_url(self) -> str:
        """
        Получить URL текущей страницы.
        
        Returns:
            str: URL текущей страницы
        """
        return self.driver.current_url
    
    @allure.step("Получить заголовок страницы")
    def get_title(self) -> str:
        """
        Получить заголовок текущей страницы.
        
        Returns:
            str: Заголовок страницы
        """
        return self.driver.title
    
    @allure.step("Ожидать видимости элемента")
    def wait_for_element_visible(self, locator: tuple) -> Any:
        """
        Ожидать пока элемент станет видимым.
        
        Args:
            locator (tuple): Локатор элемента (By, value)
            
        Returns:
            Any: Видимый элемент
        """
        return self.wait.until(EC.visibility_of_element_located(locator))
    
    @allure.step("Ожидать кликабельности элемента")
    def wait_for_element_clickable(self, locator: tuple) -> Any:
        """
        Ожидать пока элемент станет кликабельным.
        
        Args:
            locator (tuple): Локатор элемента (By, value)
            
        Returns:
            Any: Кликабельный элемент
        """
        return self.wait.until(EC.element_to_be_clickable(locator))
