from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


class FormPage:
    def __init__(self, driver):
        driver.implicitly_wait(10)
        self.driver = driver
        self.wait = WebDriverWait(driver, 5)

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
        self.submit_button = (By.CSS_SELECTOR, "button[type='submit'].btn.btn-outline-primary.mt-3")


    def fill_form(self, first_name, last_name, address, email, phone, zip_code, city, country, job_position, company):
        form = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form")))

        # Ожидание и получение ссылок на элементы
        first_name_input = self.wait.until(EC.visibility_of_element_located(self.first_name))
        last_name_input = self.wait.until(EC.visibility_of_element_located(self.last_name))

        # Использование ссылок на элементы для ввода данных
        first_name_input.send_keys(first_name)
        last_name_input.send_keys(last_name)

        first_name_input = self.wait.until(EC.visibility_of_element_located(self.first_name))
        last_name_input = self.wait.until(EC.visibility_of_element_located(self.last_name))
        address_input = self.wait.until(EC.visibility_of_element_located(self.address))
        email_input = self.wait.until(EC.visibility_of_element_located(self.email))
        phone_input = self.wait.until(EC.visibility_of_element_located(self.phone))
        zip_code_input = self.wait.until(EC.visibility_of_element_located(self.zip_code))
        city_input = self.wait.until(EC.visibility_of_element_located(self.city))
        country_input = self.wait.until(EC.visibility_of_element_located(self.country))
        job_position_input = self.wait.until(EC.visibility_of_element_located(self.job_position))
        company_input = self.wait.until(EC.visibility_of_element_located(self.company))

        first_name_input.send_keys(first_name)
        last_name_input.send_keys(last_name)
        address_input.send_keys(address)
        email_input.send_keys(email)
        phone_input.send_keys(phone)
        zip_code_input.send_keys(zip_code)
        city_input.send_keys(city)
        country_input.send_keys(country)
        job_position_input.send_keys(job_position)
        company_input.send_keys(company)
    
    def click_submit(self):
        submit_button = self.wait.until(EC.element_to_be_clickable(self.submit_button))
        submit_button.click()

    def is_zip_code_highlighted(self, expected_class):
        try:
            zip_code_input = self.wait.until(EC.visibility_of_element_located(self.zip_code))
            return expected_class in zip_code_input.get_attribute("class")
        except:
            return False


    def are_other_fields_not_highlighted(self, expected_class):
        failed_fields = []
        fields = [self.first_name, self.last_name, self.address, self.email, self.phone, self.city, self.country,
                  self.job_position, self.company]

        for field in fields:
            try:
                element = self.wait.until(EC.visibility_of_element_located(field))
                if expected_class in element.get_attribute("class"):
                    failed_fields.append(field)
            except:
                failed_fields.append(field)

        return failed_fields

