# calculator_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CalculatorPage:
    def __init__(self, driver):
        self.driver = driver

    def open_page(self, url):
        # Открываем указанную страницу
        self.driver.get(url)

    def enter_delay_value(self, delay_value):
        # Находим поле ввода и вводим в него заданное значение
        delay_input = self.driver.find_element(By.CSS_SELECTOR, "#delay")
        delay_input.clear()
        delay_input.send_keys(delay_value)

    def click_button(self, button_locator):
        # Находим кнопку по указанному локатору и кликаем на нее
        button = self.driver.find_element(By.CSS_SELECTOR, button_locator)
        button.click()

    def get_result_text(self):
        # Ожидаем появление элемента "screen" и возвращаем его текст
        result_element = WebDriverWait(self.driver, 45).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.screen"))
        )
        return result_element.text
