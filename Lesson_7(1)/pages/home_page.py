from selenium import webdriver

class HomePage:
    def __init__(self, driver):
        self.driver = driver
    
    def open(self):
        self.driver.get("https://bonigarcia.dev/selenium-webdriver-java/data-types.html")
