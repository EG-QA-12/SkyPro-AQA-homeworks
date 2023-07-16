from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
driver.maximize_window()


# Шаг 1: Переходим на сайт
driver.get("https://bonigarcia.dev/selenium-webdriver-java/loading-images.html")

sleep(10)

# Шаг 2: Дожидаемся загрузки всех картинок
wait = WebDriverWait(driver, 30, 0.1)

# Используем лямбда-функцию для проверки загрузки всех картинок
images = wait.until(lambda driver: driver.find_elements(By.TAG_NAME, "img"))

# Шаг 3: Проверяем, что список images не пустой и содержит достаточное количество элементов
if len(images) >= 3:
    # Шаг 3: Получаем значение атрибута src у 3-й картинки
    third_image = images[3]
    src_value = third_image.get_attribute("src")

    # Шаг 4: Выводим значение атрибута src в консоль
    print("Значение атрибута src третьей картинки:", src_value)
else:
    print("Не удалось найти достаточное количество изображений.")

# Закрываем браузер
driver.quit()

