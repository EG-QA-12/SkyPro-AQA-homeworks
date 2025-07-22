import pytest
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from typing import List, Tuple

CSV_PATH = "tests/data/burger_menu_links.csv"
WAIT_TIMEOUT = 5  # секунд


def load_burger_menu_links() -> List[Tuple[str, str]]:
    """Загружает параметры теста из CSV-файла."""
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [(row["link_text"].strip(), row["href"].strip()) for row in reader]

def add_allow_session_param(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query['allow-session'] = ['2']
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

@pytest.fixture(scope="session")
def driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.mark.parametrize("link_text,href", load_burger_menu_links())
def test_burger_menu_link_selenium(driver: webdriver.Chrome, link_text: str, href: str):
    main_url = add_allow_session_param("https://bll.by/")
    href = add_allow_session_param(href)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    driver.get(main_url)
    # Ожидание и клик по бургер-меню
    burger_btn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a.menu-btn.menu-btn_new")))
    burger_btn.click()
    # Ожидание нужной ссылки
    link_selector = f"a.menu_item_link[href='{href}']"
    link = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, link_selector)))
    # Проверка текста (на случай, если href не уникален)
    assert link_text in link.text, f"Текст ссылки '{link.text}' не содержит ожидаемый '{link_text}'"
    link.click()
    # Ожидание заголовка
    heading = wait.until(EC.visibility_of_element_located((By.XPATH, f"//h1[contains(text(), '{link_text}')]")))
    assert heading.is_displayed(), f"Заголовок '{link_text}' не найден после перехода по ссылке ({href})" 