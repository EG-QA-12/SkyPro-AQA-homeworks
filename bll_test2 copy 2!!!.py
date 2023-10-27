import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MainPage:
    # Класс MainPage представляет главную страницу сайта

    def init(self, driver):
        # Метод init инициализирует объект класса MainPage с переданным веб-драйвером

        self.driver = driver

    def enter_login(self, login):
        # Метод enter_login вводит указанный логин в поле для ввода логина

        login_field = self.driver.find_element(By.XPATH, "//input[@id='login']")
        login_field.send_keys(login)

    def enter_password(self, password):
        # Метод enter_password вводит указанный пароль в поле для ввода пароля

        password_field = self.driver.find_element(By.XPATH, "//input[@id='password']")
        password_field.send_keys(password)

    def click_login_button(self):
        # Метод click_login_button нажимает на кнопку "Войти"

        login_button = self.driver.find_element(By.XPATH, "//input[@value='Войти']")
        login_button.click()

    def click_all_questions_button(self):
        # Метод click_all_questions_button нажимает на кнопку "Все вопросы"

        all_questions_button = self.driver.find_element(By.XPATH, "//a[@class='lnk_all2']")
        all_questions_button.click()

    def enter_search_query(self, query):
        # Метод enter_search_query вводит указанный запрос в поле поиска

        search_field = self.driver.find_element(By.XPATH, "//input[@class='page-search__input inp_noborder']")
        search_field.send_keys(query)


class TestScenario(unittest.TestCase):
    # Класс TestScenario содержит набор тестовых сценариев

    def setUp(self):
        # Метод setUp выполняется перед каждым тестовым методом и инициализирует веб-драйвер и открывает главную страницу

        self.driver = webdriver.Firefox()
        self.driver.get("https://bll.by/")

    def test_steps(self):
        # Метод test_steps реализует тестовый сценарий

        main_page = MainPage(self.driver)

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

    def tearDown(self):
        # Метод tearDown выполняется после каждого тестового метода и закрывает веб-драйвер

        self.driver.quit()


if __name__ == "__main__":
    unittest.main()