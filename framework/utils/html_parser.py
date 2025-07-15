"""
Парсер HTML для поиска локаторов авторизации в SSO тестах.

Обеспечивает надежную проверку состояния авторизации пользователя
через анализ HTML контента без использования браузера.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class AuthLocators:
    """Константы локаторов для проверки состояния авторизации."""
    
    # Локаторы неавторизованного состояния (кнопка "Войти")
    UNAUTHENTICATED_SELECTORS = [
        'a.top-nav__item.top-nav__ent',  # Основной селектор кнопки "Войти"
        'a[href*="login"]',              # Любая ссылка на логин
        '.top-nav__ent',                 # Класс входа
    ]
    
    # Локаторы авторизованного состояния (профиль пользователя)
    AUTHENTICATED_SELECTORS = [
        'a#myProfile_id',                # Основной ID профиля
        'a.top-nav__item.top-nav__profile', # Класс профиля
        '.user-in__nick',                # Никнейм пользователя
        'a[href*="profile"]',            # Ссылка на профиль
        '.profile-menu__link-1',         # Меню профиля
    ]
    
    # Текстовые маркеры для дополнительной проверки
    UNAUTHENTICATED_TEXT_MARKERS = ['Войти', 'Вход', 'Авторизация', 'Login']
    AUTHENTICATED_TEXT_MARKERS = ['Мой профиль', 'Профиль', 'Выйти', 'Выход', 'Logout']


class HTMLAuthChecker:
    """
    Анализатор HTML для определения состояния авторизации пользователя.
    
    Проверяет наличие специфических локаторов и текстовых маркеров
    для определения авторизован ли пользователь на странице.
    """
    
    def __init__(self, html_content: str):
        """
        Инициализирует анализатор HTML.
        
        Args:
            html_content: HTML контент страницы для анализа
        """
        self.html_content = html_content
        self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def is_unauthenticated(self) -> Tuple[bool, List[str]]:
        """
        Проверяет что пользователь НЕ авторизован.
        
        Returns:
            Кортеж (найдены_маркеры_неавторизации, список_найденных_элементов)
        """
        found_elements = []
        
        # Проверяем локаторы неавторизованного состояния
        for selector in AuthLocators.UNAUTHENTICATED_SELECTORS:
            try:
                elements = self.soup.select(selector)
                if elements:
                    # Проверяем содержимое элементов на текстовые маркеры
                    for element in elements:
                        element_text = element.get_text(strip=True)
                        if any(marker in element_text for marker in AuthLocators.UNAUTHENTICATED_TEXT_MARKERS):
                            found_elements.append(f"Селектор: {selector}, Текст: '{element_text}'")
                            logger.debug(f"Найден маркер неавторизации: {selector} с текстом '{element_text}'")
            except Exception as e:
                logger.warning(f"Ошибка при проверке селектора {selector}: {e}")
        
        # Дополнительная проверка по тексту на всей странице
        page_text = self.soup.get_text()
        for marker in AuthLocators.UNAUTHENTICATED_TEXT_MARKERS:
            if marker in page_text:
                # Ищем контекст вокруг маркера
                context = self._find_text_context(page_text, marker, 50)
                found_elements.append(f"Текстовый маркер: '{marker}' в контексте: '{context}'")
                logger.debug(f"Найден текстовый маркер неавторизации: '{marker}'")
        
        is_unauthenticated = len(found_elements) > 0
        
        if is_unauthenticated:
            logger.info(f"Обнаружено неавторизованное состояние: {len(found_elements)} маркеров")
        else:
            logger.info("Маркеры неавторизованного состояния не найдены")
        
        return is_unauthenticated, found_elements
    
    def is_authenticated(self) -> Tuple[bool, List[str]]:
        """
        Проверяет что пользователь авторизован.
        
        Returns:
            Кортеж (найдены_маркеры_авторизации, список_найденных_элементов)
        """
        found_elements = []
        
        # Проверяем локаторы авторизованного состояния
        for selector in AuthLocators.AUTHENTICATED_SELECTORS:
            try:
                elements = self.soup.select(selector)
                if elements:
                    for element in elements:
                        element_text = element.get_text(strip=True)
                        # Для авторизованного состояния достаточно найти элемент
                        # Но дополнительно проверяем на известные текстовые маркеры
                        found_elements.append(f"Селектор: {selector}, Текст: '{element_text}'")
                        logger.debug(f"Найден маркер авторизации: {selector} с текстом '{element_text}'")
            except Exception as e:
                logger.warning(f"Ошибка при проверке селектора {selector}: {e}")
        
        # Дополнительная проверка по тексту авторизации
        page_text = self.soup.get_text()
        for marker in AuthLocators.AUTHENTICATED_TEXT_MARKERS:
            if marker in page_text:
                context = self._find_text_context(page_text, marker, 50)
                found_elements.append(f"Текстовый маркер: '{marker}' в контексте: '{context}'")
                logger.debug(f"Найден текстовый маркер авторизации: '{marker}'")
        
        is_authenticated = len(found_elements) > 0
        
        if is_authenticated:
            logger.info(f"Обнаружено авторизованное состояние: {len(found_elements)} маркеров")
        else:
            logger.info("Маркеры авторизованного состояния не найдены")
        
        return is_authenticated, found_elements
    
    def get_auth_status_summary(self) -> Dict[str, any]:
        """
        Получает полный анализ состояния авторизации.
        
        Returns:
            Словарь с детальной информацией о состоянии авторизации
        """
        is_unauth, unauth_markers = self.is_unauthenticated()
        is_auth, auth_markers = self.is_authenticated()
        
        # Определяем итоговый статус
        if is_auth and not is_unauth:
            status = "authenticated"
        elif is_unauth and not is_auth:
            status = "unauthenticated"
        elif is_auth and is_unauth:
            status = "ambiguous"  # Найдены маркеры обоих состояний
        else:
            status = "unknown"    # Не найдено маркеров
        
        return {
            'status': status,
            'is_authenticated': is_auth,
            'is_unauthenticated': is_unauth,
            'authenticated_markers': auth_markers,
            'unauthenticated_markers': unauth_markers,
            'page_title': self.soup.title.string if self.soup.title else 'Нет заголовка',
            'page_size': len(self.html_content),
        }
    
    def _find_text_context(self, text: str, marker: str, context_length: int = 50) -> str:
        """
        Находит контекст вокруг текстового маркера.
        
        Args:
            text: Полный текст для поиска
            marker: Маркер для поиска
            context_length: Длина контекста с каждой стороны
            
        Returns:
            Строка с контекстом вокруг маркера
        """
        index = text.find(marker)
        if index == -1:
            return marker
        
        start = max(0, index - context_length)
        end = min(len(text), index + len(marker) + context_length)
        
        context = text[start:end].strip()
        return re.sub(r'\s+', ' ', context)  # Убираем лишние пробелы
    
    def find_specific_element(self, selector: str) -> Optional[str]:
        """
        Ищет конкретный элемент по селектору.
        
        Args:
            selector: CSS селектор для поиска
            
        Returns:
            Текст найденного элемента или None
        """
        try:
            element = self.soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
            return None
        except Exception as e:
            logger.warning(f"Ошибка при поиске элемента {selector}: {e}")
            return None


def check_auth_status(html_content: str) -> Dict[str, any]:
    """
    Удобная функция для быстрой проверки состояния авторизации.
    
    Args:
        html_content: HTML контент для анализа
        
    Returns:
        Словарь с информацией о состоянии авторизации
    """
    checker = HTMLAuthChecker(html_content)
    return checker.get_auth_status_summary()


def validate_sso_response(html_without_cookies: str, html_with_cookies: str) -> Dict[str, any]:
    """
    Валидирует SSO ответы - сравнивает состояние до и после установки кук.
    
    Args:
        html_without_cookies: HTML без кук авторизации
        html_with_cookies: HTML с куками авторизации
        
    Returns:
        Словарь с результатами валидации SSO
    """
    status_without = check_auth_status(html_without_cookies)
    status_with = check_auth_status(html_with_cookies)
    
    # Определяем успешность SSO
    sso_success = (
        status_without['status'] in ['unauthenticated', 'unknown'] and
        status_with['status'] == 'authenticated'
    )
    
    return {
        'sso_success': sso_success,
        'without_cookies': status_without,
        'with_cookies': status_with,
        'analysis': {
            'cookies_changed_auth_state': status_without['status'] != status_with['status'],
            'before_auth': status_without['is_authenticated'],
            'after_auth': status_with['is_authenticated'],
        }
    } 