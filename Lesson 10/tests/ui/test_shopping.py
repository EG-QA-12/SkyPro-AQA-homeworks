"""Тесты для интернет-магазина с Allure разметкой."""

import pytest
import allure
from selenium import webdriver

from pages.shopping_page import LoginPage, ProductsPage, CheckoutPage, PersonalInfoPage, OverviewPage
from data.test_data import SHOPPING_TEST_DATA


@allure.epic("SkyPro QA Homework")
@allure.feature("E-commerce Tests")
@allure.story("Complete Purchase Flow")
class TestShopping:
    """
    Класс для тестирования процесса покупки в интернет-магазине.
    
    Тестирует полный цикл покупки от логина до подтверждения заказа.
    """
    
    @allure.title("Полный цикл покупки")
    @allure.description("Тест полного процесса покупки от логина до завершения")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "regression", "e2e")
    @pytest.mark.ui
    def test_complete_purchase(self, driver: webdriver.Remote) -> None:
        """
        Тест полного процесса покупки.
        
        Args:
            driver (webdriver.Remote): Экземпляр веб-драйвера
        """
        # Инициализация страниц
        login_page = LoginPage(driver)
        products_page = ProductsPage(driver)
        checkout_page = CheckoutPage(driver)
        personal_info_page = PersonalInfoPage(driver)
        overview_page = OverviewPage(driver)
        
        with allure.step("Выполнить вход в систему"):
            login_page.login_as_standard_user()
        
        with allure.step("Добавить товары в корзину"):
            products_page.add_products_to_cart(*SHOPPING_TEST_DATA['products'])
        
        with allure.step("Перейти в корзину"):
            products_page.go_to_shopping_cart()
        
        with allure.step("Перейти к оформлению заказа"):
            checkout_page.proceed_to_checkout()
        
        with allure.step("Заполнить персональную информацию"):
            user_info = SHOPPING_TEST_DATA['user_info']
            personal_info_page.fill_personal_info(
                user_info['first_name'],
                user_info['last_name'],
                user_info['postal_code']
            )
        
        with allure.step("Проверить итоговую стоимость"):
            total_amount = overview_page.get_total_amount()
            
            with allure.step(f"Проверить что итоговая сумма равна '{SHOPPING_TEST_DATA['expected_total']}'"):
                assert total_amount == SHOPPING_TEST_DATA['expected_total'], \
                    f"Ожидаемая сумма: {SHOPPING_TEST_DATA['expected_total']}, фактическая: {total_amount}"
        
        with allure.step("Завершить покупку"):
            overview_page.complete_purchase()
    
    @allure.title("Тест добавления товаров в корзину")
    @allure.description("Проверка добавления различных товаров в корзину")
    @allure.severity(allure.severity_level.HIGH)
    @allure.tag("cart", "products")
    @pytest.mark.ui
    def test_add_products_to_cart(self, driver: webdriver.Remote) -> None:
        """
        Тест добавления товаров в корзину.
        
        Args:
            driver (webdriver.Remote): Экземпляр веб-драйвера
        """
        login_page = LoginPage(driver)
        products_page = ProductsPage(driver)
        
        with allure.step("Выполнить вход в систему"):
            login_page.login_as_standard_user()
        
        with allure.step("Проверить наличие кнопок добавления товаров"):
            for product_name in products_page.add_to_cart_buttons_locators.keys():
                with allure.step(f"Проверить наличие кнопки для товара '{product_name}'"):
                    button_locator = products_page.add_to_cart_buttons_locators[product_name]
                    button = products_page.wait_for_element_visible(button_locator)
                    assert button.is_displayed(), f"Кнопка для товара '{product_name}' не отображается"
        
        with allure.step("Добавить первый товар в корзину"):
            products_page.add_products_to_cart("Sauce Labs Backpack")
        
        with allure.step("Проверить что товар добавлен"):
            # Проверяем что кнопка изменилась на "Remove"
            # (это может требовать дополнительной логики для проверки состояния корзины)
            button_locator = products_page.add_to_cart_buttons_locators["Sauce Labs Backpack"]
            button = products_page.wait_for_element_visible(button_locator)
            button_text = button.text
            assert "Remove" in button_text, f"Товар не был добавлен в корзину, текст кнопки: {button_text}"
    
    @allure.title("Тест формы персональных данных")
    @allure.description("Проверка заполнения формы персональных данных")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("checkout", "form")
    @pytest.mark.ui
    def test_personal_info_form(self, driver: webdriver.Remote) -> None:
        """
        Тест формы персональных данных.
        
        Args:
            driver (webdriver.Remote): Экземпляр веб-драйвера
        """
        login_page = LoginPage(driver)
        products_page = ProductsPage(driver)
        checkout_page = CheckoutPage(driver)
        personal_info_page = PersonalInfoPage(driver)
        
        with allure.step("Выполнить вход и перейти к оформлению"):
            login_page.login_as_standard_user()
            products_page.add_products_to_cart("Sauce Labs Backpack")
            products_page.go_to_shopping_cart()
            checkout_page.proceed_to_checkout()
        
        with allure.step("Проверить наличие всех полей формы"):
            fields_to_check = [
                ("first_name", personal_info_page.first_name_locator),
                ("last_name", personal_info_page.last_name_locator),
                ("postal_code", personal_info_page.postal_code_locator)
            ]
            
            for field_name, locator in fields_to_check:
                with allure.step(f"Проверить наличие поля '{field_name}'"):
                    field = personal_info_page.wait_for_element_visible(locator)
                    assert field.is_displayed(), f"Поле '{field_name}' не отображается"
        
        with allure.step("Проверить наличие кнопки продолжения"):
            continue_button = personal_info_page.wait_for_element_visible(personal_info_page.continue_button_locator)
            assert continue_button.is_displayed(), "Кнопка продолжения не отображается"
        
        with allure.step("Заполнить форму тестовыми данными"):
            user_info = SHOPPING_TEST_DATA['user_info']
            personal_info_page.fill_personal_info(
                user_info['first_name'],
                user_info['last_name'],
                user_info['postal_code']
            )
        
        with allure.step("Проверить что поля заполнены"):
            first_name_field = personal_info_page.wait_for_element_visible(personal_info_page.first_name_locator)
            assert first_name_field.get_attribute('value') == user_info['first_name'], \
                f"Поле first name заполнено неверно"
            
            last_name_field = personal_info_page.wait_for_element_visible(personal_info_page.last_name_locator)
            assert last_name_field.get_attribute('value') == user_info['last_name'], \
                f"Поле last name заполнено неверно"
            
            postal_code_field = personal_info_page.wait_for_element_visible(personal_info_page.postal_code_locator)
            assert postal_code_field.get_attribute('value') == user_info['postal_code'], \
                f"Поле postal code заполнено неверно"