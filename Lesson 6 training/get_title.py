from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.firefox import GeckoDriverManager

# Инициализация списка веб-драйверов
drivers = [
    webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install())),
    webdriver.Firefox(service=GeckoService(executable_path=GeckoDriverManager().install()))
]

def test_me():
    for driver in drivers:
        # Открытие страницы Яндекса
        driver.get("https://ya.ru")

        # Дополнительные действия на странице, если нужно
        # ...
        sleep(5)

    for driver in drivers:
        # Получение заголовка текущей страницы
        current_title = driver.title
        print(current_title)

        # Закрытие веб-драйвера
        driver.quit()

# Вызов функции для тестирования
test_me()

print(current_title)
        # Закрытие веб-драйвера
drivers.quit()






