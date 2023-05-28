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
driver.get("http://the-internet.herokuapp.com/login")

# Находим поле username
username_field = driver.find_element(By.ID, "username")
# Вводим значение "tomsmith" в поле username
username_field.send_keys("tomsmith")
sleep(2) 
# Находим поле password
password_field = driver.find_element(By.ID, "password")
# Вводим значение "SuperSecretPassword!" в поле password
password_field.send_keys("SuperSecretPassword!")
sleep(2) 
# Находим кнопку Login
login_button = driver.find_element(By.XPATH, "//i[contains(@class, 'fa-sign-in')]")
# Кликаем на кнопку Login
login_button.click()
sleep(2) 
# Закрываем веб-драйвер
driver.quit()