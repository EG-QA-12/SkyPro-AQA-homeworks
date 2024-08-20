from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""
Этот скрипт автоматизирует взаимодействие с веб-страницей "Add/Remove Elements" на сайте the-internet.herokuapp.com.
Скрипт кликает на кнопку "Add Element" пять раз, а затем подсчитывает и выводит количество кнопок "Delete".
"""

# Установка Chrome драйвера с помощью ChromeDriverManager
driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()))
driver.maximize_window()

# Открытие страницы
driver.get("http://the-internet.herokuapp.com/add_remove_elements/")

# Ждем, пока кнопка Add Element станет кликабельной
add_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@onclick='addElement()']"))
)

"""
Кликаем на кнопку Add Element пять раз.
Каждый клик добавляет одну кнопку "Delete" на страницу.
"""
for _ in range(5):
    add_button.click()

# Находим все кнопки Delete
delete_buttons = driver.find_elements(By.XPATH, "//button[@class='added-manually']")

"""
Подсчитываем количество добавленных кнопок "Delete" и выводим результат.
"""
print("Размер списка кнопок Delete:", len(delete_buttons))

# Закрываем веб-драйвер
driver.quit()
