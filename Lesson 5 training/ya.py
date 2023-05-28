from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
driver.maximize_window()
driver.get("https://ya.ru")

driver.get("https://vk.com")

for x in range (1, 10):
    driver.back()
    driver.forward()
    driver.refresh()

sleep(15)
