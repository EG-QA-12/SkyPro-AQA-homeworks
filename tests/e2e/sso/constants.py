"""
Константы для SSO тестирования.

Содержит все домены экосистемы Bll и локаторы для проверки авторизации.
"""
from __future__ import annotations

from typing import List

# === ДОМЕНЫ ДЛЯ SSO ТЕСТИРОВАНИЯ ===

SSO_DOMAINS: List[str] = [
    "https://bll.by/",
    "https://ca.bll.by/", 
    "https://expert.bll.by/",
    "https://cp.bll.by/",
    "https://gz.bll.by/",
    "https://bonus.bll.by/"
]

# === ЛОКАТОРЫ СОСТОЯНИЯ АВТОРИЗАЦИИ ===

class SSOLocators:
    """CSS селекторы для проверки состояния авторизации через requests."""
    
    # Локаторы неавторизованного состояния (кнопка "Войти")
    UNAUTHENTICATED = {
        # Основной локатор кнопки "Войти" 
        "login_button": 'a.top-nav__item.top-nav__ent',
        
        # Альтернативные локаторы входа
        "login_link": 'a[href*="login"]',
        "entry_class": '.top-nav__ent',
        
        # Ожидаемые ссылки на авторизацию
        "ca_login_link": 'a[href="https://ca.bll.by/login?return=https%3A%2F%2Fbll.by%2F"]'
    }
    
    # Локаторы авторизованного состояния (профиль пользователя)
    AUTHENTICATED = {
        # Основной локатор профиля (по требованию пользователя)
        "profile_button": 'a#myProfile_id',
        
        # Альтернативные локаторы профиля
        "profile_class": 'a.top-nav__item.top-nav__profile',
        "user_nick": '.user-in__nick',
        "profile_link": 'a[href*="profile"]',
        "profile_menu": '.profile-menu__link-1',
        
        # Ссылки профиля и данных
        "user_data_link": 'a[href="https://ca.bll.by/user/profile"]'
    }

# === ТЕКСТОВЫЕ МАРКЕРЫ ===

class SSOTextMarkers:
    """Текстовые маркеры для дополнительной валидации состояния."""
    
    # Маркеры неавторизованного состояния
    UNAUTHENTICATED_TEXTS = [
        "Войти",
        "Вход", 
        "Авторизация",
        "Login"
    ]
    
    # Маркеры авторизованного состояния
    AUTHENTICATED_TEXTS = [
        "Мой профиль",
        "Профиль",
        "Мои данные",
        "Выйти",
        "Выход",
        "Logout",
        "admin",  # Часто встречается в профиле админа
        "user",   # Общий маркер пользователя
    ]

# === НАСТРОЙКИ ТЕСТИРОВАНИЯ ===

class SSOTestConfig:
    """Настройки для SSO тестов."""
    
    # Таймауты
    REQUEST_TIMEOUT = 15  # Таймаут HTTP запросов (секунды)
    
    # Настройки retry
    MAX_RETRIES = 3
    RETRY_BACKOFF_FACTOR = 1
    
    # Настройки куки
    COOKIE_NAME = "test_joint_session"  # Основная кука авторизации
    COOKIE_DOMAIN = ".bll.by"          # Домен кук
    
    # Пути
    COOKIES_DIR = "cookies"            # Папка с файлами кук
    
    # Ожидаемые HTTP статусы
    EXPECTED_STATUS_CODES = [200, 301, 302]  # Успешные коды ответов

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def get_domain_name(url: str) -> str:
    """
    Извлекает имя домена из URL для логирования.
    
    Args:
        url: Полный URL
        
    Returns:
        Короткое имя домена (например, "bll.by")
    """
    if "bll.by" in url:
        if "ca.bll.by" in url:
            return "ca.bll.by"
        elif "expert.bll.by" in url:
            return "expert.bll.by"
        elif "cp.bll.by" in url:
            return "cp.bll.by"
        elif "gz.bll.by" in url:
            return "gz.bll.by"
        elif "bonus.bll.by" in url:
            return "bonus.bll.by"
        else:
            return "bll.by"
    return url

def get_domain_display_name(url: str) -> str:
    """
    Получает читаемое имя домена для отчетов.
    
    Args:
        url: URL домена
        
    Returns:
        Читаемое название домена
    """
    domain_names = {
        "https://bll.by/": "Основной сайт (bll.by)",
        "https://ca.bll.by/": "Центр авторизации (ca.bll.by)",
        "https://expert.bll.by/": "Экспертный раздел (expert.bll.by)",
        "https://cp.bll.by/": "Панель управления (cp.bll.by)",
        "https://gz.bll.by/": "Госзакупки (gz.bll.by)",
        "https://bonus.bll.by/": "Бонусная система (bonus.bll.by)"
    }
    
    return domain_names.get(url, get_domain_name(url)) 