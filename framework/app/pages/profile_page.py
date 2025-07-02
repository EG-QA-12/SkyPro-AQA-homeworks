"""
Модуль страницы профиля пользователя.

Содержит класс:
- ProfilePage: Page Object Model (POM) для страницы профиля пользователя.
"""
import logging
from typing import Optional

from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class ProfilePage:
    """
    Класс для работы со страницей профиля пользователя.
    
    Args:
        page: Экземпляр страницы Playwright.
    """
    
    def __init__(self, page: Page):
        self.page = page
        # Локатор для никнейма пользователя на странице профиля
        self.user_nickname_locator = self.page.locator("div.user-in__nick")
        # Альтернативные локаторы для повышения надежности
        self.profile_link_locator = self.page.locator("a[href*='/user/profile']")
        self.community_link_pattern = "Я в Сообществе:"

    def get_user_nickname(self, timeout: int = 10000) -> Optional[str]:
        """
        Получает никнейм пользователя со страницы профиля.
        
        Args:
            timeout: Время ожидания элемента в миллисекундах.
            
        Returns:
            str: Никнейм пользователя или None, если элемент не найден.
        """
        try:
            logger.debug("Ожидание появления элемента с никнеймом пользователя")
            self.user_nickname_locator.wait_for(state="visible", timeout=timeout)
            
            nickname = self.user_nickname_locator.text_content()
            if nickname:
                nickname = nickname.strip()
                logger.info(f"Получен никнейм пользователя: {nickname}")
                return nickname
            else:
                logger.warning("Элемент с никнеймом найден, но текст пустой")
                return None
                
        except PlaywrightTimeoutError:
            logger.error(f"Элемент с никнеймом не найден в течение {timeout}ms")
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении никнейма: {e}")
            return None

    def is_user_logged_in(self, expected_username: str, timeout: int = 10000) -> bool:
        """
        Проверяет, что пользователь успешно авторизован.
        
        Сравнивает никнейм на странице с ожидаемым логином пользователя.
        
        Args:
            expected_username: Ожидаемый логин пользователя.
            timeout: Время ожидания элемента в миллисекундах.
            
        Returns:
            bool: True, если пользователь авторизован с правильным логином.
        """
        try:
            logger.info(f"Проверка авторизации для пользователя: {expected_username}")
            
            # Получаем никнейм со страницы
            actual_nickname = self.get_user_nickname(timeout)
            
            if actual_nickname is None:
                logger.error("Не удалось получить никнейм со страницы")
                return False
            
            # Убираем лишние пробелы для корректного сравнения
            expected_username_clean = expected_username.strip()
            actual_nickname_clean = actual_nickname.strip()
            
            # Сравниваем логины
            is_match = expected_username_clean == actual_nickname_clean
            
            if is_match:
                logger.info(f"✅ Авторизация подтверждена. Ожидаемый логин: '{expected_username_clean}', "
                           f"фактический: '{actual_nickname_clean}'")
            else:
                logger.error(f"❌ Авторизация НЕ подтверждена. Ожидаемый логин: '{expected_username_clean}', "
                            f"фактический: '{actual_nickname_clean}'")
            
            return is_match
            
        except Exception as e:
            logger.error(f"Ошибка при проверке авторизации: {e}")
            return False

    def wait_for_profile_page_load(self, timeout: int = 15000) -> bool:
        """
        Ожидает полной загрузки страницы профиля.
        
        Args:
            timeout: Время ожидания в миллисекундах.
            
        Returns:
            bool: True, если страница загружена успешно.
        """
        try:
            logger.debug("Ожидание загрузки страницы профиля")
            
            # Ожидаем загрузки основных элементов страницы
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            
            # Проверяем, что мы на странице профиля
            if "/user/profile" not in self.page.url:
                logger.warning(f"Текущий URL не содержит '/user/profile': {self.page.url}")
                return False
            
            # Ожидаем появления ключевых элементов
            self.user_nickname_locator.wait_for(state="attached", timeout=5000)
            
            logger.info("Страница профиля успешно загружена")
            return True
            
        except PlaywrightTimeoutError:
            logger.error(f"Страница профиля не загрузилась в течение {timeout}ms")
            return False
        except Exception as e:
            logger.error(f"Ошибка при ожидании загрузки страницы профиля: {e}")
            return False

    def navigate_to_profile(self, base_url: str = "https://ca.bll.by") -> bool:
        """
        Переходит на страницу профиля пользователя.
        
        Args:
            base_url: Базовый URL сайта.
            
        Returns:
            bool: True, если переход выполнен успешно.
        """
        try:
            profile_url = f"{base_url}/user/profile"
            logger.info(f"Переход на страницу профиля: {profile_url}")
            
            self.page.goto(profile_url, wait_until="domcontentloaded", timeout=15000)
            
            # Проверяем, что переход выполнен успешно
            if self.wait_for_profile_page_load():
                logger.info("Успешный переход на страницу профиля")
                return True
            else:
                logger.error("Не удалось подтвердить загрузку страницы профиля")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при переходе на страницу профиля: {e}")
            return False

    def get_current_url(self) -> str:
        """
        Возвращает текущий URL страницы.
        
        Returns:
            str: Текущий URL.
        """
        return self.page.url

    def take_screenshot(self, path: str = "profile_page_debug.png") -> bool:
        """
        Делает скриншот страницы для отладки.
        
        Args:
            path: Путь для сохранения скриншота.
            
        Returns:
            bool: True, если скриншот сделан успешно.
        """
        try:
            self.page.screenshot(path=path)
            logger.info(f"Скриншот сохранен: {path}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при создании скриншота: {e}")
            return False
