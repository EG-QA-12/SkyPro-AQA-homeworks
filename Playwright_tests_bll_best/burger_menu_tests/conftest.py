import pytest
from playwright.sync_api import sync_playwright
import os


def pytest_addoption(parser):
    """
    Добавляем опции командной строки для выбора режима headless и пользователя.
    """
    parser.addoption(
        "--headless",
        action="store",
        default="true",
        help="Запуск в headless режиме (true/false)"
    )
    parser.addoption(
        "--user",
        action="store",
        default=None,
        help="Запуск теста для конкретного пользователя"
    )


@pytest.fixture
def user_option(request):
    """
    Фикстура для получения параметра --user
    """
    return request.config.getoption("--user")


@pytest.fixture
def browser_fixture(request):
    """
    Фикстура для инициализации браузера.
    Автоматически закрывает браузер после каждого теста.
    """
    headless = request.config.getoption("--headless").lower() == "true"

    with sync_playwright() as playwright:
        # Создаем браузер
        browser = playwright.chromium.launch(
            headless=headless,
            slow_mo=0,  # Ускоренный режим
        )

        # Создаем контекст с определенными настройками
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            accept_downloads=True,
        )

        # Создаем страницу
        page = context.new_page()

        try:
            yield page
        finally:
            # Закрываем ресурсы после использования
            page.close()
            context.close()
            browser.close()


@pytest.fixture(autouse=True)
def setup_folders():
    """
    Фикстура для создания необходимых директорий.
    Запускается автоматически перед каждым тестом.
    """
    # Создаем директории для скриншотов и логов если они не существуют
    os.makedirs('screenshots', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
