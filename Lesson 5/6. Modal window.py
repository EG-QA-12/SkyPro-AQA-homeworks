from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
driver.maximize_window()

# Инициализация веб-драйвера
driver = webdriver.Chrome()
driver.get("http://the-internet.herokuapp.com/entry_ad")

# Ждем, пока модальное окно станет видимым
modal_window = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "modal"))
)

# Находим кнопку Close внутри модального окна
close_button = modal_window.find_element(By.XPATH, "//p[text()='Close']")

sleep(2) 

# Кликаем на кнопку Close
close_button.click()

# Закрываем веб-драйвер
driver.quit()