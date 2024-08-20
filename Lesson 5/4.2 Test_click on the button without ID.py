from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    """
    Устанавливает и инициализирует драйвер Firefox.

    Returns:
        webdriver.Firefox: Инициализированный веб-драйвер Firefox.
    """
    # Устанавливаем путь к драйверу Firefox
    driver_service = FirefoxService(executable_path=GeckoDriverManager().install())

    # Инициализируем драйвер Firefox
    driver = webdriver.Firefox(service=driver_service)
    driver.maximize_window()
    return driver


def click_blue_button(driver, wait_time=10):
    """
    Заходит на веб-страницу и кликает на синюю кнопку с динамическим ID.

    Args:
        driver (webdriver.Firefox): Веб-драйвер, использующийся для взаимодействия с браузером.
        wait_time (int, optional): Время ожидания в секундах для элемента до того, как он станет кликабельным. По умолчанию 10 секунд.
    """
    driver.get("http://uitestingplayground.com/dynamicid")

    # Ожидаем, пока синяя кнопка не станет кликабельной
    blue_button = WebDriverWait(driver, wait_time).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary"))
    )

    # Кликаем по синей кнопке
    blue_button.click()


def run_script(driver, iterations=3):
    """
    Выполняет скрипт несколько раз, кликая по кнопке на странице.

    Args:
        driver (webdriver.Firefox): Веб-драйвер, использующийся для взаимодействия с браузером.
        iterations (int, optional): Количество запусков скрипта. По умолчанию 3.
    """
    for i in range(iterations):
        click_blue_button(driver)
        print(f"Click executed ({i + 1}/{iterations})")


def main():
    """
    Основная функция, запускающая драйвер и выполняющая основной сценарий.
    """
    driver = setup_driver()
    try:
        run_script(driver)
    finally:
        # Закрываем драйвер после завершения работы
        driver.quit()


if __name__ == "__main__":
    main()
