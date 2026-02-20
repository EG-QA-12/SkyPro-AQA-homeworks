"""Общие фикстуры для всех тестов."""

import os
import pytest
import allure
from typing import Generator, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


# Загрузка переменных окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_browser_options(browser: str, headless: bool = True) -> object:
    """
    Получить опции для указанного браузера.
    
    Args:
        browser (str): Имя браузера ('chrome' или 'firefox')
        headless (bool): Запуск в headless режиме
        
    Returns:
        object: Объект опций браузера
    """
    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--log-level=ERROR")
        return options
    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        return options
    else:
        raise ValueError(f"Неподдерживаемый браузер: {browser}")


@pytest.fixture(scope="function")
def driver(request: pytest.FixtureRequest) -> Generator[webdriver.Remote, None, None]:
    """
    Фикстура для создания веб-драйвера с автоматическим управлением.
    
    По умолчанию использует Chrome в headless режиме.
    Можно переопределить через:
        - Параметр маркера: @pytest.mark.browser("firefox")
        - Переменную окружения: BROWSER=firefox
        - Параметр фикстуры: indirect=True, params=["firefox"]
    
    Yields:
        webdriver.Remote: Экземпляр веб-драйвера
    """
    # Определение браузера
    browser_marker = request.node.get_closest_marker("browser")
    browser = os.getenv("BROWSER", "chrome").lower()
    if browser_marker and browser_marker.args:
        browser = browser_marker.args[0].lower()
    
    # Определение headless режима
    headless = os.getenv("HEADLESS", "true").lower() == "true"
    headless_marker = request.node.get_closest_marker("headless")
    if headless_marker:
        headless = headless_marker.args[0] if headless_marker.args else True
    
    # Создание драйвера
    if browser == "chrome":
        service = ChromeService(ChromeDriverManager().install())
        options = get_browser_options("chrome", headless)
        driver_instance = webdriver.Chrome(service=service, options=options)
    elif browser == "firefox":
        service = FirefoxService(GeckoDriverManager().install())
        options = get_browser_options("firefox", headless)
        driver_instance = webdriver.Firefox(service=service, options=options)
    else:
        raise ValueError(f"Неподдерживаемый браузер: {browser}")
    
    # Установка неявного ожидания
    driver_instance.implicitly_wait(5)
    
    yield driver_instance
    
    # Очистка
    driver_instance.quit()


@pytest.fixture(scope="function")
def chrome_driver() -> Generator[webdriver.Chrome, None, None]:
    """
    Фикстура для создания Chrome драйвера (явное использование).
    
    Yields:
        webdriver.Chrome: Экземпляр Chrome драйвера
    """
    service = ChromeService(ChromeDriverManager().install())
    options = get_browser_options("chrome", headless=True)
    driver_instance = webdriver.Chrome(service=service, options=options)
    driver_instance.implicitly_wait(5)
    
    yield driver_instance
    
    driver_instance.quit()


@pytest.fixture(scope="function")
def firefox_driver() -> Generator[webdriver.Firefox, None, None]:
    """
    Фикстура для создания Firefox драйвера (явное использование).
    
    Yields:
        webdriver.Firefox: Экземпляр Firefox драйвера
    """
    service = FirefoxService(GeckoDriverManager().install())
    options = get_browser_options("firefox", headless=True)
    driver_instance = webdriver.Firefox(service=service, options=options)
    driver_instance.implicitly_wait(5)
    
    yield driver_instance
    
    driver_instance.quit()


@pytest.fixture(params=["chrome", "firefox"], ids=["chrome", "firefox"])
def cross_browser_driver(request: pytest.FixtureRequest) -> Generator[webdriver.Remote, None, None]:
    """
    Фикстура для кросс-браузерного тестирования.
    
    Args:
        request (pytest.FixtureRequest): Объект запроса pytest с параметром браузера
        
    Yields:
        webdriver.Remote: Экземпляр соответствующего браузера
    """
    browser = request.param
    options = get_browser_options(browser, headless=True)
    
    if browser == "chrome":
        service = ChromeService(ChromeDriverManager().install())
        driver_instance = webdriver.Chrome(service=service, options=options)
    elif browser == "firefox":
        service = FirefoxService(GeckoDriverManager().install())
        driver_instance = webdriver.Firefox(service=service, options=options)
    
    driver_instance.implicitly_wait(5)
    
    yield driver_instance
    
    driver_instance.quit()


@pytest.fixture
def screenshot_on_failure(request: pytest.FixtureRequest) -> Generator[None, None, None]:
    """
    Фикстура для создания скриншота при падении теста.
    
    Должна использоваться вместе с фикстурой driver.
    
    Args:
        request (pytest.FixtureRequest): Объект запроса pytest
    """
    yield
    
    # Проверяем, есть ли атрибут failed у теста
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        driver_instance = request.node.funcargs.get('driver')
        if driver_instance:
            try:
                screenshot_name = f"screenshot_{request.node.name.replace('::', '_')}.png"
                driver_instance.save_screenshot(screenshot_name)
                allure.attach.file(
                    screenshot_name,
                    name="Скриншот при падении",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                allure.attach(
                    f"Не удалось создать скриншот: {str(e)}",
                    name="screenshot_error",
                    attachment_type=allure.attachment_type.TEXT
                )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Optional[pytest.TestReport]:
    """
    Хук для создания отчёта о выполнении теста.
    
    Args:
        item (pytest.Item): Элемент теста
        call (pytest.CallInfo): Информация о вызове
        
    Returns:
        Optional[pytest.TestReport]: Отчёт о тесте
    """
    outcome = yield
    report = outcome.get_result()
    
    # Сохраняем результат в атрибуты теста
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture
def test_data_generator():
    """
    Фикстура для генерации тестовых данных.
    
    Yields:
        DataGenerator: Генератор тестовых данных
    """
    from data.faker_data import generate_teacher, generate_form_data
    
    class DataGenerator:
        """Генератор тестовых данных."""
        
        def teacher(self) -> dict:
            """Сгенерировать данные учителя."""
            return generate_teacher()
        
        def form(self) -> dict:
            """Сгенерировать данные формы."""
            return generate_form_data()
    
    yield DataGenerator()