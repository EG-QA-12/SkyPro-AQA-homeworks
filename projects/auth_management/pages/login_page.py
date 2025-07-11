"""
Модуль страницы логина.

Содержит класс:
- LoginPage: Page Object Model (POM) для страницы логина.
"""
import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)

class LoginPage:
    """
    Класс для работы со страницей логина.
    
    Args:
        page: Экземпляр страницы Playwright.
    """
    def __init__(self, page: Page):
        self.page = page
        self.login_link = self.page.locator("a.top-nav__ent")
        self.username_input = self.page.locator("#login")
        self.password_input = self.page.locator("#password")
        self.submit_button = self.page.locator("input[type='submit'][value='Войти']")

    def fill_username(self, username: str) -> None:
        """
        Заполняет поле 'Логин'.
        
        Args:
            username: Логин пользователя.
        """
        logger.debug(f"Заполняем поле логина: {username}")
        self.username_input.wait_for()
        self.username_input.fill(username)

    def fill_password(self, password: str) -> None:
        """
        Заполняет поле 'Пароль'.
        
        Args:
            password: Пароль пользователя.
        """
        logger.debug(f"Заполняем поле пароля: {'*' * len(password)}")
        self.password_input.wait_for()
        self.password_input.fill(password)

    def click_submit(self) -> None:
        """Нажимает кнопку 'Войти'."""
        logger.debug("Нажимаем кнопку 'Войти'")
        self.submit_button.wait_for()
        self.submit_button.click()

    def login(self, username: str, password: str) -> None:
        """
        Выполняет полный процесс логина.
        
        Args:
            username: Логин пользователя.
            password: Пароль пользователя.
        """
        logger.info(f"Попытка входа для пользователя: {username}")
        self.fill_username(username)
        self.fill_password(password)
        self.click_submit()
        logger.info("Форма логина отправлена.")
