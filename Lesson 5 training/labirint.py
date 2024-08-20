from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Путь к драйверу Chrome (укажите правильный путь к файлу chromedriver.exe)
chrome_driver_path = "C:/path/to/chromedriver.exe"

# Создание экземпляра браузера
driver = webdriver.Chrome(service=ChromeService(executable_path=chrome_driver_path))
driver.maximize_window()

# зайти в лабиринт 
driver.get("https://www.labirint.ru/")
search_locator = "#search-field"

# найти книги по слову Python
search_input = driver.find_element(By.CSS_SELECTOR, search_locator)
search_input.send_keys("Python")
search_input.send_keys(Keys.RETURN)

# собрать все карточки товаров
sleep(5)  # небольшой пауза, чтобы страница успела загрузиться
books = driver.find_elements(By.CSS_SELECTOR, "div.product")
print(len(books))

# вывести в консоль инфо: название + автор + цена
for book in books:
    title = book.find_element(By.CSS_SELECTOR, 'span.product-title').text
    price = book.find_element(By.CSS_SELECTOR, 'span.price-val').text
    author = ''
    try:
        author = book.find_element(By.CSS_SELECTOR, 'div.product-author').text
    except:
        author = "Автор не указан"
    print(author + "\t" + title + "\t" + price)

sleep(5)
driver.quit()
