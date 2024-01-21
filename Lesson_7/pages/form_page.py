"""
Module for FormPage class representing a web page with a form. From page form_page
"""

from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.support import expected_conditions as SeleniumEC

class FormPage:
    """
    Class representing a web page with a form.
    """

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.form_fields = {
            "first_name": (SeleniumBy.CSS_SELECTOR, "input[type='text'][name='first-name']"),
            "last_name": (SeleniumBy.CSS_SELECTOR, "input[type='text'][name='last-name']"),
            "address": (SeleniumBy.CSS_SELECTOR, "input[type='text'][name='address']"),
            "zip_code": (SeleniumBy.CSS_SELECTOR, "input[type='text'][name='zip-code']"),
            "city": (SeleniumBy.CSS_SELECTOR, "input[type='text'][name='city']"),
            "country": (SeleniumBy.CSS_SELECTOR, "input[type='text'][name='country']"),
            "email": (SeleniumBy.CSS_SELECTOR, "input[type='email'][name='e-mail']"),
            "phone": (SeleniumBy.CSS_SELECTOR, "input[type='text'][name='phone']"),
            "job_position": (SeleniumBy.CSS_SELECTOR, "input[type='text'][name='job-position']"),
            "company": (SeleniumBy.CSS_SELECTOR, "input[type='text'][name='company']"),
        }
        self.submit_button = (SeleniumBy.XPATH, "//button[@type='submit']")
        self.zip_code_alert = (SeleniumBy.ID, "zip-code")
        self.success_alerts = (SeleniumBy.CSS_SELECTOR, "div.alert.py-2.alert-success")

    def open_page(self, url):
        """Open the web page with the given URL."""
        self.driver.get(url)

    def fill_form(self, field_name, value):
        """
        Fill the specified form field with the provided value.

        Args:
            field_name (str): The name of the form field.
            value (str): The value to be entered into the form field.
        """
        field_locator = self.form_fields.get(field_name.lower())
        if field_locator:
            self.wait.until(SeleniumEC.visibility_of_element_located(field_locator)) \
                .send_keys(value)

    def submit_form(self):
        """Submit the form on the web page."""
        submit_button = self.wait.until(SeleniumEC.element_to_be_clickable(self.submit_button))
        submit_button.click()

    def get_zip_code_highlight_color(self):
        """Get the background color of the zip code alert."""
        zip_code_alert = self.wait.until(
            SeleniumEC.visibility_of_element_located(self.zip_code_alert)
        )
        return zip_code_alert.value_of_css_property("background-color")

    def get_field_highlight_color(self, field_id):
        """Get the background color of the specified form field."""
        field_locator = (
            SeleniumBy.XPATH,
            f"//div[@class='alert py-2 alert-success' and @id='{field_id}']"
        )
        field = self.wait.until(SeleniumEC.visibility_of_element_located(field_locator))
        return field.value_of_css_property("background-color")
