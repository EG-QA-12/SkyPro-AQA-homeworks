"""
Module for TestForm class testing the form filling functionality.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pages.form_page


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
        page = pages.form_page.FormPage(driver, wait)
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
        other_fields_colors = setup.get_other_fields_highlight_colors()
        for color in other_fields_colors:
            assert color == 'rgb(209, 231, 221)'
