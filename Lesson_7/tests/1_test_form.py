# 1_test_form.py
import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from pages.form_page import FormPage

class TestForm:
    @pytest.fixture
    def setup(self):
        driver = webdriver.Firefox()
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        page = FormPage(driver, wait)
        yield page
        driver.quit()

    def test_fill_form_and_verify_highlight(self, setup):
        # Открываем страницу с формой
        setup.open_page("https://bonigarcia.dev/selenium-webdriver-java/data-types.html")

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
        setup.fill_form(form_data)

        # Нажимаем кнопку Submit
        setup.submit_form()

        # Проверяем подсветку полей
        setup.verify_zip_code_highlight()
        setup.verify_other_fields_highlight()
