from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Pages.MainPage import MainPage
from Pages.ResultPage import ResultPage
from Pages.CartPage import CartPage

def test_cart_counter():
    browser = webdriver.Firefox(service=GeckoService(executable_path=GeckoDriverManager().install()))

    main_page = MainPage(browser)
    main_page.set_cookie_policy()
    main_page.search('python')

    result_page = ResultPage(browser)
    result_page.switch_to_table()
    result_page.add_books()

    cart_page = CartPage(browser)
    cart_page.get()
    as_is = cart_page.get_counter()
    to_be = 10  # Определите ожидаемое значение для to_be

    assert as_is == to_be

    browser.quit()

def test_empty_search_result():
    browser = webdriver.Firefox(service=GeckoService(executable_path=GeckoDriverManager().install()))

    main_page = MainPage(browser)
    main_page.set_cookie_policy()
    main_page.search("no book search term")

    result_page = ResultPage(browser)
    msg = result_page.get_empty_result_message()

    assert msg == 'Мы ничего не нашли по вашему запросу! Что делать?'
    browser.quit()