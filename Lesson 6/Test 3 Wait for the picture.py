from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Драйвера Chrome
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Открытие страницы
driver.get("https://bonigarcia.dev/selenium-webdriver-java/loading-images.html")


# Дождаться загрузки всех картинок
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#landscape")))

# Получить значение атрибута src у 3-й картинки
third_image_src = driver.find_element(By.CSS_SELECTOR, "#award").get_attribute("src")

# Вывести значение в консоль
print(third_image_src)

# Закрытие браузера
driver.quit()