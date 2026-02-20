"""Page Object классы для интернет-магазина."""

from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import allure
import re

from .base_page import BasePage


class LoginPage(BasePage):
    """
    Класс для работы со страницей логина интернет-магазина.
    
    Предоставляет методы для аутентификации пользователя в системе.
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализация страницы логина.
        
        Args:
            driver (WebDriver): Экземпляр веб-драйвера Selenium
        """
        super().__init__(driver)
        self.username_locator = (By.ID, "user-name")
        self.password_locator = (By.ID, "password")
        self.login_button_locator = (By.ID, "login-button")
        self.login_url = "https://www.saucedemo.com/"
    
    @allure.step("Открыть страницу логина")
    def open_login_page(self) -> None:
        """
        Открыть страницу входа в систему.
        """
        self.open_page(self.login_url)
    
    @allure.step("Выполнить вход как стандартный пользователь")
    def login_as_standard_user(self) -> None:
        """
        Выполнить вход в систему с учетными данными стандартного пользователя.
        """
        self.open_login_page()
        
        username_field = self.wait_for_element_visible(self.username_locator)
        username_field.send_keys("standard_user")
        
        password_field = self.wait_for_element_visible(self.password_locator)
        password_field.send_keys("secret_sauce")
        
        login_button = self.wait_for_element_clickable(self.login_button_locator)
        login_button.click()


class ProductsPage(BasePage):
    """
    Класс для работы со страницей товаров интернет-магазина.
    
    Предоставляет методы для добавления товаров в корзину и навигации.
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализация страницы товаров.
        
        Args:
            driver (WebDriver): Экземпляр веб-драйвера Selenium
        """
        super().__init__(driver)
        self.add_to_cart_buttons_locators = {
            "Sauce Labs Backpack": (By.ID, "add-to-cart-sauce-labs-backpack"),
            "Sauce Labs Bolt T-Shirt": (By.ID, "add-to-cart-sauce-labs-bolt-t-shirt"),
            "Sauce Labs Onesie": (By.ID, "add-to-cart-sauce-labs-onesie"),
        }
        self.shopping_cart_link_locator = (By.CLASS_NAME, "shopping_cart_link")
    
    @allure.step("Добавить товары в корзину: {product_names}")
    def add_products_to_cart(self, *product_names: str) -> None:
        """
        Добавить указанные товары в корзину.
        
        Args:
            *product_names (str): Имена товаров для добавления в корзину
        """
        for product_name in product_names:
            button_locator = self.add_to_cart_buttons_locators.get(product_name)
            if button_locator:
                add_button = self.wait_for_element_clickable(button_locator)
                add_button.click()
    
    @allure.step("Перейти в корзину")
    def go_to_shopping_cart(self) -> None:
        """
        Перейти на страницу корзины покупок.
        """
        cart_link = self.wait_for_element_clickable(self.shopping_cart_link_locator)
        cart_link.click()


class CheckoutPage(BasePage):
    """
    Класс для работы со страницей оформления заказа.
    
    Предоставляет методы для начала процесса оформления покупки.
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализация страницы оформления заказа.
        
        Args:
            driver (WebDriver): Экземпляр веб-драйвера Selenium
        """
        super().__init__(driver)
        self.checkout_button_locator = (By.ID, "checkout")
    
    @allure.step("Перейти к оформлению заказа")
    def proceed_to_checkout(self) -> None:
        """
        Начать процесс оформления заказа.
        """
        checkout_button = self.wait_for_element_clickable(self.checkout_button_locator)
        checkout_button.click()


class PersonalInfoPage(BasePage):
    """
    Класс для работы со страницей ввода персональных данных.
    
    Предоставляет методы для заполнения информации о покупателе.
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализация страницы персональных данных.
        
        Args:
            driver (WebDriver): Экземпляр веб-драйвера Selenium
        """
        super().__init__(driver)
        self.first_name_locator = (By.ID, "first-name")
        self.last_name_locator = (By.ID, "last-name")
        self.postal_code_locator = (By.ID, "postal-code")
        self.continue_button_locator = (By.ID, "continue")
    
    @allure.step("Заполнить персональную информацию")
    def fill_personal_info(self, first_name: str, last_name: str, postal_code: str) -> None:
        """
        Заполнить форму персональными данными.
        
        Args:
            first_name (str): Имя покупателя
            last_name (str): Фамилия покупателя
            postal_code (str): Почтовый индекс
        """
        first_name_field = self.wait_for_element_visible(self.first_name_locator)
        first_name_field.send_keys(first_name)
        
        last_name_field = self.wait_for_element_visible(self.last_name_locator)
        last_name_field.send_keys(last_name)
        
        postal_code_field = self.wait_for_element_visible(self.postal_code_locator)
        postal_code_field.send_keys(postal_code)
        
        continue_button = self.wait_for_element_clickable(self.continue_button_locator)
        continue_button.click()


class OverviewPage(BasePage):
    """
    Класс для работы со страницей подтверждения заказа.
    
    Предоставляет методы для проверки итоговой стоимости и завершения покупки.
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализация страницы подтверждения заказа.
        
        Args:
            driver (WebDriver): Экземпляр веб-драйвера Selenium
        """
        super().__init__(driver)
        self.total_locator = (By.XPATH, '//div[@class="summary_info_label summary_total_label" and contains(text(), "Total:")]')
        self.finish_button_locator = (By.ID, "finish")
    
    @allure.step("Получить итоговую сумму")
    def get_total_amount(self) -> Optional[str]:
        """
        Получить итоговую сумму заказа.
        
        Returns:
            Optional[str]: Сумма заказа или None, если элемент не найден
        """
        try:
            total_element = self.wait_for_element_visible(self.total_locator)
            total_text = total_element.text
            
            # Извлекаем числовое значение из текста
            total_match = re.search(r'Total: \$([\d.]+)', total_text)
            if total_match:
                return total_match.group(1)
            return None
        except Exception:
            return None
    
    @allure.step("Завершить покупку")
    def complete_purchase(self) -> None:
        """
        Завершить процесс покупки.
        """
        finish_button = self.wait_for_element_clickable(self.finish_button_locator)
        finish_button.click()
