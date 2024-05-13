from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Открываем файл chromedriver.log на запись
f = open('chromedriver.log', 'w')

# Создаем экземпляр ChromeService с указанием log_output
service = ChromeService(executable_path=ChromeDriverManager().install(), log_output=f)

driver = webdriver.Chrome(service=service)
driver.maximize_window()

driver.get("http://the-internet.herokuapp.com/login")

# Используем явное ожидание для уверенности, что элементы доступны для взаимодействия
wait = WebDriverWait(driver, 10)

username = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#username")))
password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#password")))
login = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.radius")))

username.send_keys("tomsmith")
password.send_keys("SuperSecretPassword!")
login.click()

# Добавляем проверку успешного входа в систему
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".flash.success")))

driver.quit()

# Закрываем файл chromedriver.log
f.close()
