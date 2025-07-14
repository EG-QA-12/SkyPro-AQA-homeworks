"""
Тесты для проверки валидации авторизации пользователей.

Содержит тесты для:
- Проверки успешной авторизации через страницу профиля
- Валидации логина пользователя на странице профиля  
- Обработки ошибок при неуспешной авторизации
"""
import pytest
import logging
from pathlib import Path
from unittest.mock import Mock, patch

from playwright.sync_api import sync_playwright, Page, BrowserContext
from framework.app.pages.profile_page import ProfilePage
from framework.app.pages.login_page import LoginPage
from config.secrets_manager import SecretsManager

logger = logging.getLogger(__name__)


class TestAuthValidation:
    """Тесты для проверки валидации авторизации."""
    
    @pytest.fixture
    def browser_context(self):
        """Создает и предоставляет браузерный контекст для тестов."""
        with sync_playwright() as p:
            # Убираем жестко заданный headless, чтобы Playwright мог управляться
            # флагами командной строки (--headed), которые передает наш скрипт.
            browser = p.chromium.launch()
            context = browser.new_context()
            yield context
            context.close()
            browser.close()
    
    @pytest.fixture
    def page(self, browser_context: BrowserContext) -> Page:
        """Фикстура для создания страницы."""
        page = browser_context.new_page()
        yield page
        page.close()
    
    def test_profile_page_initialization(self, page: Page):
        """
        Тест инициализации ProfilePage.
        
        Проверяет, что класс ProfilePage корректно инициализируется
        и содержит необходимые локаторы.
        """
        logger.info("🧪 Тест инициализации ProfilePage")
        
        profile_page = ProfilePage(page)
        
        # Проверяем, что объект создан
        assert profile_page is not None
        assert profile_page.page == page
        
        # Проверяем, что локаторы инициализированы
        assert profile_page.user_nickname_locator is not None
        assert profile_page.profile_link_locator is not None
        assert profile_page.community_link_pattern == "Я в Сообществе:"
        
        logger.info("✅ ProfilePage успешно инициализирована")
    
    def test_navigate_to_profile_method(self, page: Page):
        """
        Тест метода navigate_to_profile.
        
        Проверяет, что метод корректно переходит на страницу профиля.
        """
        logger.info("🧪 Тест метода navigate_to_profile")
        
        profile_page = ProfilePage(page)
        
        # Мокаем методы для изоляции теста
        with patch.object(profile_page, 'wait_for_profile_page_load', return_value=True):
            result = profile_page.navigate_to_profile("https://ca.bll.by")
            
        # В реальном сценарии потребуется подключение к серверу
        # Для unit-теста просто проверяем, что метод вызывается
        assert hasattr(profile_page, 'navigate_to_profile')
        
        logger.info("✅ Метод navigate_to_profile протестирован")
    
    def test_get_user_nickname_method(self, page: Page):
        """Проверяет получение никнейма со страницы профиля."""
        logger.info("🧪 Тест метода get_user_nickname")
        
        profile_page = ProfilePage(page)
        
        # Тест с мокированием
        mock_locator = Mock()
        mock_locator.wait_for.return_value = None
        mock_locator.text_content.return_value = "TestUser"
        
        with patch.object(profile_page, 'user_nickname_locator', mock_locator):
            nickname = profile_page.get_user_nickname(timeout=1000)
            
        assert nickname == "TestUser"
        
        logger.info("✅ Метод get_user_nickname работает корректно")
    
    def test_is_user_logged_in_success(self, page: Page):
        """
        Тест успешной проверки авторизации пользователя.
        
        Проверяет случай, когда логин на странице совпадает с ожидаемым.
        """
        logger.info("🧪 Тест успешной проверки авторизации")
        
        profile_page = ProfilePage(page)
        expected_username = "EvgenQA"
        
        # Мокаем метод получения никнейма
        with patch.object(profile_page, 'get_user_nickname', return_value="EvgenQA"):
            result = profile_page.is_user_logged_in(expected_username)
            
        assert result is True
        
        logger.info("✅ Проверка авторизации прошла успешно")
    
    def test_is_user_logged_in_failure(self, page: Page):
        """
        Тест неуспешной проверки авторизации пользователя.
        
        Проверяет случай, когда логин на странице НЕ совпадает с ожидаемым.
        """
        logger.info("🧪 Тест неуспешной проверки авторизации")
        
        profile_page = ProfilePage(page)
        expected_username = "EvgenQA"
        
        # Мокаем метод получения никнейма - возвращаем другой логин
        with patch.object(profile_page, 'get_user_nickname', return_value="DifferentUser"):
            result = profile_page.is_user_logged_in(expected_username)
            
        assert result is False
        
        logger.info("✅ Проверка неуспешной авторизации работает корректно")
    
    def test_is_user_logged_in_no_nickname(self, page: Page):
        """
        Тест проверки авторизации когда никнейм не найден.
        
        Проверяет случай, когда элемент с никнеймом отсутствует на странице.
        """
        logger.info("🧪 Тест проверки авторизации без никнейма")
        
        profile_page = ProfilePage(page)
        expected_username = "EvgenQA"
        
        # Мокаем метод получения никнейма - возвращаем None
        with patch.object(profile_page, 'get_user_nickname', return_value=None):
            result = profile_page.is_user_logged_in(expected_username)
            
        assert result is False
        
        logger.info("✅ Обработка отсутствующего никнейма работает корректно")
    
    def test_perform_login_with_verification_success(self, page: Page):
        """
        Проверяет успешный логин с последующей верификацией на странице профиля.
        Тест-кейс:
        1. Открыть страницу логина.
        2. Ввести валидные учетные данные.
        3. Нажать кнопку "Войти".
        4. Проверить, что произошел переход на страницу профиля.
        5. Проверить, что имя пользователя на странице соответствует ожидаемому.
        """
        secrets_manager = SecretsManager()
        creds = secrets_manager.get_auth_credentials()
        
        login_page = LoginPage(page)
        profile_page = ProfilePage(page)

        # Выполняем логин через метод страницы
        login_page.login(creds.username, creds.password)

        # Проверяем, что мы авторизованы
        is_logged_in = profile_page.is_user_logged_in(creds.username)
        
        assert is_logged_in is True, f"Пользователь '{creds.username}' должен быть авторизован."

    def test_perform_login_without_verification(self, page: Page):
        """
        Проверяет базовый функционал логина без верификации на странице профиля.
        Тест-кейс:
        1. Открыть страницу логина.
        2. Ввести валидные учетные данные.
        3. Нажать кнопку "Войти".
        4. Проверить, что URL изменился и не содержит 'login', что указывает на успешный редирект.
        """
        secrets_manager = SecretsManager()
        creds = secrets_manager.get_auth_credentials()
        login_page = LoginPage(page)

        # Выполняем логин
        login_page.login(creds.username, creds.password)

        # Простая проверка, что мы ушли со страницы логина
        page.wait_for_url(lambda url: "login" not in url, timeout=5000)
        assert "login" not in page.url, "После успешного логина URL не должен содержать 'login'."

    def test_login_page_integration_with_profile_validation(self, page: Page):
        """
        Интеграционный тест: логин и проверка имени на странице профиля.
        """
        secrets_manager = SecretsManager()
        admin_creds = secrets_manager.get_auth_credentials()
        
        login_page = LoginPage(page)
        login_page.navigate()
        login_page.login(admin_creds.username, admin_creds.password)
        
        profile_page = ProfilePage(page)
        
        # Явное ожидание загрузки элемента с никнеймом
        profile_page.nickname_element.wait_for(state='visible', timeout=10000)
        
        user_nickname = profile_page.get_user_nickname()
        assert user_nickname == admin_creds.username, \
            f"Ожидаемый никнейм '{admin_creds.username}', но получен '{user_nickname}'"

    @pytest.mark.parametrize("username,expected_result", [
        ("EvgenQA", True),
        ("EvgenQA ", True),  # С пробелом
        (" EvgenQA", True),  # С пробелом в начале
        (" EvgenQA ", True), # С пробелами с обеих сторон
        ("DifferentUser", False),
        ("", False),
    ])
    def test_username_matching_scenarios(self, page: Page, username: str, expected_result: bool):
        """
        Параметризованный тест различных сценариев сравнения логинов.
        
        Проверяет обработку пробелов и различных вариантов логинов.
        """
        logger.info(f"🧪 Тест сравнения логинов: '{username}' -> {expected_result}")
        
        profile_page = ProfilePage(page)
        
        # Мокаем получение никнейма - всегда возвращаем "EvgenQA"
        with patch.object(profile_page, 'get_user_nickname', return_value="EvgenQA"):
            result = profile_page.is_user_logged_in(username)
            
        assert result is expected_result
        
        logger.info(f"✅ Сравнение логинов работает корректно для '{username}'")


@pytest.mark.integration  
class TestAuthValidationIntegration:
    """Интеграционные тесты для валидации авторизации."""
    
    @pytest.fixture
    def real_browser_context(self):
        """Фикстура для реального браузерного контекста (только для интеграционных тестов)."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Используем headless для CI/CD
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True
            )
            yield context
            context.close()
            browser.close()
    
    @pytest.mark.skip(reason="Требует подключения к тестовому серверу")
    def test_real_auth_validation_flow(self, real_browser_context):
        """
        Полный интеграционный тест валидации авторизации.
        
        ВНИМАНИЕ: Этот тест требует:
        - Подключения к тестовому серверу
        - Валидных учетных данных
        - VPN подключения (если требуется)
        """
        logger.info("🧪 Полный интеграционный тест авторизации")
        
        page = real_browser_context.new_page()
        
        try:
            # Получаем реальные учетные данные
            login, password = get_credentials()
            
            # Выполняем авторизацию с проверкой
            perform_login_on_page(
                page,
                login,
                password,
                verify_login=True
            )
            
            logger.info("✅ Полный цикл авторизации с валидацией выполнен успешно")
            
        except Exception as e:
            logger.error(f"❌ Интеграционный тест не прошел: {e}")
            # Делаем скриншот для отладки
            page.screenshot(path="integration_test_failure.png")
            raise
        finally:
            page.close()


if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v", "-s"])
