from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()

# Инициализация веб-драйвера
driver.get("http://the-internet.herokuapp.com/inputs")

# Находим поле ввода
input_field = driver.find_element(By.CSS_SELECTOR, "input[type='number']")

# Вводим текст "1000" в поле ввода
input_field.send_keys("1000")

# Очищаем поле ввода
input_field.clear()

# Вводим текст "999" в то же самое поле ввода
input_field.send_keys("999")

# Закрываем веб-драйвер
driver.quit()