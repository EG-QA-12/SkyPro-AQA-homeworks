import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from calculator_page import CalculatorPage
import time

# Фикстура для инициализации и завершения браузера
@pytest.fixture
def driver():
    # Запускаем браузер Firefox
    driver = webdriver.Firefox()
    yield driver
    # Закрываем браузер после завершения теста
    driver.quit()

# Тест для калькулятора
def test_calculator(driver):
    # Создаем объект страницы калькулятора
    calculator_page = CalculatorPage(driver)

    # Открываем страницу калькулятора
    calculator_page.open_page("https://bonigarcia.dev/selenium-webdriver-java/slow-calculator.html")

    # Вводим значение 45 в поле #delay
    calculator_page.enter_delay_value("45")

    # Находим все элементы с классом "btn-outline-primary"
    buttons = driver.find_elements(By.CSS_SELECTOR, "span.btn-outline-primary")

    # Проходимся по каждому элементу и нажимаем на тот, у которого текст "7"
    for button in buttons:
        if button.text == "7":
            button.click()
            time.sleep(2)  # Подождать 2 секунды
            break

    # Прокручиваем список кнопок и нажимаем на кнопку "+"
    plus_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[@class='operator btn btn-outline-success'][text()='+']")))
    plus_button.click()

    # Проходимся по каждому элементу и нажимаем на тот, у которого текст "8"
    for button in buttons:
        if button.text == "8":
            button.click()
            time.sleep(2)  # Подождать 2 секунды
            break

    # Нажать на кнопку "="
    equals_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[@class='btn btn-outline-warning'][text()='=']")))
    equals_button.click()

    # Получить результат после нажатия "="
    wait = WebDriverWait(driver, 45)
    result_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.screen")))
    result = result_element.text

    # Проверить результат
    assert result == "15"
