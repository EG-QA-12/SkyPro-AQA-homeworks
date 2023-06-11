from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from selenium.webdriver.common.by import By

driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
driver.maximize_window()
#driver.get("http://ya.ru")

#txt = driver.find_element(By.CSS_SELECTOR, "a[title='USD MOEX']").text
#tag = driver.find_element(By.CSS_SELECTOR, "a[title='USD MOEX']").tag_name
#id = driver.find_element(By.CSS_SELECTOR, "a[title='USD MOEX']").id
##print(txt)
#print(tag)
#print(id)

#sleeep(5)
driver.get("http://www.uitestingplayground.com/visibility")
is_displayed = driver.find_element(By.CSS_SELECTOR, "#transparentButton").is_displayed()
print(is_displayed)

is_displayed = driver.find_element(By.CSS_SELECTOR, "#hideButton").click()
sleep(3)

is_displayed = driver.find_element(By.CSS_SELECTOR, "#transparentButton").is_displayed()
print(is_displayed)
sleep(3)


#driver.quit()


