import time
import random
import re
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

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

    def click_random_object(self):
        objects = self.driver.find_elements(By.XPATH, "//a[@class='search-list-result__link_2']")
        random_object = random.choice(objects)
        random_object.click()

    def get_search_results(self):
        search_results = self.driver.find_elements(By.XPATH, "//div[@class='search-result']")
        return search_results

    def get_question_text(self):
        question_element = self.driver.find_element(By.XPATH, "//*[@class='question-item question-item__main']")
        return question_element.text

    def count_matching_text(self, query, text):
        match_count = len(re.findall(query, text, re.IGNORECASE))
        return match_count

class TestScenario(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.get("https://bll.by/")

    def test_steps(self):
        self.main_page = MainPage(self.driver)

        # Шаг 1
        # Ничего не нужно делать, тест автоматически открывает главную страницу

        # Шаг 2
        self.driver.get("https://ca.bll.by/login?return=https%3A%2F%2Fbll.by")

        # Шаг 3
        self.main_page.enter_login("usrtest16")

        # Шаг 4
        self.main_page.enter_password("pwdtest16")

        # Шаг 5
        self.main_page.click_login_button()

        # Шаг 6
        self.main_page.click_all_questions_button()

        # Шаг 7
        self.main_page.enter_search_query("Пенсион")
        time.sleep(5)

        # Шаг 8
        self.main_page.click_random_object()
        time.sleep(5)

        # Добавьте здесь ожидание результата шага 8, если требуется

        # Шаг 9
        page_text = self.driver.page_source
        print(page_text)


        # Шаг 10
        match_count = self.main_page.count_matching_text(r"пенсион", question_text)
        if match_count >= 1:
            print("Тест пройден. Найдено {} совпадений.".format(match_count))
        else:
            print("Тест не пройден. Не найдено ни одного совпадения.")


if __name__ == "__main__":
    unittest.main()
