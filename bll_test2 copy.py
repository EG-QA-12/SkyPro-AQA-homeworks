import random
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MainPage:
    def __init__(self, driver):
        self.driver = driver

    def enter_login(self, login):
        login_field = self.driver.find_element(By.XPATH, "//input[@id='login']")
        login_field.send_keys(login)

    def enter_password(self, password):
        password_field = self.driver.find_element(By.XPATH, "//input[@id='password']")
        password_field.send_keys(password)

    def click_login_button(self):
        login_button = self.driver.find_element(By.XPATH, "//input[@value='Войти']")
        login_button.click()

    def click_all_questions_button(self):
        all_questions_button = self.driver.find_element(By.XPATH, "//a[@class='lnk_all2']")
        all_questions_button.click()

    def enter_search_query(self, query):
        search_field = self.driver.find_element(By.XPATH, "//input[@class='page-search__input inp_noborder']")
        search_field.send_keys(query)

    def open_random_object(self):
        objects = self.driver.find_elements(By.XPATH, "//a[@class='search-list-result__link_2']")
        random_object = random.choice(objects)
        random_object.click()

    def search_text_in_page(self, text):
        page_text = self.driver.page_source
        return page_text.count(text)


class TestScenario(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.get("https://bll.by/")

    def test_steps(self):
        main_page = MainPage(self.driver)
        results = []

        # Шаг 1-7 (предыдущие шаги остаются без изменений)
        main_page.click_all_questions_button()
        main_page.enter_search_query("Пенсион")
        time.sleep(5)
        # Добавьте здесь ожидание результата поискового запроса, если требуется

        for i in range(5):
            # Шаг 8
            main_page.open_random_object()

            # Шаг 9
            result = main_page.search_text_in_page("Пенсион")
            results.append(result)

            # Шаг 10
            next_page_link = self.driver.find_element(By.XPATH, "//a[@class='paging__item paging__item--next']")
            next_page_link.click()

        # Шаг 14
        print("Results:")
        for i, result in enumerate(results):
            print(f"Result{i+1}: {result}")
            if result == 0:
                print("Failed")
            else:
                print("Pass")

        # Шаг 15
        if sum(results) == 0:
            print("Result=0 Failed")
        else:
            print("Result>0 Pass")

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()