"""
Module for FormPage class representing a web page with a form.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class FormPage:
    """
    Class representing a web page with a form.
    """

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.form_fields = {
            "first_name": (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='first-name']"),
            "last_name": (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='last-name']"),
            "address": (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='address']"),
            "zip_code": (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='zip-code']"),
            "city": (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='city']"),
            "country": (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='country']"),
            "email": (By.CSS_SELECTOR, "input[type='email'][class='form-control'][name='e-mail']"),
            "phone": (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='phone']"),
            "job_position": (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='job-position']"),
            "company": (By.CSS_SELECTOR, "input[type='text'][class='form-control'][name='company']"),
        }
        self.submit_button = (By.XPATH, "//button[@type='submit']")
        self.zip_code_alert = (By.ID, "zip-code")
        self.success_alerts = (By.CSS_SELECTOR, "div.alert.py-2.alert-success")

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
            self.wait.until(EC.visibility_of_element_located(field_locator)).send_keys(value)

    def submit_form(self):
        """Submit the form on the web page."""
        submit_button = self.wait.until(EC.element_to_be_clickable(self.submit_button))
        submit_button.click()

    def get_zip_code_highlight_color(self):
        """Get the background color of the zip code alert."""
        zip_code_alert = self.wait.until(EC.visibility_of_element_located(self.zip_code_alert))
        return zip_code_alert.value_of_css_property("background-color")

    def get_other_fields_highlight_colors(self):
        """Get the background colors of all success alerts."""
        success_alerts = self.wait.until(EC.visibility_of_all_elements_located(self.success_alerts))
        return [alert.value_of_css_property("background-color") for alert in success_alerts]
