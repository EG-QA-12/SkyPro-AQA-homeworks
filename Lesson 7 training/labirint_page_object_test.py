from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Pages.MainPage import MainPage
from Pages.ResultPage import ResultPage
from Pages.CartPage import CartPage

def test_cart_counter ():
    browser = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))

    MainPage = MainPage(browser)
    MainPage.set_cookie_policy()
    MainPage.search ('python')

    result_page = ResultPage(browser)
    result_page.switch_to_table()
    result_page.add_books()

    CartPage = CartPage (browser)
    CartPage.get ()


sleep (5)


 