import pytest
from selenium import webdriver
from LoginPage import LoginPage
from ProductPage import ProductPage, CartPage
from CheckoutPage import CheckoutPage

@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_complete_purchase(browser):
    login_page = LoginPage(browser)
    login_page.login_as_standard_user("standard_user", "secret_sauce")

    product_page = ProductPage(browser)
    product_page.add_product_to_cart('//*[@id="add-to-cart-sauce-labs-backpack"]')
    product_page.add_product_to_cart('//*[@id="add-to-cart-sauce-labs-bolt-t-shirt"]')
    product_page.add_product_to_cart('//*[@id="add-to-cart-sauce-labs-onesie"]')

    cart_page = CartPage(browser)
    cart_page.proceed_to_checkout()

    checkout_page = CheckoutPage(browser)
    checkout_page.fill_shipping_info("Evgeny", "Gusinets", "246006")
    checkout_page.get_total_price()  # You can store this value in a variable if needed

    checkout_page.finish_order()
    total_price = checkout_page.get_total_price()

    assert total_price == "$58.29"
