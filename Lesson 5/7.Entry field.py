from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
driver.maximize_window()

# Инициализация веб-драйвера
driver = webdriver.Chrome()
driver.get("http://the-internet.herokuapp.com/inputs")

# Находим поле ввода
input_field = driver.find_element(By.CSS_SELECTOR, "input[type='number']")

# Вводим текст "1000" в поле ввода
input_field.send_keys("1000")

sleep(2) 

# Очищаем поле ввода
input_field.clear()

sleep(2) 

# Вводим текст "999" в то же самое поле ввода
input_field.send_keys("999")

sleep(2) 

# Закрываем веб-драйвер
driver.quit()