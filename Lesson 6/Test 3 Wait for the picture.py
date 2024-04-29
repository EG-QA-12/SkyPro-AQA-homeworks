from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.maximize_window()

# Шаг 1: Переходим на сайт
driver.get("https://bonigarcia.dev/selenium-webdriver-java/loading-images.html")

# Шаг 2: Дожидаемся загрузки всех картинок
wait = WebDriverWait(driver, 30, 0.1)

# Добавляем ожидание появления надписи "Done"
wait.until(EC.text_to_be_present_in_element((By.ID, "text"), 'Done!'))

# Используем лямбда-функцию для проверки загрузки всех картинок
images = wait.until(lambda driver: driver.find_elements(By.TAG_NAME, "img"))

# Шаг 3: Проверяем, что список images не пустой и содержит достаточное количество элементов
if len(images) >= 4:
    # Шаг 3: Получаем значение атрибута src у 4-й картинки
    fourth_image = images[3]  # Индексация начинается с 0, поэтому для четвертой картинки используем индекс 3
    src_value = fourth_image.get_attribute("src")

    # Получаем только имя файла из URL
    parsed_url = urlparse(src_value)
    filename = parsed_url.path.split("/")[-1]

    # Шаг 4: Выводим имя файла в консоль
    print("Имя файла четвертой картинки:", filename)
else:
    print("Не удалось найти достаточное количество изображений.")

# Закрываем браузер
driver.quit()
