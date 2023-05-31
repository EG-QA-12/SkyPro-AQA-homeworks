from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Устанавливаем путь к драйверу Firefox
driver_service = FirefoxService(executable_path=GeckoDriverManager().install())

# Инициализируем драйвер Firefox
driver = webdriver.Firefox(service=driver_service)
driver.maximize_window()
driver.get("http://the-internet.herokuapp.com/add_remove_elements/")

# Ждем, пока кнопка Add Element станет кликабельной
add_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@onclick='addElement()']"))
)

# Кликаем на кнопку Add Element пять раз
for _ in range(5):
    add_button.click()

# Находим все кнопки Delete
delete_buttons = driver.find_elements(By.XPATH, "//button[@class='added-manually']")

# Выводим размер списка кнопок Delete
print("Размер списка кнопок Delete:", len(delete_buttons))

# Закрываем браузер
driver.quit()