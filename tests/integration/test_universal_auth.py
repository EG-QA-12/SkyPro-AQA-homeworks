"""
Универсальный модуль для тестирования авторизации через куки.

Содержит функции, которые могут быть использованы для любого типа пользователя:
- Обычного пользователя
- Модератора
- Администратора
"""
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import pytest

from src.config import config
from src.auth import load_cookies
from src.user_manager import UserManager


# Настраиваем логгер
logger = logging.getLogger(__name__)


def get_user_by_role_or_login(
    role: Optional[str] = None, 
    login: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Получает данные пользователя по роли или логину.
    
    Args:
        role: Роль пользователя ('admin', 'moderator', 'user')
        login: Логин пользователя
        
    Returns:
        dict: Словарь с данными пользователя или None, если пользователь не найден
    """
    user_manager = UserManager()
    
    if login:
        return user_manager.get_user(login=login)
    elif role:
        return user_manager.get_user_by_role(role)
    
    return None


def get_cookie_path_for_user(user: Union[str, Dict[str, Any]]) -> Path:
    """
    Формирует путь к файлу кук для пользователя.
    
    Args:
        user: Логин пользователя или словарь с данными пользователя
        
    Returns:
        Path: Путь к файлу кук
    """
    if isinstance(user, dict):
        login = user.get('login') or user.get('username')
    else:
        login = user
        
    return config.COOKIES_PATH.parent / f"{login}_cookies.json"


def find_user_cookies_file(login: Optional[str] = None, role: Optional[str] = None) -> Tuple[Optional[str], Optional[Path]]:
    """
    Находит файл кук для пользователя по логину или роли.
    
    Args:
        login: Логин пользователя
        role: Роль пользователя
        
    Returns:
        tuple: (логин, путь к файлу кук) или (None, None), если файл не найден
    """
    cookies_dir = config.COOKIES_PATH.parent
    
    # Если указан логин, проверяем наличие файла кук для этого пользователя
    if login:
        cookies_file = cookies_dir / f"{login}_cookies.json"
        if cookies_file.exists():
            return login, cookies_file
    
    # Если указана роль, ищем соответствующие файлы кук
    if role:
        # Шаблоны имен файлов для разных ролей
        role_patterns = {
            'admin': ['admin_cookies.json', 'administrator_cookies.json'],
            'moderator': ['moderator_cookies.json', 'moderator_user_cookies.json', 'EvgenQA_cookies.json'],
            'user': ['user_cookies.json']
        }
        
        # Проверяем шаблоны для указанной роли
        if role in role_patterns:
            for pattern in role_patterns[role]:
                if (cookies_dir / pattern).exists():
                    user_login = pattern.replace('_cookies.json', '')
                    return user_login, cookies_dir / pattern
        
        # Ищем пользователя с указанной ролью в базе данных
        user = get_user_by_role_or_login(role=role)
        if user:
            user_login = user.get('login') or user.get('username')
            cookies_file = cookies_dir / f"{user_login}_cookies.json"
            if cookies_file.exists():
                return user_login, cookies_file
    
    # Если ничего не найдено, возвращаем None
    return None, None


def test_authorization_with_cookies(
    login: Optional[str] = None,
    role: Optional[str] = None,
    cookies_file: Optional[Union[str, Path]] = None,
    target_url: Optional[str] = None,
    base_url: Optional[str] = None,
    headless: bool = True,
    check_elements: Optional[List[str]] = None,
    expected_url_contains: Optional[str] = None
) -> bool:
    """
    Универсальная функция для тестирования авторизации через куки.
    
    Args:
        login: Логин пользователя
        role: Роль пользователя ('admin', 'moderator', 'user')
        cookies_file: Путь к файлу кук
        target_url: URL, на который нужно перейти после авторизации
        base_url: Базовый URL сайта
        headless: Запускать браузер в headless режиме
        check_elements: Список локаторов элементов, которые должны присутствовать на странице
        expected_url_contains: Строка, которая должна содержаться в URL после авторизации
        
    Returns:
        bool: True, если авторизация прошла успешно
    """
    # Настраиваем значения по умолчанию
    if target_url is None:
        target_url = config.TARGET_URL
    if base_url is None:
        base_url = config.BASE_URL
    
    # Если путь к файлу кук не указан, пытаемся найти его по логину или роли
    if cookies_file is None:
        user_login, cookies_path = find_user_cookies_file(login, role)
        if user_login and cookies_path:
            login = user_login
            cookies_file = cookies_path
        else:
            print(f"❌ Не найден файл кук для пользователя: логин={login}, роль={role}")
            return False
    
    # Преобразуем путь в объект Path, если это строка
    if isinstance(cookies_file, str):
        cookies_file = Path(cookies_file)
    
    print(f"🍪 Тестирование авторизации через куки")
    print(f"👤 Пользователь: {login or role or 'неизвестен'}")
    print(f"📁 Файл кук: {cookies_file}")
    
    if not cookies_file.exists():
        print(f"❌ Файл кук не найден: {cookies_file}")
        return False
    
    try:
        with sync_playwright() as p:
            print(f"🌐 Запуск браузера (headless: {headless})...")
            browser = p.chromium.launch(headless=headless)
            
            # Проверка авторизации через куки
            result = check_cookie_authentication(
                browser, 
                cookies_file, 
                target_url, 
                check_elements, 
                expected_url_contains
            )
            
            browser.close()
            return result
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании авторизации через куки: {e}")
        logger.error(f"Ошибка при тестировании авторизации через куки: {e}", exc_info=True)
        return False


def check_cookie_authentication(
    browser: Browser, 
    cookies_file: Path, 
    target_url: str,
    check_elements: Optional[List[str]] = None,
    expected_url_contains: Optional[str] = None
) -> bool:
    """
    Проверяет авторизацию через куки.
    
    Args:
        browser: Экземпляр браузера Playwright
        cookies_file: Путь к файлу кук
        target_url: URL, на который нужно перейти после авторизации
        check_elements: Список локаторов элементов, которые должны присутствовать на странице
        expected_url_contains: Строка, которая должна содержаться в URL после авторизации
        
    Returns:
        bool: True, если авторизация прошла успешно
    """
    try:
        # Загружаем куки
        cookies = load_cookies(cookies_file)
        if not cookies:
            print(f"❌ Не удалось загрузить куки из {cookies_file}")
            return False
        
        print(f"📊 Загружено {len(cookies)} кук")
        
        # Создаем новый контекст и добавляем куки
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        
        # Переходим на целевую страницу
        print(f"🔗 Переход на целевую страницу: {target_url}")
        page.goto(target_url, timeout=30000)
        
        # Проверяем успешную авторизацию
        if "/login" in page.url:
            print(f"❌ Ошибка авторизации через куки. Произошел редирект на страницу логина.")
            # Делаем скриншот для отладки
            page.screenshot(path="auth_failed.png")
            print(f"📸 Скриншот сохранен: auth_failed.png")
            return False
        
        # Проверяем URL, если указано ожидаемое содержимое
        if expected_url_contains and expected_url_contains not in page.url:
            print(f"❌ URL после авторизации не содержит ожидаемую строку: {expected_url_contains}")
            print(f"   Текущий URL: {page.url}")
            return False
        
        # Проверяем наличие элементов на странице
        if check_elements:
            all_elements_found = True
            for selector in check_elements:
                try:
                    element_count = page.locator(selector).count()
                    if element_count > 0:
                        print(f"✅ Найден элемент: {selector}")
                    else:
                        print(f"❌ Элемент не найден: {selector}")
                        all_elements_found = False
                except Exception as e:
                    print(f"❌ Ошибка при поиске элемента {selector}: {e}")
                    all_elements_found = False
            
            if not all_elements_found:
                print("❌ Не все ожидаемые элементы найдены на странице")
                # Делаем скриншот для отладки
                page.screenshot(path="missing_elements.png")
                print(f"📸 Скриншот сохранен: missing_elements.png")
                return False
        
        print("✅ Авторизация через куки прошла успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке авторизации через куки: {e}")
        logger.error(f"Ошибка при проверке авторизации через куки: {e}", exc_info=True)
        return False


# Специализированные функции для разных типов пользователей

def test_user_authentication(login: Optional[str] = None, headless: bool = True) -> bool:
    """
    Тестирует авторизацию обычного пользователя через куки.
    
    Args:
        login: Логин пользователя (по умолчанию используется USER_LOGIN из config)
        headless: Запускать браузер в headless режиме
        
    Returns:
        bool: True, если авторизация прошла успешно
    """
    if login is None:
        login = config.USER_LOGIN
    
    # Элементы, характерные для авторизованного пользователя
    user_elements = [
        "a:has-text('Профиль')",
        "a:has-text('Выход')",
        "a:has-text('Мои заказы')",
        "div.user-profile",
        "[href*='profile']",
        "[href*='logout']"
    ]
    
    return test_authorization_with_cookies(
        login=login,
        role="user",
        target_url=config.TARGET_URL,
        headless=headless,
        check_elements=user_elements
    )


def test_moderator_authentication(login: Optional[str] = None, headless: bool = True) -> bool:
    """
    Тестирует авторизацию модератора через куки.
    
    Args:
        login: Логин модератора (по умолчанию используется MODERATOR_LOGIN из config)
        headless: Запускать браузер в headless режиме
        
    Returns:
        bool: True, если авторизация прошла успешно
    """
    if login is None:
        login = config.MODERATOR_LOGIN
    
    # Элементы, характерные для модератора
    moderator_elements = [
        "a:has-text('Панель модерации')",
        "a:has-text('Модерация')",
        "a:has-text('Администрирование')",
        "a:has-text('Управление')",
        "a:has-text('Admin')",
        "a:has-text('Админ')",
        "div.moderator-panel",
        "div.admin-panel",
        "div.dashboard",
        "[href*='moderation']",
        "[href*='admin']",
        "[href*='dashboard']",
        "[href*='control']"
    ]
    
    return test_authorization_with_cookies(
        login=login,
        role="moderator",
        target_url=config.TARGET_URL,
        headless=headless,
        check_elements=moderator_elements
    )


def test_admin_authentication(login: Optional[str] = None, headless: bool = True) -> bool:
    """
    Тестирует авторизацию администратора через куки.
    
    Args:
        login: Логин администратора (по умолчанию используется ADMIN_LOGIN из config)
        headless: Запускать браузер в headless режиме
        
    Returns:
        bool: True, если авторизация прошла успешно
    """
    if login is None:
        login = config.ADMIN_LOGIN
    
    # Элементы, характерные для администратора
    admin_elements = [
        "a:has-text('Панель администратора')",
        "a:has-text('Администрирование')",
        "a:has-text('Admin')",
        "a:has-text('Админ')",
        "div.admin-panel",
        "div.dashboard",
        "[href*='admin']",
        "[href*='dashboard']"
    ]
    
    return test_authorization_with_cookies(
        login=login,
        role="admin",
        target_url=config.TARGET_URL,
        headless=headless,
        check_elements=admin_elements
    )


# Pytest фикстуры для использования в тестах

@pytest.fixture
def auth_user(request):
    """
    Фикстура для авторизации пользователя через куки.
    
    Параметры:
        request.param: Логин пользователя или роль
        
    Пример использования:
    
    @pytest.mark.parametrize("auth_user", ["user1", "admin", "moderator"], indirect=True)
    def test_something(auth_user):
        # auth_user содержит авторизованный контекст страницы
        assert auth_user.url.startswith("https://ca.bll.by")
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        param = request.param
        login = None
        role = None
        
        # Определяем, что передано - логин или роль
        if param in ["admin", "moderator", "user"]:
            role = param
        else:
            login = param
            
        # Находим куки для пользователя
        user_login, cookies_path = find_user_cookies_file(login, role)
        
        if not (user_login and cookies_path and cookies_path.exists()):
            pytest.skip(f"Куки для пользователя {login or role} не найдены")
            
        # Загружаем куки
        cookies = load_cookies(cookies_path)
        if not cookies:
            pytest.skip(f"Не удалось загрузить куки из {cookies_path}")
            
        # Создаем контекст с куками
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        
        # Переходим на целевую страницу
        page.goto(config.TARGET_URL, timeout=30000)
        
        # Проверяем, что авторизация прошла успешно
        if "/login" in page.url:
            pytest.skip(f"Авторизация через куки не удалась, редирект на страницу логина")
            
        # Yield возвращает страницу для использования в тесте
        yield page
        
        # Закрываем браузер после теста
        browser.close()
