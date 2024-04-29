
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Устанавливаем путь к драйверу Firefox
driver_service = FirefoxService(executable_path=GeckoDriverManager().install())

# Инициализируем драйвер Firefox
driver = webdriver.Firefox(service=driver_service)
driver.maximize_window()


try:
    driver.maximize_window()
    # Run the script 3 times
    for i in range(3):
        driver.get("http://uitestingplayground.com/dynamicid")

        # Wait until the blue button becomes clickable
        blue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary"))
        )

        # Click the blue button
        blue_button.click()

        # Print a message after each click
        print(f"Click executed ({i+1}/3)")

finally:
    # Close the WebDriver
    driver.quit()
