

#вывести в консоль инфо: название + автор + цена


from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
driver.maximize_window()

#зайти в лабиринт 
driver.get("https://www.labirint.ru/")
search_locator ="#search-field"

# найти книги по слову Python
search_imput = driver.find_element(By.CSS_SELECTOR, search_locator)
search_imput.send_keys("Python")
search_imput.send_keys(Keys.RETURN)

# собрать все карточки товаров

books = driver.find_elements(By.CSS_SELECTOR,"div.product")
print (len (books))

#вывести в консоль инфо: название + автор + цена
for book in books:
   title = book.find_element(By.CSS_SELECTOR,'span.product-title').text
   price = book.find_element(By.CSS_SELECTOR,'span.price-val').text
   author = ''
   try:
        author =  book.find_element(By.CSS_SELECTOR,'div.product-author').text
   except:
       author = "Автор не указан"
   print(author +"\t" + title + "\t" + price)

sleep(5) 