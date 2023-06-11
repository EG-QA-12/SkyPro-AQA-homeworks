from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from selenium.webdriver.common.by import By

driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
driver.maximize_window()

driver.get("https://demoqa.com/browser-windows")

is_displayed = driver.find_element(By.CSS_SELECTOR, "#tabButton").click()

sleep(5)

driver.close()

sleep(15)

driver.quit()



