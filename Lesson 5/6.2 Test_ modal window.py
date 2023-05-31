from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.firefox import GeckoDriverManager

driver = webdriver.Firefox(service=GeckoService(executable_path=GeckoDriverManager().install()))

# Инициализация веб-драйвера
driver.get("http://the-internet.herokuapp.com/entry_ad")

# Ждем, пока модальное окно станет видимым
modal_window = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "modal"))
)

# Находим кнопку Close внутри модального окна
close_button = modal_window.find_element(By.XPATH, "//p[text()='Close']")

# Кликаем на кнопку Close
close_button.click()

# Закрываем веб-драйвер
driver.quit()
