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
# Импорт SecretsManager перенесен внутрь функций для избежания циклических импортов

logger = logging.getLogger(__name__)


def save_cookie(context: BrowserContext, filename: str) -> None:
    """
    Сохраняет cookie авторизации из браузерного контекста в файл.

    Args:
        context (BrowserContext): Контекст браузера Playwright, из которого извлекаются cookies.
        filename (str): Имя файла, в который будут сохранены cookies.

    Returns:
        None

    Raises:
        IOError: Если не удалось записать файл.
    
    Example:
        >>> save_cookie(context, "admin_cookies.json")
    """
    cookies: List[Dict[str, Any]] = [cookie for cookie in context.cookies() if cookie["name"] == COOKIE_NAME]
    with open(filename, "w") as file:
        json.dump(cookies, file)


def load_cookie(context: BrowserContext, filename: str) -> None:
    """
    Загружает cookie test_joint_session из файла и добавляет её в контекст.

    Args:
        context (BrowserContext): Браузерный контекст Playwright.
        filename (str): Название файла с сохранённой кукой.

    Returns:
        None

    Raises:
        FileNotFoundError: Если файл не найден.
        json.JSONDecodeError: Если файл не является корректным JSON.
    """
    with open(filename, 'r') as file:
        cookies: List[Dict[str, Any]] = json.load(file)
        target_cookies: List[Dict[str, Any]] = [cookie for cookie in cookies if cookie.get("name") == COOKIE_NAME]
        if target_cookies:
            context.add_cookies([target_cookies[0]])


def get_cookie_path(username: str) -> Path:
    """
    Получает путь к файлу с cookies для указанного пользователя.
    
    Теперь cookies сохраняются в централизованной папке cookies/,
    что упрощает управление и поиск файлов.
    
    Args:
        username (str): Имя пользователя для которого нужен файл cookies
        
    Returns:
        Path: Полный путь к файлу с cookies пользователя
        
    Example:
        >>> path = get_cookie_path("admin")
        >>> print(path)  # D:/Bll_tests/cookies/admin_cookies.json
    """
    project_root: Path = Path(__file__).parent.parent.parent
    cookies_dir: Path = project_root / "cookies"
    cookies_dir.mkdir(exist_ok=True)
    cookie_filename: str = f"{username}_cookies.json"
    return cookies_dir / cookie_filename


def save_user_cookie(context: BrowserContext, username: str) -> None:
    """
    Сохраняет cookies пользователя с автоматическим определением пути.
    Теперь использует данные из creds.env для авторизации перед сохранением cookie.
    
    Args:
        context (BrowserContext): Браузерный контекст Playwright
        username (str): Имя пользователя для сохранения cookies
    
    Returns:
        None
    
    Example:
        >>> save_user_cookie(context, "admin")
        # Cookies сохранятся в cookies/admin_cookies.json
    """
    creds: Dict[str, str] = get_auth_credentials()
    page = context.new_page()
    page.goto(LOGIN_URL)
    page.fill("#username", creds["username"])
    page.fill("#password", creds["password"])
    page.click("#submit")
    cookie_path: Path = get_cookie_path(username)
    save_cookie(context, str(cookie_path))
    logger.info(f"Cookies для пользователя '{username}' сохранены в {cookie_path}")


def load_user_cookie(context: BrowserContext, username: str) -> bool:
    """
    Загружает cookies пользователя с автоматическим определением пути.
    
    Проверяет существование файла с cookies перед загрузкой.
    Это предотвращает ошибки при попытке загрузить несуществующие cookies.
    
    Args:
        context (BrowserContext): Браузерный контекст Playwright
        username (str): Имя пользователя для загрузки cookies
        
    Returns:
        bool: True если cookies успешно загружены, False если файл не найден
        
    Example:
        >>> if load_user_cookie(context, "admin"):
        ...     print("Авторизация через cookies успешна")
        ... else:
        ...     print("Нужна обычная авторизация")
    """
    cookie_path: Path = get_cookie_path(username)
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
        context (BrowserContext): Браузерный контекст Playwright
    
    Returns:
        None
    """
    context.clear_cookies()
    logger.debug("Все cookies очищены из браузерного контекста")


def check_cookie_validity(context: BrowserContext, username: str) -> bool:
    """
    Проверяет валидность загруженных cookies.
    
    Проверяет наличие основной cookie авторизации в контексте.
    Это помогает убедиться, что авторизация через cookies прошла успешно.
    
    Args:
        context (BrowserContext): Браузерный контекст Playwright
        username (str): Имя пользователя (для логирования)
        
    Returns:
        bool: True если cookie авторизации найдена, False - если нет
    """
    cookies: List[Dict[str, Any]] = context.cookies()
    auth_cookie: Optional[Dict[str, Any]] = next((cookie for cookie in cookies if cookie["name"] == COOKIE_NAME), None)
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
        List[str]: Список имён файлов с cookies
    """
    project_root: Path = Path(__file__).parent.parent.parent
    cookies_dir: Path = project_root / "cookies"
    if not cookies_dir.exists():
        return []
    return [f.name for f in cookies_dir.glob("*_cookies.json") if f.is_file()]


def get_auth_credentials() -> Dict[str, str]:
    """
    Получает учетные данные для авторизации из файла creds.env.
    
    Returns:
        Dict[str, str]: Словарь с ключами 'username' и 'password'.
    
    Raises:
        FileNotFoundError: Если файл creds.env не найден.
        KeyError: Если в файле отсутствуют необходимые ключи.
    """
    # Импортируем здесь, чтобы избежать циклических импортов
    from config.secrets_manager import get_secret
    username: str = get_secret("username")
    password: str = get_secret("password")
    return {"username": username, "password": password}
