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
from framework.app.pages.base_page import BasePage
from framework.utils.cookie_constants import LOGIN_URL

logger = logging.getLogger(__name__)

class LoginPage(BasePage):
    """
    Класс, представляющий страницу логина.
    Содержит локаторы и методы для взаимодействия с элементами на странице.
    """
    # URL страницы логина вынесен в константы для легкого доступа
    URL = LOGIN_URL
    
    # --- Локаторы ---
    # Использование словарей для локаторов позволяет легко их расширять
    # и делает код более читаемым. Мы используем CSS-селекторы.
    
    LOCATORS = {
        # Используем более надежные селекторы по 'name' атрибуту, 
        # так как 'id' может меняться.
"username_input": "input[name='login'], input[name='email'], #login",
"password_input": "input[type='password'], input[name='password'], #password",
        
        # Локатор для кнопки входа - используем составной селектор
        "submit_button": "button[type='submit']:has-text('Войти'), button[type='submit']:has-text('Вход'), input[type='submit']",
        
        # Локатор для сообщения об ошибке
        "error_message": "div.form-error" 
    }

    def __init__(self, page):
        """
        Инициализация LoginPage.
        
        Args:
            page: Экземпляр страницы Playwright.
        """
        super().__init__(page)
        
        # --- Элементы страницы ---
        # Мы инициализируем локаторы как свойства класса для удобного доступа.
        # Это позволяет избежать повторного поиска элементов в каждом методе.
        self.username_input = self.page.locator(self.LOCATORS["username_input"])
        self.password_input = self.page.locator(self.LOCATORS["password_input"])
        self.submit_button = self.page.locator(self.LOCATORS["submit_button"])
        self.error_message = self.page.locator(self.LOCATORS["error_message"])

    def navigate(self) -> None:
        """
        Переходит на страницу логина и ожидает готовности формы авторизации.
        
        Этот метод инкапсулирует логику перехода на URL страницы логина
        и обеспечивает, что форма авторизации готова к взаимодействию.
        Использует таймауты для стабильности в различных условиях сети.
        
        Raises:
            TimeoutError: Если страница не загрузится за 30 секунд
            
        Example:
            >>> login_page = LoginPage(page)
            >>> login_page.navigate()
            >>> # Теперь можно заполнять форму логина
            
        Note:
            После успешного выполнения поле ввода логина готово к заполнению.
        """
        self.logger.info(f"Начинаем навигацию на страницу логина: {self.URL}")
        self.page.goto(self.URL, timeout=30000)
        
        # Ожидаем появления формы логина для обеспечения готовности
        try:
            self.page.wait_for_selector(self.LOCATORS["username_input"], timeout=5000)
            self.logger.info("Форма логина успешно загружена и готова к использованию")
        except Exception as e:
            self.logger.warning(f"Форма логина не появилась за 5 секунд: {e}")
            # Продолжаем выполнение, так как страница может загрузиться позже

    def fill_username(self, username: str) -> None:
        """
        Заполняет поле логина с валидацией и проверкой готовности.
        
        Метод безопасно заполняет поле ввода логина, ожидая его готовности
        к взаимодействию. Включает валидацию входных данных и подробное
        логирование для отладки тестов.
        
        Args:
            username: Логин пользователя для ввода. Не должен быть пустым.
            
        Raises:
            ValueError: Если username пустой или None
            TimeoutError: Если поле ввода недоступно в течение 10 секунд
            
        Example:
            >>> login_page = LoginPage(page)
            >>> login_page.navigate()
            >>> login_page.fill_username("admin")
            
        Note:
            Метод ожидает видимости поля перед заполнением для стабильности.
        """
        if not username or username.strip() == "":
            raise ValueError("Логин не может быть пустым")
            
        self.logger.info(f"Заполняем поле логина пользователем: '{username}'")
        self.username_input.wait_for(state="visible", timeout=10000)
        self.username_input.fill(username)
        self.logger.info("Поле логина успешно заполнено")

    def fill_password(self, password: str):
        """
        Заполняет поле 'Пароль'.
        
        Для безопасности в логах показываем только количество символов,
        а не сам пароль.
        
        Args:
            password (str): Пароль пользователя для ввода
        
        Returns:
            None
        """
        self.logger.info("Ввод пароля (скрыт)")
        self.password_input.wait_for(state="visible", timeout=10000)
        self.password_input.fill(password)

    def click_submit_button(self):
        """
        Нажимает кнопку 'Войти' для отправки формы.
        
        Returns:
            None
        """
        self.logger.info("Нажатие на кнопку 'Войти'")
        self.submit_button.wait_for(state="visible", timeout=10000)
        self.submit_button.click()

    def login(self, username: str, password: str, cookies_path: str = None):
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
        self.logger.info(f"Выполнение полного цикла логина для пользователя '{username}'")
        self.fill_username(username)
        self.fill_password(password)
        self.click_submit_button()
        
        # После успешного входа, ожидаем перехода на другую страницу.
        # Это делает тест более надежным, так как мы дожидаемся завершения
        # асинхронной операции (редиректа).
        # Ждем, пока URL изменится (уйдем со страницы логина)
        self.page.wait_for_url(lambda url: "login" not in url, timeout=15000)
        
        if cookies_path:
            self.save_cookies(cookies_path)
            self.logger.info(f"Куки для пользователя '{username}' сохранены в {cookies_path}")
            
    def get_error_message(self) -> str:
        """
        Получает текст ошибки валидации, если она присутствует.
        
        Returns:
            Optional[str]: Текст ошибки, если найден, None - если ошибок нет
        """
        if self.error_message.is_visible():
            return self.error_message.inner_text()
        return ""
