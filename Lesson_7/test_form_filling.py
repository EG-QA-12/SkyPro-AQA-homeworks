import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Определение класса страницы
# Определение класса страницы
class FormPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)  # Добавляем атрибут wait
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

    # остальные методы остаются без изменений


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

# Определение класса тестового сценария
class TestForm:
    def setup(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        self.page = FormPage(self.driver)

    def teardown(self):
        self.driver.quit()

    def test_fill_form_and_verify_highlight(self):
        # Открываем страницу с формой
        self.page.open_page("https://bonigarcia.dev/selenium-webdriver-java/data-types.html")

        # Данные для заполнения формы
        form_data = {
            "First name": "Иван",
            "Last name": "Петров",
            "Address": "Ленина, 55-3",
            "Zip code": "",
            "City": "Москва",
            "Country": "Россия",
            "Email": "test@skypro.com",
            "Phone number": "+7985899998787",
            "Job position": "QA",
            "Company": "SkyPro"
        }

        # Заполняем форму
        self.page.fill_form(form_data)

        # Нажимаем кнопку Submit
        self.page.submit_form()

        # Проверяем подсветку полей
        self.page.verify_zip_code_highlight()
        self.page.verify_other_fields_highlight()
