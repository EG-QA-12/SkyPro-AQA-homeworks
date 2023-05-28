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
driver.get("http://the-internet.herokuapp.com/add_remove_elements/")

# Ждем, пока кнопка Add Element станет кликабельной
add_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@onclick='addElement()']"))
)
# Кликаем на кнопку Add Element пять раз
for _ in range(5):
    add_button.click()
sleep(5) 
# Находим все кнопки Delete
delete_buttons = driver.find_elements(By.XPATH, "//button[@class='added-manually']")

# Выводим размер списка кнопок Delete
print("Размер списка кнопок Delete:", len(delete_buttons))


# Закрываем веб-драйвер
driver.quit()


