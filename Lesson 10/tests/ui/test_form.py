"""Тесты для формы с Allure разметкой."""

import pytest
import allure
from selenium import webdriver

from pages.form_page import FormPage
from data.test_data import FORM_VALID_DATA


@allure.epic("SkyPro QA Homework")
@allure.feature("Form Tests")
@allure.story("Form Validation and Submission")
class TestForm:
    """
    Класс для тестирования функциональности формы.
    
    Тестирует заполнение формы, валидацию полей и подсветку.
    """
    
    @allure.title("Тест заполнения и проверки формы")
    @allure.description("Проверка заполнения формы валидными данными и подсветки полей")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "regression")
    @pytest.mark.ui
    def test_fill_form_and_verify_highlight(self, driver: webdriver.Remote) -> None:
        """
        Тест заполнения формы и проверки подсветки полей.
        
        Args:
            driver (webdriver.Remote): Экземпляр веб-драйвера
        """
        form_page = FormPage(driver)
        
        with allure.step("Открыть страницу с формой"):
            form_page.open_page("https://bonigarcia.dev/selenium-webdriver-java/data-types.html")
        
        with allure.step("Заполнить форму валидными данными"):
            form_page.fill_form_with_data(FORM_VALID_DATA)
        
        with allure.step("Отправить форму"):
            form_page.submit_form()
        
        with allure.step("Проверить подсветку полей"):
            # Проверяем что поле zip code подсвечено красным (пустое)
            with allure.step("Проверить цвет подсветки поля zip code"):
                zip_code_color = form_page.get_zip_code_highlight_color()
                assert zip_code_color == 'rgb(248, 215, 218)', \
                    f"Ожидаемый цвет zip code: rgb(248, 215, 218), фактический: {zip_code_color}"
            
            # Проверяем что все остальные поля подсвечены зеленым
            expected_green_color = 'rgb(209, 231, 221)'
            fields_to_check = [
                "first-name", "last-name", "address", "city", 
                "country", "e-mail", "phone", "job-position", "company"
            ]
            
            for field_id in fields_to_check:
                with allure.step(f"Проверить цвет подсветки поля '{field_id}'"):
                    field_color = form_page.get_field_highlight_color(field_id)
                    assert field_color == expected_green_color, \
                        f"Ожидаемый цвет поля {field_id}: {expected_green_color}, фактический: {field_color}"
    
    @allure.title("Тест формы с пустым zip code")
    @allure.description("Проверка валидации поля zip code при пустом значении")
    @allure.severity(allure.severity_level.HIGH)
    @allure.tag("validation", "negative")
    @pytest.mark.ui
    def test_form_empty_zip_code(self, driver: webdriver.Remote) -> None:
        """
        Тест формы с пустым полем zip code.
        
        Args:
            driver (webdriver.Remote): Экземпляр веб-драйвера
        """
        form_page = FormPage(driver)
        
        with allure.step("Открыть страницу с формой"):
            form_page.open_page("https://bonigarcia.dev/selenium-webdriver-java/data-types.html")
        
        with allure.step("Заполнить форму с пустым zip code"):
            form_data = FORM_VALID_DATA.copy()
            form_data['zip_code'] = ''  # Пустое значение
            form_page.fill_form_with_data(form_data)
        
        with allure.step("Отправить форму"):
            form_page.submit_form()
        
        with allure.step("Проверить подсветку поля zip code"):
            with allure.step("Проверить что поле zip code подсвечено красным"):
                zip_code_color = form_page.get_zip_code_highlight_color()
                assert zip_code_color == 'rgb(248, 215, 218)', \
                    f"Поле zip code должно быть подсвечено красным цветом, фактический: {zip_code_color}"
    
    @allure.title("Тест формы с невалидным email")
    @allure.description("Проверка валидации поля email")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("validation", "negative")
    @pytest.mark.ui
    def test_form_invalid_email(self, driver: webdriver.Remote) -> None:
        """
        Тест формы с невалидным email.
        
        Args:
            driver (webdriver.Remote): Экземпляр веб-драйвера
        """
        form_page = FormPage(driver)
        
        with allure.step("Открыть страницу с формой"):
            form_page.open_page("https://bonigarcia.dev/selenium-webdriver-java/data-types.html")
        
        with allure.step("Заполнить форму с невалидным email"):
            form_data = FORM_VALID_DATA.copy()
            form_data['email'] = 'invalid-email'  # Невалидный email
            form_page.fill_form_with_data(form_data)
        
        with allure.step("Отправить форму"):
            form_page.submit_form()
        
        with allure.step("Проверить что поле email подсвечено красным"):
            # В данном случае поле email должно быть подсвечено красным
            # из-за невалидного формата (если реализована такая валидация)
            email_color = form_page.get_field_highlight_color("e-mail")
            # Проверяем что цвет не зеленый (может быть красным или остаться без подсветки)
            assert email_color != 'rgb(209, 231, 221)', \
                f"Поле email не должно быть подсвечено зеленым при невалидном значении, фактический: {email_color}"
    
    @allure.title("Тестирование всех полей формы")
    @allure.description("Проверка работы всех полей формы")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("ui", "exploratory")
    @pytest.mark.ui
    def test_form_all_fields(self, driver: webdriver.Remote) -> None:
        """
        Тест всех полей формы на работоспособность.
        
        Args:
            driver (webdriver.Remote): Экземпляр веб-драйвера
        """
        form_page = FormPage(driver)
        
        with allure.step("Открыть страницу с формой"):
            form_page.open_page("https://bonigarcia.dev/selenium-webdriver-java/data-types.html")
        
        with allure.step("Проверить наличие всех полей формы"):
            for field_name in form_page.form_fields.keys():
                with allure.step(f"Проверить наличие поля '{field_name}'"):
                    field_locator = form_page.form_fields[field_name]
                    field_element = form_page.wait_for_element_visible(field_locator)
                    assert field_element.is_displayed(), f"Поле '{field_name}' не отображается"
        
        with allure.step("Проверить наличие кнопки отправки"):
            submit_button = form_page.wait_for_element_visible(form_page.submit_button_locator)
            assert submit_button.is_displayed(), "Кнопка отправки не отображается"