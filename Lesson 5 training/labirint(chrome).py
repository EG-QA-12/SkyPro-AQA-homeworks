from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Укажите путь к распакованному ChromeDriver
driver_path = "C:\\path\\to\\chromedriver.exe"  # Убедитесь, что путь правильный и экранирован

service = Service(driver_path)
driver = webdriver.Chrome(service=service)
driver.maximize_window()

driver.get("http://uitestingplayground.com/ajax")

driver.find_element(By.CSS_SELECTOR, "#ajaxButton").click()

waiter = WebDriverWait(driver, 60)
green_banner = waiter.until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, ".bg-success"))
)

text = green_banner.text
print(text)

driver.quit()
