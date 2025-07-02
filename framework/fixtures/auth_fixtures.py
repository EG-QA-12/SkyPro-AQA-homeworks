"""
Fixtures для автоматизации авторизации в тестах.

Этот модуль предоставляет готовые fixtures для pytest, которые
упрощают процесс авторизации в тестах.

Основные преимущества:
1. Готовые фикстуры "из коробки" - не нужно каждый раз писать код авторизации
2. Автоматическое управление cookies и сессиями
3. Возможность легко переключаться между разными пользователями
4. Централизованное управление браузерными контекстами
5. Изоляция тестов - каждый тест получает свой чистый контекст
6. Повторное использование авторизованных сессий для ускорения тестов

Fixtures:
    browser_context: Базовый браузерный контекст
    authenticated_admin: Контекст с авторизованным администратором
    authenticated_user: Контекст с обычным авторизованным пользователем
    clean_context: Контекст без авторизации (чистые cookies)
"""

import pytest
from typing import Generator, Optional
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page
from ..utils.auth_utils import load_user_cookie, save_user_cookie, clear_all_cookies, check_cookie_validity
from ..app.pages.login_page import LoginPage


@pytest.fixture(scope="function")
def browser_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Базовая фикстура для создания браузерного контекста.
    
    Создает новый контекст для каждого теста, что обеспечивает
    изоляцию между тестами - cookies одного теста не влияют на другой.
    
    Args:
        browser: Браузер из playwright (должен быть настроен в conftest.py)
        
    Yields:
        BrowserContext: Новый браузерный контекст для теста
        
    Example:
        def test_something(browser_context):
            page = browser_context.new_page()
            # ... логика теста
    """
    context = browser.new_context()
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function") 
def clean_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Фикстура для создания контекста без авторизации.
    
    Гарантированно создает контекст с очищенными cookies.
    Полезно для тестирования функциональности неавторизованных пользователей.
    
    Args:
        browser: Браузер из playwright
        
    Yields:
        BrowserContext: Браузерный контекст без cookies авторизации
        
    Example:
        def test_login_form_visibility(clean_context):
            page = clean_context.new_page()
            # Тест проверки формы логина для неавторизованного пользователя
    """
    context = browser.new_context()
    clear_all_cookies(context)
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def authenticated_admin(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Фикстура для авторизованного администратора.
    
    Пытается загрузить сохраненные cookies администратора.
    Если cookies нет или они невалидны, выполняет авторизацию через UI
    и сохраняет новые cookies для будущих тестов.
    
    Args:
        browser: Браузер из playwright
        
    Yields:
        BrowserContext: Контекст с авторизацией под администратором
        
    Example:
        def test_admin_panel(authenticated_admin):
            page = authenticated_admin.new_page()
            page.goto("/admin")
            # Тест функций админ-панели
    """
    context = browser.new_context()
    
    # Пытаемся загрузить существующие cookies администратора
    if load_user_cookie(context, "admin"):
        # Проверяем валидность загруженных cookies
        page = context.new_page()
        page.goto("https://bll.by/")  # Базовый URL приложения
        
        if check_cookie_validity(context, "admin"):
            try:
                yield context
                return
            finally:
                context.close()
    
    # Если cookies нет или невалидны, выполняем авторизацию
    page = context.new_page()
    login_page = LoginPage(page)
    
    # Переходим на страницу логина
    page.goto("https://bll.by/login")
    
    # Получаем данные администратора из secrets
    secrets_dir = Path(__file__).parent.parent.parent / "secrets"
    admin_credentials = _get_user_credentials(secrets_dir, "admin")
    
    if admin_credentials:
        login_page.login(admin_credentials["username"], admin_credentials["password"])
        
        # Ждем завершения авторизации
        page.wait_for_timeout(2000)
        
        # Сохраняем cookies для будущего использования
        save_user_cookie(context, "admin")
    
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def authenticated_user(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Фикстура для обычного авторизованного пользователя.
    
    Аналогично authenticated_admin, но для обычного пользователя.
    Полезно для тестирования функциональности, доступной обычным пользователям.
    
    Args:
        browser: Браузер из playwright
        
    Yields:
        BrowserContext: Контекст с авторизацией под обычным пользователем
        
    Example:
        def test_user_profile(authenticated_user):
            page = authenticated_user.new_page()
            page.goto("/profile")
            # Тест профиля пользователя
    """
    context = browser.new_context()
    
    # Пытаемся загрузить существующие cookies пользователя
    if load_user_cookie(context, "user"):
        page = context.new_page()
        page.goto("https://bll.by/")
        
        if check_cookie_validity(context, "user"):
            try:
                yield context
                return
            finally:
                context.close()
    
    # Если cookies нет или невалидны, выполняем авторизацию
    page = context.new_page()
    login_page = LoginPage(page)
    
    page.goto("https://bll.by/login")
    
    # Получаем данные пользователя из secrets
    secrets_dir = Path(__file__).parent.parent.parent / "secrets"
    user_credentials = _get_user_credentials(secrets_dir, "user")
    
    if user_credentials:
        login_page.login(user_credentials["username"], user_credentials["password"])
        page.wait_for_timeout(2000)
        save_user_cookie(context, "user")
    
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def auth_page(authenticated_admin) -> Generator[Page, None, None]:
    """
    Фикстура для страницы с авторизованным администратором.
    
    Комбинирует authenticated_admin с созданием страницы.
    Удобно когда нужна готовая страница с авторизацией.
    
    Args:
        authenticated_admin: Контекст с авторизованным администратором
        
    Yields:
        Page: Готовая страница с авторизацией
        
    Example:
        def test_admin_dashboard(auth_page):
            auth_page.goto("/admin/dashboard")
            # Проверяем элементы дашборда
    """
    page = authenticated_admin.new_page()
    try:
        yield page
    finally:
        page.close()


def _get_user_credentials(secrets_dir: Path, user_type: str) -> Optional[dict]:
    """
    Вспомогательная функция для получения учетных данных пользователя.
    
    Читает файл с тестовыми пользователями и возвращает данные 
    для указанного типа пользователя.
    
    Args:
        secrets_dir: Путь к папке с секретными данными
        user_type: Тип пользователя ("admin", "user", "moderator")
        
    Returns:
        dict: Словарь с ключами "username" и "password" или None
        
    Note:
        Эта функция предполагает наличие файла test_users.csv в папке secrets
        с колонками username, password, role
    """
    import csv
    
    test_users_file = secrets_dir / "test_users.csv"
    
    if not test_users_file.exists():
        print(f"Файл с тестовыми пользователями не найден: {test_users_file}")
        return None
    
    try:
        with open(test_users_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get('role', '').lower() == user_type.lower():
                    return {
                        'username': row['username'],
                        'password': row['password']
                    }
    except Exception as e:
        print(f"Ошибка при чтении файла пользователей: {e}")
        return None
    
    print(f"Пользователь типа '{user_type}' не найден в файле test_users.csv")
    return None


# Дополнительные удобные фикстуры

@pytest.fixture(scope="function")
def quick_auth(browser: Browser):
    """
    Фикстура для быстрой авторизации любым пользователем.
    
    Принимает имя пользователя как параметр и пытается
    загрузить его cookies или выполнить авторизацию.
    
    Returns:
        function: Функция для авторизации по имени пользователя
        
    Example:
        def test_something(quick_auth):
            context = quick_auth("moderator")
            page = context.new_page()
            # ... логика теста
    """
    def _auth(username: str) -> BrowserContext:
        context = browser.new_context()
        
        if load_user_cookie(context, username):
            page = context.new_page()
            page.goto("https://bll.by/")
            
            if check_cookie_validity(context, username):
                return context
        
        # Если cookies нет, нужна ручная авторизация
        print(f"Cookies для пользователя '{username}' не найдены или невалидны")
        print("Требуется ручная авторизация или создание cookies")
        
        return context
    
    return _auth
