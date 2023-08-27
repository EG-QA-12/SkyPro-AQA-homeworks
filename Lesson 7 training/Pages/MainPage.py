from selenium.webdriver.common.by import By
class MainPage:
    def __init__(self, driver):
        self._driver = driver
        self._driver.get("https://www.labirint.ru/")
        self.browser.implicitly_wait(4)
        self.browser.maximize_window()

    def set_cookie_policy(self):
        cookie = {
    "name": "cookie_policy",
    "value":"1"
         }
    
         self._driver.add_cookie(cookie)
         print('меня вызвали')
    
    def search (self, term):
        self_driver.find_element(By.CSS_SELECTOR, "#search-field").send_keys(term)
        self_driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
