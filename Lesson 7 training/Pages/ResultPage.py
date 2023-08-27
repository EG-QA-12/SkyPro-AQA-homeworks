from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ResultPage:
    def __init__(self, browser):
    self._driver = browser

    def switch_to_table(self):
    sel_driver.find_element(By.CSS_SELECTOR, 'a[title="таблицей"]').click()
    WebDriverWait( sel_driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table"))

def add_books (self)
    buy_buttons = browser.find_elements(By.CSS_SELECTOR, 'btn.buy-link.btn-primary')
    counter = 0
    for btn in buy_buttons:
        btn.click()
        counter += 1
  
    return counter
def get_empty_result_message (self):
div = self.driver.find_element (By.CSS_SELECTOR, "div.search-error")
h1 = div.find_element (By.CSS_SELECTOR, "h1")
return h1.text