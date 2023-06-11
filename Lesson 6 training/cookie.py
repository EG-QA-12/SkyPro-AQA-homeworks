from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager, ChromeType

driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
driver.maximize_window()

my_cookie = {
    'name': 'cookie_policy',
    'value': '1'
}

driver.get("http://labirint.ru")
driver.add_cookie(my_cookie)

cookie = driver.get_cookie('PHPSESSID')
print(cookie)
cookies = driver.get_cookies()

#driver.refresh()
#driver.delete_all_cookies()

#driver.refresh()
#sleep(5)
driver.quit()


