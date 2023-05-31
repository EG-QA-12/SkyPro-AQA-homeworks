from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_script():
    # Инициализация веб-драйвера
    driver = webdriver.Chrome()
    driver.get("http://uitestingplayground.com/classattr")

    # Ждем, пока кнопка синего цвета станет кликабельной
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-primary.btn-test"))
    )

    # Кликаем на синюю кнопку
    button.click()

    # Закрываем веб-драйвер
    driver.quit()

# Запускаем скрипт 3 раза и проверяем наличие ошибок
for i in range(3):
    try:
        run_script()
        print(f"Скрипт успешно выполнен ({i+1}/3)")
    except Exception as e:
        print(f"Ошибка при выполнении скрипта ({i+1}/3): {str(e)}")