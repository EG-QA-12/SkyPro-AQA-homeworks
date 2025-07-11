"""
Модуль бизнес-логики авторизации и работы с куками для автотестов.
"""
from typing import Any, Dict, Optional, Tuple

from playwright.sync_api import Browser, BrowserContext, sync_playwright

from .config import config
from .logger import setup_logger
from .user_manager import UserManager

# Настройка логирования
logger = setup_logger(__name__)


def verify_page_cookie_status(page, expected_username: str) -> bool:
    """
    Проверяет статус авторизации пользователя через куки на странице.

    Эта функция является алиасом для verify_user_authorization для обеспечения
    совместимости с GUI интерфейсом.

    Args:
        page: Объект Playwright страницы
        expected_username: Ожидаемый логин пользователя

    Returns:
        bool: True если пользователь авторизован, False иначе
    """
    return verify_user_authorization(page, expected_username)


def verify_user_authorization(page, expected_username: str) -> bool:
    """
    Подтверждает, что пользователь авторизован на целевой странице.

    Args:
        page: Объект Playwright страницы.
        expected_username: Ожидаемый логин пользователя для сверки.

    Returns:
        bool: True, если пользователь авторизован, иначе False.
    """
    try:
        auth_indicators = [
            "[data-testid='user-menu']",
            ".user-profile",
            "#logout",
            "[href*='logout']",
            ".user-name",
            "[class*='user']",
            ".user-in__nick",  # Основной индикатор никнейма
        ]

        found_indicators = []
        for indicator in auth_indicators:
            try:
                if page.locator(indicator).first.is_visible(timeout=1000):
                    found_indicators.append(indicator)
            except Exception as e:
                logger.debug("Индикатор %s не найден: %s", indicator, e)

        user_nickname = None
        try:
            user_nickname_element = page.locator(".user-in__nick")
            if user_nickname_element.count() > 0:
                user_nickname = user_nickname_element.text_content()
                if user_nickname:
                    user_nickname = user_nickname.strip()
        except Exception as e:
            logger.debug("Не удалось получить никнейм: %s", e)

        is_authorized_by_nickname = (
            user_nickname and user_nickname == expected_username.strip()
        )
        is_authorized_by_url = (
            page.url == config.TARGET_URL and len(found_indicators) > 0
        )
        is_authorized_by_dashboard = "dashboard" in page.url.lower()
        is_authorized_by_profile = (
            "profile" in page.url.lower() and len(found_indicators) > 0
        )

        is_authorized = (
            is_authorized_by_nickname
            or is_authorized_by_url
            or is_authorized_by_dashboard
            or is_authorized_by_profile
        )

        logger.info(
            "Проверка авторизации: ник='%s', ожидали='%s', инд=%d, рез=%s",
            user_nickname,
            expected_username,
            len(found_indicators),
            is_authorized,
        )
        return is_authorized

    except Exception as e:
        logger.error("Ошибка проверки статуса авторизации: %s", e)
        return False


def get_credentials() -> Tuple[str, str]:
    """
    Возвращает логин и пароль из конфигурации.
    """
    if not config.LOGIN or not config.PASS:
        raise ValueError(
            f"LOGIN и/или PASS не заданы в {config.CREDS_PATH}"
        )
    return config.LOGIN, config.PASS



def save_cookies(context: BrowserContext, username: str):
    """
    Сохраняет куки из контекста браузера для указанного пользователя.

    Args:
        context: Контекст браузера Playwright.
        username: Имя пользователя для сохранения кук.
    """
    try:
        cookies = context.cookies()
        user_manager = UserManager()
        user_manager.save_user_cookies(username, cookies)
        logger.info("Куки для пользователя '%s' успешно сохранены.", username)
    except Exception as e:
        logger.error("Ошибка при сохранении кук для '%s': %s", username, e)


def load_cookies(context: BrowserContext, username: str) -> bool:
    """
    Загружает куки для пользователя в контекст браузера.

    Args:
        context: Контекст браузера Playwright.
        username: Имя пользователя для загрузки кук.

    Returns:
        bool: True, если куки успешно загружены, иначе False.
    """
    try:
        user_manager = UserManager()
        cookies = user_manager.get_user_cookies(username)

        if cookies:
            context.add_cookies(cookies)
            logger.info("Куки для пользователя '%s' успешно загружены.", username)
            return True
        else:
            logger.warning("Куки для пользователя '%s' не найдены.", username)
            return False
    except Exception as e:
        logger.error("Ошибка при загрузке кук для '%s': %s", username, e)
        return False


def perform_login_on_page(
    page: Any,  # Ожидаем объект playwright.sync_api.Page
    login: str,
    password: str,
    verify_login: bool = True
) -> None:
    """
    Выполняет авторизацию на существующей странице Playwright.

    Args:
        page: Активный объект страницы Playwright.
        login: Логин пользователя.
        password: Пароль пользователя.
        verify_login: Флаг для проверки успешности авторизации.
    """
    login_url = config.LOGIN_URL
    target_url = config.TARGET_URL

    try:
        logger.info("Начало процесса авторизации на странице")
        if page.url != login_url:
            logger.debug("Переход на страницу авторизации: %s", login_url)
            page.goto(login_url, timeout=60000)

        logger.info("Заполнение формы авторизации для пользователя '%s'", login)
        page.fill('#login', login)
        page.fill('#password', password)

        with page.expect_navigation(wait_until="load", timeout=60000):
            page.click('input[type="submit"][value="Войти"]')

        if not page.url.startswith(target_url):
            raise RuntimeError(
                f"Ошибка авторизации. URL: {page.url}, ожидался: {target_url}"
            )

        if verify_login:
            logger.info("Проверка успешности авторизации для '%s'", login)
            if not verify_user_authorization(page, login):
                raise RuntimeError(f"Авторизация не удалась для пользователя {login}")

        logger.info("Авторизация для '%s' прошла успешно.", login)

    except Exception as e:
        logger.error("Ошибка во время авторизации для '%s': %s", login, e)
        raise


class PlaywrightAuth:
    """
    Класс для управления авторизацией через Playwright.
    """

    def __init__(self, headless: bool = True):
        self.playwright = None
        self.browser = None
        self.context = None
        self.headless = headless

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def login(
        self, username: Optional[str] = None, password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Выполняет вход в систему и возвращает результат.
        """
        if not username or not password:
            username, password = get_credentials()

        try:
            self.context = self.browser.new_context()
            page = self.context.new_page()
            perform_login_on_page(page, username, password)

            cookies = self.context.cookies()
            save_cookies(self.context, username)

            return {
                'success': True,
                'cookies': cookies,
                'username': username
            }
        except Exception as e:
            logger.error("Ошибка авторизации для '%s': %s", username, e)
            return {
                'success': False,
                'error': str(e),
                'username': username
            }
        finally:
            if self.context:
                self.context.close()

    def close(self) -> None:
        """
        Закрывает браузер и освобождает ресурсы.
        """
        try:
            if self.context and not self.context.is_closed():
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("Браузер и Playwright успешно закрыты.")
        except Exception as e:
            logger.error("Ошибка при закрытии Playwright: %s", e)
