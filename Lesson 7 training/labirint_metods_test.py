from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome()
url ='https://www.labirint.ru/'
searchTerm ='python'
cookie = {
    "name": "cookie_policy",
    "value": "1"
}

def open_labirint():
    browser.get("https://www.labirint.ru/")
    browser.implicitly_wait(4)
    browser.maximize_window()
    browser.add_cookie(cookie)

def search(term):
    browser.find_element(By.CSS_SELECTOR, "#search-field").send_keys(term)
    browser.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

def switch_to_table():
    browser.find_element(By.CSS_SELECTOR, 'a[title="таблицей"]').click()
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table"))
    )

def add_books():
    buy_buttons = browser.find_elements(By.CSS_SELECTOR, 'btn.buy-link.btn-primary')
    counter = 0
    for btn in buy_buttons:
        btn.click()
        counter += 1
    print(counter)
    return counter

def go_to_cart():
    browser.get("https://www.labirint.ru/cart/")           

def get_cart_counter():
    # Примените нужные методы для получения количества товаров в корзине
    # и возвращайте это значение
    pass

def close_driver():
    browser.quit()
    
def test_cart_counter():
    open_labirint()
    search(searchTerm)
    switch_to_table()
    added = add_books()
    go_to_cart()
    cart_counter = get_cart_counter()
    close_driver()
    assert added == cart_counter
   
def test_empty_search():
    open_labirint()
    search('no book search term')
    txt = get_title()

    assert txt == 'Мы ничего не нашли по вашему запросу! Что делать?'

test_cart_counter()
test_empty_search()


  