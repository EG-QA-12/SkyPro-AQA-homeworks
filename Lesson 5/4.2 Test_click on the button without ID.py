from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Firefox(service=GeckoService(executable_path=GeckoDriverManager().install()))
driver.maximize_window()
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