"""Page Object класс для домашней страницы."""

from selenium.webdriver.remote.webdriver import WebDriver
import allure

from .base_page import BasePage


class HomePage(BasePage):
    """
    Класс для работы с домашней страницей.
    
    Предоставляет базовые методы для навигации и работы с главной страницей.
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализация домашней страницы.
        
        Args:
            driver (WebDriver): Экземпляр веб-драйвера Selenium
        """
        super().__init__(driver)
        self.url = "https://bonigarcia.dev/selenium-webdriver-java/data-types.html"
    
    @allure.step("Открыть домашнюю страницу")
    def open(self) -> None:
        """
        Открыть домашнюю страницу проекта.
        """
        self.open_page(self.url)
