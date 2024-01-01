# shopping_page.py
from selenium.webdriver.common.by import By

class BasePage:
    def __init__(self, driver):
        self.driver = driver

class LoginPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.username_locator = (By.ID, "user-name")
        self.password_locator = (By.ID, "password")
        self.login_button_locator = (By.ID, "login-button")

    def login_as_standard_user(self, username, password):
        self.driver.find_element(*self.username_locator).send_keys(username)
        self.driver.find_element(*self.password_locator).send_keys(password)
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

    def add_product_to_cart(self, product_name):
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
        self.total_locator = (By.XPATH, '//div[@class="summary_info_label summary_total_label"]')
        self.finish_button_locator = (By.ID, "finish")

    def get_total_amount(self):
        total_element = self.driver.find_element(*self.total_locator)
        total_text = total_element.text
        return total_text

    def complete_purchase(self):
        self.driver.find_element(*self.finish_button_locator).click()
