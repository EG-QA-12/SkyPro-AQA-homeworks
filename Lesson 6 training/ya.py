from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.firefox import GeckoDriverManager

# Инициализация списка веб-драйверов
drivers = [
    webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())),
    webdriver.Firefox(service=GeckoService(GeckoDriverManager().install()))
]


def test_me():
    for driver in drivers:
        # Открытие страницы Яндекса
        driver.get("https://ya.ru")

        # Дополнительные действия на странице, если нужно
        # ...
        sleep(5)
        driver.save_screenshot('./ya.png')
        # Закрытие веб-драйвера
        driver.quit()


# Вызов функции для тестирования
test_me()




