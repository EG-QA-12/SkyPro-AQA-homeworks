import csv
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class MainPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def enter_login(self, login):
        login_field = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='login']"))
        )
        login_field.send_keys(login)

    def enter_password(self, password):
        password_field = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@id='password']"))
        )
        password_field.send_keys(password)

    def click_login_button(self):
        login_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Войти']"))
        )
        login_button.click()

    def enter_search_query(self, query):
        search_field = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@class="page-search__input inp_noborder"]'))
        )
        search_field.clear()  # Очищаем поле перед вводом
        search_field.send_keys(query)
        search_field.send_keys(Keys.ENTER)

    def get_ids_from_links(self):
        links = self.wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[@class="asr"]'))
        )
        return [link.get_attribute("href").split("=")[1].split("&")[0] for link in links]

    def save_ids_to_csv(self, ids, file_name):
        with open(file_name, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["NumIDs", "IDs"])
            writer.writerows(enumerate(ids, 1))

    def click_close_button(self):
        try:
            close_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="expire-popup__close" and @id="expire-close"]'))
            )
            close_button.click()
        except TimeoutException:
            pass  # Если кнопка не найдена, игнорируем


class TestScenario(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        self.driver.get("https://bii.by/")
        self.main_page = MainPage(self.driver)  # Инициализация страницы поиска

    def test_steps(self):
        self.main_page = MainPage(self.driver)

        # Шаг 1
        # Ничего не нужно делать, тест автоматически открывает главную страницу на сайте Bii.by

        # Шаг 2
        self.driver.get("https://bii.by/login_f.dll")

        # Чтение данных из CSV файла для сайта Bii.by
        csv_path = r"D:\!!! Phyton projects\Bll\Auto2.csv"
        with open(csv_path, 'r') as file:
            reader = csv.reader(file)
            login, password = next(reader, (None, None))  # Читаем только первую строку

        # Шаг 3 и Шаг 4 для сайта Bii.by
        self.main_page.enter_login(login)
        self.main_page.enter_password(password)

        # Шаг 5 для сайта Bii.by
        self.main_page.click_login_button()

        # Чтение данных из текстового файла для поисковых запросов
        swords_path = r"D:\!!! Phyton projects\Bll\Swords.txt"
        with open(swords_path, 'r', encoding='utf-8') as file:
            queries = file.readlines()

        # Счетчик для нумерации файлов с ID
        counter = 1

        # Цикл по поисковым запросам
        for query in queries:
            try:
                # Шаг 1
                # Переходим на страницу поиска
                self.driver.get("https://bii.by/sr.dll?q=")

                # Шаг 2
                # Вводим запрос в поисковую строку
                self.main_page.enter_search_query(query)

                # Шаг 3
                # Нажать Enter (уже сделано в предыдущем шаге)

                # Шаг 4
                # Ожидание 3 сек.
                time.sleep(3)

                # Шаг 5
                # Парсим html страницу и ищем все элементы типа <a class="asr" href="tx.dll?d=12345&f=.......#f">
                # И забираем из этой конструкции <a class="asr" href="tx.dll?d=12345&f=.......#f"> значение после знака = 12345 в переменную{IDs} и сохраняем их все
                # в CSV файл по порядку в колонку NumIDs,IDs от 1 до 20.  Где  NumIDs - порядковый номер IDs начиная с 1 и до 20, а IDs значение переменной {IDs} по порядку из 20 возможных начиная с первого и до 20
                # Этот файл CSV сохраняем под названием ID_search1.CSV для первого запроса.
                ids = self.main_page.get_ids_from_links()
                file_name = f"ID_search{counter}.CSV"
                self.main_page.save_ids_to_csv(ids, file_name)

                # Увеличиваем счетчик на 1
                counter += 1

            except NoSuchElementException as e:
                print(f"Element not found: {e}")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
