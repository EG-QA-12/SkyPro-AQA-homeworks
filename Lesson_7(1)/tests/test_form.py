"""
Module for TestForm class testing the form filling functionality. From page test_form
"""

import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from pages.form_page import FormPage # Fix import

class TestForm:
    """
    Class for testing the form filling functionality.
    """

    @pytest.fixture
    def setup(self):
        """
        Fixture for setting up the test environment.
        """
        driver = webdriver.Firefox()
        driver.maximize_window()
        wait = WebDriverWait(driver, 10)
        page = FormPage(driver, wait)  # Use FormPage directly
        yield page
        driver.quit()

    def test_fill_form_and_verify_highlight(self, setup):
        """
        Test case for filling the form and verifying field highlighting.
        """
        # Step 1: Open the page with the form
        setup.open_page("https://bonigarcia.dev/selenium-webdriver-java/data-types.html")

        # Steps 2-11: Fill the form
        setup.fill_form("first_name", "Иван")
        setup.fill_form("last_name", "Петров")
        setup.fill_form("address", "Ленина, 55-3")
        setup.fill_form("zip_code", "")
        setup.fill_form("city", "Москва")
        setup.fill_form("country", "Россия")
        setup.fill_form("email", "test@skypro.com")
        setup.fill_form("phone", "+7985899998787")
        setup.fill_form("job_position", "QA")
        setup.fill_form("company", "SkyPro")

        # Step 12: Click the Submit button
        setup.submit_form()

        # Step 13: Verify field highlighting
        assert setup.get_zip_code_highlight_color() == 'rgb(248, 215, 218)'
        assert setup.get_field_highlight_color("first-name") == 'rgb(209, 231, 221)'
        assert setup.get_field_highlight_color("last-name") == 'rgb(209, 231, 221)'
        assert setup.get_field_highlight_color("address") == 'rgb(209, 231, 221)'
        assert setup.get_field_highlight_color("city") == 'rgb(209, 231, 221)'
        assert setup.get_field_highlight_color("country") == 'rgb(209, 231, 221)'
        assert setup.get_field_highlight_color("e-mail") == 'rgb(209, 231, 221)'
        assert setup.get_field_highlight_color("phone") == 'rgb(209, 231, 221)'
        assert setup.get_field_highlight_color("job-position") == 'rgb(209, 231, 221)'
        assert setup.get_field_highlight_color("company") == 'rgb(209, 231, 221)'
