"""
Модуль страницы логина для фреймворка автоматизации.

Этот модуль содержит Page Object Model (POM) для страницы логина.
POM - это паттерн проектирования, который помогает инкапсулировать
элементы веб-страницы и действия с ними в отдельном классе.

Преимущества POM:
1. Код становится более читаемым и понятным
2. Изменения в UI требуют правок только в одном месте
3. Переиспользование методов в разных тестах
4. Упрощение отладки и поддержки

Classes:
    LoginPage: Page Object для страницы входа в систему
"""
import logging
from typing import Optional
from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)

class LoginPage:
    """
    Page Object Model для страницы логина.
    
    Инкапсулирует все элементы и действия на странице входа,
    делая тесты более читаемыми и поддерживаемыми.
    
    Args:
        page (Page): Экземпляр страницы Playwright для взаимодействия с браузером
    
    Attributes:
        page (Page): Главный объект страницы
        login_link (Locator): Ссылка "Войти" в навигации
        username_input (Locator): Поле ввода логина
        password_input (Locator): Поле ввода пароля
        submit_button (Locator): Кнопка отправки формы
    """
    page: Page
    login_link: Locator
    username_input: Locator
    password_input: Locator
    submit_button: Locator

    def __init__(self, page: Page) -> None:
        """
        Инициализация Page Object.
        
        Здесь мы определяем все локаторы для элементов страницы.
        Локаторы - это способ найти элемент на странице (по ID, классу, тексту и т.д.)
        
        Args:
            page (Page): Объект страницы Playwright
        """
        self.page = page
        self.login_link = self.page.locator("a.top-nav__ent")
        self.username_input = self.page.locator("#login")
        self.password_input = self.page.locator("#password")
        self.submit_button = self.page.locator("input[type='submit'][value='Войти']")

    def navigate_to_login(self) -> None:
        """
        Переходит к форме логина, кликнув по ссылке "Войти".
        
        Returns:
            None
        """
        logger.debug("Переход к форме логина")
        self.login_link.wait_for(state="visible", timeout=5000)
        self.login_link.click()
        logger.debug("Клик по ссылке 'Войти' выполнен")

    def fill_username(self, username: str) -> None:
        """
        Заполняет поле 'Логин'.
        
        Args:
            username (str): Логин пользователя для ввода
        
        Returns:
            None
        """
        logger.debug(f"Заполняем поле логина: {username}")
        self.username_input.wait_for(state="visible", timeout=5000)
        self.username_input.fill(username)
        logger.debug("Поле логина заполнено")

    def fill_password(self, password: str) -> None:
        """
        Заполняет поле 'Пароль'.
        
        Для безопасности в логах показываем только количество символов,
        а не сам пароль.
        
        Args:
            password (str): Пароль пользователя для ввода
        
        Returns:
            None
        """
        logger.debug(f"Заполняем поле пароля: {'*' * len(password)} символов")
        self.password_input.wait_for(state="visible", timeout=5000)
        self.password_input.fill(password)
        logger.debug("Поле пароля заполнено")

    def click_submit(self) -> None:
        """
        Нажимает кнопку 'Войти' для отправки формы.
        
        Returns:
            None
        """
        logger.debug("Нажимаем кнопку 'Войти'")
        self.submit_button.wait_for(state="visible", timeout=5000)
        self.submit_button.click()
        logger.debug("Кнопка 'Войти' нажата, форма отправлена")

    def login(self, username: str, password: str) -> None:
        """
        Выполняет полный процесс логина.
        
        Этот метод объединяет все шаги входа в систему:
        1. Заполнение логина
        2. Заполнение пароля  
        3. Отправка формы
        
        Args:
            username (str): Логин пользователя
            password (str): Пароль пользователя
        
        Returns:
            None
        """
        logger.info(f"Начинаем процесс входа для пользователя: {username}")
        self.fill_username(username)
        self.fill_password(password)
        self.click_submit()
        logger.info(f"Процесс входа для пользователя {username} завершен")

    def is_login_form_visible(self) -> bool:
        """
        Проверяет, видна ли форма логина на странице.
        
        Returns:
            bool: True, если форма логина видна, False - если нет
        """
        try:
            self.username_input.wait_for(state="visible", timeout=3000)
            return True
        except Exception as e:
            logger.debug(f"Форма логина не найдена: {e}")
            return False

    def get_validation_error(self) -> Optional[str]:
        """
        Получает текст ошибки валидации, если она присутствует.
        
        Returns:
            Optional[str]: Текст ошибки, если найден, None - если ошибок нет
        """
        try:
            error_locator = self.page.locator(".error, .alert-danger, .validation-error")
            error_locator.wait_for(state="visible", timeout=2000)
            error_text = error_locator.text_content()
            logger.debug(f"Найдена ошибка валидации: {error_text}")
            return error_text
        except Exception:
            logger.debug("Ошибки валидации не найдены")
            return None
