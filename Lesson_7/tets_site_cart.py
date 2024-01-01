import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest


class BasePage:
    def __init__(self, driver):
        self.driver = driver


class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.username_locator = (By.ID, "user-name")
        self.password_locator = (By.ID, "password")
        self.login_button_locator = (By.ID, "login-button")

    def login_as_standard_user(self):
        self.driver.find_element(*self.username_locator).send_keys("standard_user")
        self.driver.find_element(*self.password_locator).send_keys("secret_sauce")
        self.driver.find_element(*self.login_button_locator).click()


class ProductsPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.add_to_cart_buttons_locators = {
            "Sauce Labs Backpack": (By.ID, "add-to-cart-sauce-labs-backpack"),
            "Sauce Labs Bolt T-Shirt": (By.ID, "add-to-cart-sauce-labs-bolt-t-shirt"),
            "Sauce Labs Onesie": (By.ID, "add-to-cart-sauce-labs-onesie"),
        }
        self.shopping_cart_link_locator = (By.CLASS_NAME, "shopping_cart_link")

    def add_products_to_cart(self, *product_names):
        for product_name in product_names:
            self.driver.find_element(*self.add_to_cart_buttons_locators[product_name]).click()

    def go_to_shopping_cart(self):
        self.driver.find_element(*self.shopping_cart_link_locator).click()


class CheckoutPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.checkout_button_locator = (By.ID, "checkout")

    def proceed_to_checkout(self):
        self.driver.find_element(*self.checkout_button_locator).click()


class PersonalInfoPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.first_name_locator = (By.ID, "first-name")
        self.last_name_locator = (By.ID, "last-name")
        self.postal_code_locator = (By.ID, "postal-code")
        self.continue_button_locator = (By.ID, "continue")

    def fill_personal_info(self, first_name, last_name, postal_code):
        self.driver.find_element(*self.first_name_locator).send_keys(first_name)
        self.driver.find_element(*self.last_name_locator).send_keys(last_name)
        self.driver.find_element(*self.postal_code_locator).send_keys(postal_code)
        self.driver.find_element(*self.continue_button_locator).click()


class OverviewPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.total_locator = (By.XPATH, '//div[@class="summary_info_label summary_total_label"]')  # Обновлен XPath
        self.finish_button_locator = (By.ID, "finish")

    def get_total_amount(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.total_locator))
            total_element = self.driver.find_element(*self.total_locator)
            total_text = total_element.text

            # Извлечение значения с помощью регулярного выражения
            total_match = re.search(r'Total: \$([\d.]+)', total_text)
            if total_match:
                return total_match.group(1)
            else:
                raise ValueError("Не удалось извлечь значение общей суммы")  # Явное исключение при неудаче

        except Exception as e:
            print(f"Exception: {e}")
            return None

    def complete_purchase(self):
        self.driver.find_element(*self.finish_button_locator).click()


@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


def test_complete_purchase(browser):
    browser.get("https://www.saucedemo.com/")

    # Шаг 2: Авторизация
    login_page = LoginPage(browser)
    login_page.login_as_standard_user()

    # Шаг 3: Добавление товаров в корзину
    products_page = ProductsPage(browser)
    products_page.add_products_to_cart("Sauce Labs Backpack", "Sauce Labs Bolt T-Shirt", "Sauce Labs Onesie")

    # Шаг 4: Переход в корзину
    products_page.go_to_shopping_cart()

    # Шаг 5: Оформление заказа
    checkout_page = CheckoutPage(browser)
    checkout_page.proceed_to_checkout()

    # Шаг 6: Заполнение персональной информации
    personal_info_page = PersonalInfoPage(browser)
    personal_info_page.fill_personal_info("Evgeny", "Gusinets", "246006")

    # Шаг 7: Проверка итоговой стоимости и завершение покупки
    overview_page = OverviewPage(browser)
    total_amount = overview_page.get_total_amount()

    assert total_amount == "58.29", f"Expected '58.29', but got {total_amount}"

    overview_page.complete_purchase()

    # Шаг 8: Проверка успешного завершения заказа (можно добавить дополнительные шаги)

    # Шаг 9: Закрытие браузера (выполняется автоматически благодаря фикстуре)
