import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time


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


class TestScenario(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.get("https://bll.by/")

    def test_steps(self):
        main_page = MainPage(self.driver)
        search_results_page = SearchResultsPage(self.driver)

        # Шаг 1
        # Ничего не нужно делать, тест автоматически открывает главную страницу

        # Шаг 2
        self.driver.get("https://ca.bll.by/login?return=https%3A%2F%2Fbll.by")

        # Шаг 3
        main_page.enter_login("usrtest16")

        # Шаг 4
        main_page.enter_password("pwdtest16")

        # Шаг 5
        main_page.click_login_button()

        # Шаг 6
        main_page.click_all_questions_button()

        # Шаг 7
        main_page.enter_search_query("Пенсион")
        time.sleep(5)
        # Добавьте здесь ожидание результата поискового запроса, если требуется

        # Шаг 8
        search_results_page.select_random_answer()

        # Шаг 9
        keyword = "пенсион"
        result = search_results_page.check_keyword_in_answer(keyword)
        self.assertTrue(result, f"Keyword '{keyword}' not found in the answer")

        # Шаг 10
        while self.driver.find_elements(By.CLASS_NAME, "search-results-paging-item.next"):
            self.driver.find_element(By.CLASS_NAME, "search-results-paging-item.next").click()
            search_results_page.select_random_answer()
            result = search_results_page.check_keyword_in_answer(keyword)
            self.assertTrue(result, f"Keyword '{keyword}' not found in the answer")

    def tearDown(self):
        self.driver.quit()


class SearchResultsPage:
    def __init__(self, driver):
        self.driver = driver

    def get_answer_ids(self):
        answer_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/questions/answers/')]")
        answer_ids = []
        for element in answer_elements:
            url = element.get_attribute('href')
            answer_id = url.split('/')[-1]
            answer_ids.append(answer_id)
        return answer_ids

    def select_random_answer(self):
        answer_ids = self.get_answer_ids()
        random_answer_id = random.choice(answer_ids)
        answer_element = self.driver.find_element(By.XPATH,f"//a[contains(@href, '/questions/answers/{random_answer_id}')]")
        answer_element.click()

    def check_keyword_in_answer(self, keyword):
        wait = WebDriverWait(self.driver, 10)
        answer_body_element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "answer-body")))
        answer_text = answer_body_element.text
        return keyword.lower() in answer_text.lower()


if __name__ == "__main__":
    unittest.main()