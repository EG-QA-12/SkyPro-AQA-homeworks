# test_purchase.py
import pytest
import re
from selenium import webdriver
from shopping_page import LoginPage, ProductsPage, CheckoutPage, PersonalInfoPage, OverviewPage

@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_complete_purchase(browser):
    browser.get("https://www.saucedemo.com/")

    # Шаг 2: Авторизация
    login_page = LoginPage(browser)
    login_page.login_as_standard_user("standard_user", "secret_sauce")

    # Шаг 3: Добавление товаров в корзину
    products_page = ProductsPage(browser)
    products_page.add_product_to_cart("Sauce Labs Backpack")
    products_page.add_product_to_cart("Sauce Labs Bolt T-Shirt")
    products_page.add_product_to_cart("Sauce Labs Onesie")

    # Шаг 4: Переход в корзину
    products_page.go_to_shopping_cart()

    # Шаг 5: Оформление заказа
    checkout_page = CheckoutPage(browser)
    checkout_page.proceed_to_checkout()

    # Шаг 6: Заполнение персональной информации
    personal_info_page = PersonalInfoPage(browser)
    personal_info_page.fill_personal_info("Evgeny", "Gusinets", "246006")

    # Шаг 7: Проверка итоговой стоимости и завершение покупки
    overview_page = OverviewPage(browser)
    total_amount = overview_page.get_total_amount()

    assert "Total: $58.29" in total_amount, f"Expected 'Total: $58.29' to be in {total_amount}"


    overview_page.complete_purchase()

    # Шаг 8: Проверка успешного завершения заказа (можно добавить дополнительные шаги)

    # Шаг 9: Закрытие браузера (выполняется автоматически благодаря фикстуре)
