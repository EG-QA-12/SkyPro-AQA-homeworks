from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Создаем экземпляр драйвера
driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()))
driver.maximize_window()

# Шаг 1: Переходим на сайт
driver.get("http://uitestingplayground.com/textinput")

# Шаг 2: Вводим текст "SkyPro" в поле ввода
input_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "newButtonName")))
input_field.send_keys("SkyPro")

# Шаг 3: Нажимаем на синюю кнопку
blue_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "updatingButton")))
blue_button.click()

# Шаг 4: Получаем текст кнопки и выводим в консоль
button_text = blue_button.text
print(button_text)

# Закрываем браузер
driver.quit()
