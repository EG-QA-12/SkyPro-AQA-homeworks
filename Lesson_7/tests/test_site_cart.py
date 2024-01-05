# test_site_cart.py
import pytest
from selenium import webdriver
from pages.shopping_page import LoginPage, ProductsPage, CheckoutPage, PersonalInfoPage, OverviewPage

@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_complete_purchase(browser):
    saucedemo_url = "https://www.saucedemo.com/"

    # Шаг 1: Создание страниц
    login_page = LoginPage(browser)
    products_page = ProductsPage(browser)
    checkout_page = CheckoutPage(browser)
    personal_info_page = PersonalInfoPage(browser)
    overview_page = OverviewPage(browser)

    # Шаг 2: Авторизация
    login_page.login_as_standard_user()

    # Шаг 3: Добавление товаров в корзину
    products_page.add_products_to_cart("Sauce Labs Backpack", "Sauce Labs Bolt T-Shirt", "Sauce Labs Onesie")

    # Шаг 4: Переход в корзину
    products_page.go_to_shopping_cart()

    # Шаг 5: Оформление заказа
    checkout_page.proceed_to_checkout()

    # Шаг 6: Заполнение персональной информации
    personal_info_page.fill_personal_info("Evgeny", "Gusinets", "246006")

    # Шаг 7: Проверка итоговой стоимости и завершение покупки
    total_amount = overview_page.get_total_amount()
    assert total_amount == "58.29", f"Expected '58.29', but got {total_amount}"

    overview_page.complete_purchase()
