from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CalculatorPage:
    URL = "https://bonigarcia.dev/selenium-webdriver-java/slow-calculator.html"

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.URL)

    def enter_value(self, value):
        delay_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#delay"))
        )
        delay_input.clear()
        delay_input.send_keys(value)

    def click_button_7(self):
        button_7 = self.driver.find_element(By.XPATH, "//span[contains(@class, 'btn-outline-primary') and text()='7']")
        button_7.click()

    def click_button_plus(self):
        button_plus = self.driver.find_element(By.XPATH, "//span[contains(@class, 'btn-outline-success') and text()='+']")
        button_plus.click()

    def click_button_8(self):
        button_8 = self.driver.find_element(By.XPATH, "//span[contains(@class, 'btn-outline-primary') and text()='8']")
        button_8.click()

    def click_button_equal(self):
        button_equal = self.driver.find_element(By.XPATH, "//span[contains(@class, 'btn-outline-warning') and text()='=']")
        button_equal.click()

    def get_result(self):
        result_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "result"))
        )
        return result_element.text