from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ResultPage:
    def __init__(self, browser):
        self._driver = browser

    def switch_to_table(self):
        self._driver.find_element(By.CSS_SELECTOR, 'a[title="таблицей"]').click()
        WebDriverWait(self._driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table")))

    def add_books(self):
        buy_buttons = self._driver.find_elements(By.CSS_SELECTOR, 'btn.buy-link.btn-primary')
        counter = 0
        for btn in buy_buttons:
            btn.click()
            counter += 1
        return counter

    def get_empty_result_message(self):
        div = self._driver.find_element(By.CSS_SELECTOR, "div.search-error")
        h1 = div.find_element(By.CSS_SELECTOR, "h1")
        return h1.text
