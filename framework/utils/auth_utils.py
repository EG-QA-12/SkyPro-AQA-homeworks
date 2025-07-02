"""
Утилиты для работы с куками авторизации.

Этот модуль предоставляет функции для сохранения и загрузки cookies
авторизации, что позволяет пропускать шаг входа в систему в тестах.

Преимущества использования:
1. Ускорение выполнения тестов (не нужно каждый раз вводить логин/пароль)
2. Возможность тестировать функциональность для авторизованных пользователей
3. Стабильность тестов (меньше зависимости от UI элементов логина)
4. Централизованное управление сессиями пользователей
5. Легкое переключение между различными ролями в тестах

Functions:
    save_cookie: Сохраняет cookies авторизации в файл
    load_cookie: Загружает cookies из файла в браузерный контекст
    get_cookie_path: Получает путь к файлу с cookies для пользователя
    clear_all_cookies: Очищает все cookies в контексте
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from .cookie_constants import COOKIE_NAME, LOGIN_URL
from playwright.sync_api import BrowserContext
from config.secrets_manager import SecretsManager

logger = logging.getLogger(__name__)


def save_cookie(context: BrowserContext, filename: str) -> None:
    """
    Сохраняет куки указанного контекста в файл.

    Args:
        context: Браузерный контекст Playwright.
        filename: Название файла для сохранения куков.
    """
    # Сохраняем только куку с именем test_joint_session
    cookies = [cookie for cookie in context.cookies() if cookie["name"] == COOKIE_NAME]
    with open(filename, "w") as file:
        json.dump(cookies, file)


def load_cookie(context: BrowserContext, filename: str) -> None:
    """
    Загружает куку test_joint_session из файла и добавляет её в контекст.

    Args:
        context: Браузерный контекст Playwright.
        filename: Название файла с сохранённой кукой.
    """
    with open(filename, 'r') as file:
        cookies = json.load(file)
        # Фильтруем только куки с нужным именем
        target_cookies = [cookie for cookie in cookies if cookie.get("name") == COOKIE_NAME]
        if target_cookies:
            context.add_cookies([target_cookies[0]])


def get_cookie_path(username: str) -> Path:
    """
    Получает путь к файлу с cookies для указанного пользователя.
    
    Теперь cookies сохраняются в централизованной папке cookies/,
    что упрощает управление и поиск файлов.
    
    Args:
        username: Имя пользователя для которого нужен файл cookies
        
    Returns:
        Path: Полный путь к файлу с cookies пользователя
        
    Example:
        >>> path = get_cookie_path("admin")
        >>> print(path)  # D:/Bll_tests/cookies/admin_cookies.json
    """
    # Определяем корневую директорию проекта
    project_root = Path(__file__).parent.parent.parent
    cookies_dir = project_root / "cookies"
    
    # Создаем папку cookies, если её нет
    cookies_dir.mkdir(exist_ok=True)
    
    # Формируем имя файла с cookies
    cookie_filename = f"{username}_cookies.json"
    return cookies_dir / cookie_filename


def save_user_cookie(context: BrowserContext, username: str) -> None:
    """
    Сохраняет cookies пользователя с автоматическим определением пути.
    Теперь использует данные из creds.env для авторизации перед сохранением cookie.
    
    Args:
        context: Браузерный контекст Playwright
        username: Имя пользователя для сохранения cookies
    
    Example:
        >>> save_user_cookie(context, "admin")
        # Cookies сохранятся в cookies/admin_cookies.json
    """
    # Получаем учетные данные из creds.env
    creds = get_auth_credentials()
    
    # Авторизуемся с этими учетными данными
    page = context.new_page()
    page.goto(LOGIN_URL)
    page.fill("#username", creds["username"])
    page.fill("#password", creds["password"])
    page.click("#submit")
    
    # Сохраняем cookies
    cookie_path = get_cookie_path(username)
    save_cookie(context, str(cookie_path))
    logger.info(f"Cookies для пользователя '{username}' сохранены в {cookie_path}")


def load_user_cookie(context: BrowserContext, username: str) -> bool:
    """
    Загружает cookies пользователя с автоматическим определением пути.
    
    Проверяет существование файла с cookies перед загрузкой.
    Это предотвращает ошибки при попытке загрузить несуществующие cookies.
    
    Args:
        context: Браузерный контекст Playwright
        username: Имя пользователя для загрузки cookies
        
    Returns:
        bool: True если cookies успешно загружены, False если файл не найден
        
    Example:
        >>> if load_user_cookie(context, "admin"):
        ...     print("Авторизация через cookies успешна")
        ... else:
        ...     print("Нужна обычная авторизация")
    """
    cookie_path = get_cookie_path(username)
    
    if not cookie_path.exists():
        logger.warning(f"Файл с cookies для пользователя '{username}' не найден: {cookie_path}")
        return False
        
    try:
        load_cookie(context, str(cookie_path))
        logger.info(f"Cookies для пользователя '{username}' успешно загружены")
        return True
    except Exception as e:
        logger.error(f"Ошибка при загрузке cookies для пользователя '{username}': {e}")
        return False


def clear_all_cookies(context: BrowserContext) -> None:
    """
    Очищает все cookies в браузерном контексте.
    
    Полезно для тестов, где нужно имитировать
    неавторизованного пользователя или сброс сессии.
    
    Args:
        context: Браузерный контекст Playwright
    """
    context.clear_cookies()
    logger.debug("Все cookies очищены из браузерного контекста")


def check_cookie_validity(context: BrowserContext, username: str) -> bool:
    """
    Проверяет валидность загруженных cookies.
    
    Проверяет наличие основной cookie авторизации в контексте.
    Это помогает убедиться, что авторизация через cookies прошла успешно.
    
    Args:
        context: Браузерный контекст Playwright
        username: Имя пользователя (для логирования)
        
    Returns:
        bool: True если cookie авторизации найдена, False - если нет
    """
    cookies = context.cookies()
    auth_cookie = next((cookie for cookie in cookies if cookie["name"] == COOKIE_NAME), None)
    
    if auth_cookie:
        logger.debug(f"Cookie авторизации для пользователя '{username}' найдена и валидна")
        return True
    else:
        logger.warning(f"Cookie авторизации для пользователя '{username}' не найдена")
        return False


def list_available_cookies() -> List[str]:
    """
    Получает список всех доступных файлов с cookies.
    
    Полезно для отладки и понимания, какие пользователи
    уже имеют сохраненные сессии.
    
    Returns:
        List[str]: Список имен пользователей с сохраненными cookies
        
    Example:
        >>> users = list_available_cookies()
        >>> print(f"Доступные cookies: {users}")
        # Доступные cookies: ['admin', 'user1', 'moderator']
    """
    project_root = Path(__file__).parent.parent.parent
    cookies_dir = project_root / "cookies"
    
    if not cookies_dir.exists():
        return []
        
    cookie_files = list(cookies_dir.glob("*_cookies.json"))
    usernames = []
    
    for cookie_file in cookie_files:
        # Извлекаем имя пользователя из имени файла
        # Например: admin_cookies.json -> admin
        username = cookie_file.stem.replace("_cookies", "")
        usernames.append(username)
        
    logger.debug(f"Найдены cookies для пользователей: {usernames}")
    return usernames


def get_auth_credentials() -> dict:
    """Получает учетные данные из creds.env через SecretsManager"""
    # Создаем экземпляр SecretsManager чтобы избежать проблем с глобальной инициализацией
    secrets = SecretsManager()
    return {
        "username": secrets.get_required_env("AUTH_USERNAME"),
        "password": secrets.get_required_env("AUTH_PASSWORD")
    }
