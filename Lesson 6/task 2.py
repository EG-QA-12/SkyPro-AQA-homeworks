from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

driver.get("http://uitestingplayground.com/textinput?")
wait = WebDriverWait(driver, 10)

element = driver.find_element(By.CSS_SELECTOR, "#newButtonName")
element.clear()

element.send_keys("SkyPro")#Укажите в поле ввода текст SkyPro
wait = WebDriverWait(driver, 10)

button = driver.find_element(By.CSS_SELECTOR, 'button[id="updatingButton"]')
button.click()#Нажмите на синюю кнопку
t = driver.find_element(By.CSS_SELECTOR, 'button[class="btn btn-primary"]').text
print(t)#Получите текст кнопки и выведите в консоль (SkyPro)

driver.quit()