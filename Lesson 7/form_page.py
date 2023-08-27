from selenium.webdriver.common.by import By

class FormPage:
    def __init__(self, driver):
        self.driver = driver
        
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
        first_name_input = self.driver.find_element(*self.first_name)
        last_name_input = self.driver.find_element(*self.last_name)
        address_input = self.driver.find_element(*self.address)
        email_input = self.driver.find_element(*self.email)
        phone_input = self.driver.find_element(*self.phone)
        zip_code_input = self.driver.find_element(*self.zip_code)
        city_input = self.driver.find_element(*self.city)
        country_input = self.driver.find_element(*self.country)
        job_position_input = self.driver.find_element(*self.job_position)
        company_input = self.driver.find_element(*self.company)
        
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
        submit_button = self.driver.find_element(*self.submit_button)
        submit_button.click()
    
    def is_zip_code_highlighted(self):
        zip_code_input = self.driver.find_element(*self.zip_code)
        return "highlight-negative" in zip_code_input.get_attribute("class")
    
     def are_other_fields_highlighted(self):
        fields = [self.first_name, self.last_name, self.address, self.email, self.phone, self.city, self.country, self.job_position, self.company]
        for field in fields:
            element = self.driver.find_element(*field)
            if "highlight-positive" not in element.get_attribute("class"):
                return False
        return True