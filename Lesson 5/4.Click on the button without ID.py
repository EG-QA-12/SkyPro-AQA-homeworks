from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Запуск скрипта 3 раза
for i in range(3):
    driver.get("http://uitestingplayground.com/dynamicid")

    # Ждем, пока кнопка синего цвета станет кликабельной
    blue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary"))
    )

    # Кликаем на кнопку синего цвета
    blue_button.click()

    # Выводим сообщение после каждого клика
    print(f"Клик выполнен ({i+1}/3)")

# Закрываем веб-драйвер
driver.quit()
