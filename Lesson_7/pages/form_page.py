# form_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FormPage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.first_name = (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='first-name']")
        self.last_name = (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='last-name']")
        self.address = (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='address']")
        self.zip_code = (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='zip-code']")
        self.city = (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='city']")
        self.country = (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='country']")
        self.email = (By.CSS_SELECTOR, "input[type='email'][class='form-control'][name='e-mail']")
        self.phone = (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='phone']")
        self.job_position = (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='job-position']")
        self.company = (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='company']")
        self.submit_button = (By.XPATH, "//button[@type='submit']")
        self.zip_code_alert = (By.ID, "zip-code")
        self.success_alerts = (By.CSS_SELECTOR, "div.alert.py-2.alert-success")

    def open_page(self, url):
        self.driver.get(url)

    def fill_form(self, data):
        self.driver.find_element(*self.first_name).send_keys(data["First name"])
        self.driver.find_element(*self.last_name).send_keys(data["Last name"])
        self.driver.find_element(*self.address).send_keys(data["Address"])
        self.driver.find_element(*self.zip_code).send_keys(data["Zip code"])
        self.driver.find_element(*self.city).send_keys(data["City"])
        self.driver.find_element(*self.country).send_keys(data["Country"])
        self.driver.find_element(*self.email).send_keys(data["Email"])
        self.driver.find_element(*self.phone).send_keys(data["Phone number"])
        self.driver.find_element(*self.job_position).send_keys(data["Job position"])
        self.driver.find_element(*self.company).send_keys(data["Company"])

    def submit_form(self):
        self.driver.find_element(*self.submit_button).click()

    def verify_zip_code_highlight(self):
        zip_code_alert = self.wait.until(EC.visibility_of_element_located(self.zip_code_alert))
        assert zip_code_alert.value_of_css_property("background-color") == 'rgb(248, 215, 218)'

    def verify_other_fields_highlight(self):
        success_alerts = self.wait.until(EC.visibility_of_all_elements_located(self.success_alerts))
        for alert in success_alerts:
            assert alert.value_of_css_property("background-color") == 'rgb(209, 231, 221)'
