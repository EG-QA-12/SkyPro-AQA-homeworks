import pytest
from selenium import webdriver
from home_page import HomePage
from form_page import FormPage

class TestForm:
    @pytest.fixture(scope="class")
    def driver(self):
        driver = webdriver.Chrome()
        yield driver
        driver.quit()
    
    def test_fill_form(self, driver):
        home_page = HomePage(driver)
        home_page.open()
        
        form_page = FormPage(driver)
        form_page.fill_form(
            "Иван",
            "Петров",
            "Ленина, 55-3",
            "test@skypro.com",
            "+7985899998787",
            "",
            "Москва",
            "Россия",
            "QA",
            "SkyPro"
        )
        form_page.click_submit()
        
        assert form_page.is_zip_code_highlighted() == True
        assert form_page.are_other_fields_highlighted() == True