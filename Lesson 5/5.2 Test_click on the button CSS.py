from selenium import webdriver
from selenium.webdriver.firefox.service import Service as GeckoService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_script():
    # Initialize Firefox WebDriver using GeckoDriverManager to manage the executable path
    driver = webdriver.Firefox(service=GeckoService(executable_path=GeckoDriverManager(version="v0.30.0").install()))
    driver.get("http://uitestingplayground.com/classattr")

    # Wait until the blue button becomes clickable
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-primary.btn-test"))
    )

    # Click the blue button
    button.click()

    # Close the WebDriver
    driver.quit()

# Run the script 3 times and check for errors
for i in range(3):
    try:
        run_script()
        print(f"Script executed successfully ({i+1}/3)")
    except Exception as e:
        print(f"Error executing script ({i+1}/3): {str(e)}")
