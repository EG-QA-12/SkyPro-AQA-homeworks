from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from selenium.webdriver.common.by import By

# Создаем экземпляр драйвера
driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()))
driver.maximize_window()

# Шаг 1: Переходим на сайт
driver.get("http://uitestingplayground.com/textinput")

# Шаг 2: Вводим текст "SkyPro" в поле ввода
input_field = driver.find_element(By.ID, "newButtonName")
input_field.send_keys("SkyPro")

# Шаг 3: Нажимаем на синюю кнопку
blue_button = driver.find_element(By.CSS_SELECTOR, "button.btn-primary")
blue_button.click()

# Шаг 4: Получаем текст кнопки и выводим в консоль
button_text = blue_button.text
print(button_text)

# Закрываем браузер
driver.quit()
