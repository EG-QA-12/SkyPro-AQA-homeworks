import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class MainPage:
    def __init__(self, driver):
        self.driver = driver

        self.login_button = (By.XPATH, "//a[contains(text(), 'Войти')]")
        self.username_field = (By.XPATH, "//input[@id='login']")
        self.password_field = (By.XPATH, "//input[@id='password']")
        self.submit_button = (By.XPATH, "//input[@value='Войти']")
        self.all_questions_button = (By.XPATH, "//a[@class='lnk_all2']")
        self.search_input = (By.XPATH, "//input[@class='page-search__input inp_noborder']")

    def click_login_button(self):
        self.driver.find_element(*self.login_button).click()

    def enter_username(self, username):
        self.driver.find_element(*self.username_field).clear()
        self.driver.find_element(*self.username_field).send_keys(username)

    def enter_password(self, password):
        self.driver.find_element(*self.password_field).clear()
        self.driver.find_element(*self.password_field).send_keys(password)

    def click_submit_button(self):
        self.driver.find_element(*self.submit_button).click()

    def click_all_questions_button(self):
        self.driver.find_element(*self.all_questions_button).click()

    def enter_search_query(self, query):
        self.driver.find_element(*self.search_input).clear()
        self.driver.find_element(*self.search_input).send_keys(query)

def run_test():
    # Создание экземпляра драйвера Selenium (в данном случае используется Firefox)
    driver = webdriver.Firefox()

    # Шаги 1-5: Вход на главную страницу и ввод логина и пароля
    main_page = MainPage(driver)
    driver.get("https://bll.by/")
    main_page.click_login_button()
    main_page.enter_username("Login")
    main_page.enter_password("Password")
    main_page.click_submit_button()

    # Шаг 6: Переход на страницу со всеми вопросами
    main_page.click_all_questions_button()

    # Шаг 7: Ввод поискового запроса
    query = "Пенсион"
    main_page.enter_search_query(query)
  
    # Закрытие браузера
    driver.quit()

# Запуск теста
run_test()