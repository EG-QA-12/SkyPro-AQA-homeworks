"""
Модуль страницы панели модератора.

Содержит класс:
- ModeratorDashboardPage: Page Object Model (POM) для страницы панели управления модератора.
"""
import logging
from typing import Optional, List

from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from framework.utils.url_utils import add_allow_session_param, is_headless

logger = logging.getLogger(__name__)


class ModeratorDashboardPage:
    """
    Класс для работы со страницей панели управления модератора.
    
    Args:
        page: Экземпляр страницы Playwright.
    """
    
    def __init__(self, page: Page):
        self.page = page
        # Локаторы для элементов панели модератора
        self.moderator_menu_locator = self.page.locator("a.moderator-menu")
        self.items_for_moderation_locator = self.page.locator("div.items-for-moderation")
        self.moderation_table_locator = self.page.locator("table.moderation-table")
        self.approve_buttons_locator = self.page.locator("button.approve-button, button[data-action='approve']")
        self.reject_buttons_locator = self.page.locator("button.reject-button, button[data-action='reject']")
        # Альтернативные локаторы для определения доступа модератора
        self.moderation_indicators = [
            "a:has-text('Панель модерации')",
            "a:has-text('Модерация')",
            "div.moderator-panel",
            "div.mod-controls",
            "[href*='moderation']",
            "a:has-text('Администрирование')",
            "a:has-text('Управление')",
            "a:has-text('Admin')",
            "a:has-text('Админ')",
            "div.admin-panel",
            "div.dashboard",
            "[href*='admin']",
            "[href*='dashboard']",
            "[href*='control']",
        ]
    
    def navigate_to_dashboard(self, base_url: str = None) -> bool:
        """
        Переходит на страницу панели модератора.
        
        Args:
            base_url: Базовый URL сайта (по умолчанию берется из config).
            
        Returns:
            bool: True, если переход выполнен успешно.
        """
        from projects.auth_management.config import config
        
        if base_url is None:
            # Проверяем несоответствие между BASE_URL и LOGIN_URL/TARGET_URL
            if hasattr(config, 'TARGET_URL') and config.TARGET_URL:
                # Предпочитаем использовать TARGET_URL в качестве базового,
                # так как он, скорее всего, содержит правильный домен
                base_url_parts = config.TARGET_URL.split('/')
                if len(base_url_parts) >= 3:  # Проверяем, что URL имеет хотя бы протокол и домен
                    base_url = f"{base_url_parts[0]}//{base_url_parts[2]}"
                else:
                    base_url = config.BASE_URL
            else:
                base_url = config.BASE_URL
                
        try:
            # Проверяем путь к панели модератора
            possible_paths = [
                "/moderation/dashboard",
                "/admin",
                "/admin/dashboard",
                "/dashboard",
                "/moderator",
                "/control"
            ]
            
            # Пробуем первый путь
            dashboard_url = f"{base_url}{possible_paths[0]}"
            logger.info(f"Переход на панель модератора: {dashboard_url}")
            
            self.page.goto(add_allow_session_param(dashboard_url, is_headless()), wait_until="domcontentloaded", timeout=15000)
            
            # Проверяем, что переход выполнен успешно
            if self.wait_for_dashboard_load():
                logger.info("Успешный переход на панель модератора")
                return True
            else:
                logger.error("Не удалось подтвердить загрузку панели модератора")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при переходе на панель модератора: {e}")
            return False
    
    def wait_for_dashboard_load(self, timeout: int = 15000) -> bool:
        """
        Ожидает полной загрузки панели модератора.
        
        Args:
            timeout: Время ожидания в миллисекундах.
            
        Returns:
            bool: True, если страница загружена успешно.
        """
        try:
            logger.debug("Ожидание загрузки панели модератора")
            
            # Ожидаем загрузки основных элементов страницы
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            
            # Проверяем, что мы на странице модерации или в административной панели
            if "/moderation" not in self.page.url and "/admin" not in self.page.url:
                logger.warning(f"Текущий URL не содержит путь модерации: {self.page.url}")
                # Попробуем проверить наличие элементов модерации на странице
                return self.has_moderation_elements()
            
            # Пытаемся найти хотя бы один элемент модерации
            if self.has_moderation_elements():
                logger.info("Панель модератора успешно загружена")
                return True
            else:
                logger.warning("Не найдены элементы модерации на странице")
                return False
            
        except PlaywrightTimeoutError:
            logger.error(f"Панель модератора не загрузилась в течение {timeout}ms")
            return False
        except Exception as e:
            logger.error(f"Ошибка при ожидании загрузки панели модератора: {e}")
            return False
    
    def has_moderation_elements(self, timeout: int = 5000) -> bool:
        """
        Проверяет наличие элементов модерации на странице.
        
        Args:
            timeout: Время ожидания в миллисекундах.
            
        Returns:
            bool: True, если найдены элементы модерации.
        """
        try:
            # Перебираем все возможные индикаторы модерации
            for selector in self.moderation_indicators:
                try:
                    if self.page.locator(selector).count(timeout=timeout // len(self.moderation_indicators)) > 0:
                        logger.info(f"Найден элемент модерации: {selector}")
                        return True
                except:
                    continue
            
            # Проверим наличие кнопок одобрения/отклонения
            if self.approve_buttons_locator.count() > 0 or self.reject_buttons_locator.count() > 0:
                logger.info("Найдены кнопки модерации (одобрить/отклонить)")
                return True
                
            logger.warning("Не найдены элементы модерации на странице")
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при проверке элементов модерации: {e}")
            return False
    
    def is_moderator_authorized(self) -> bool:
        """
        Проверяет, авторизован ли пользователь как модератор.
        
        Returns:
            bool: True, если пользователь имеет права модератора.
        """
        try:
            logger.info("Проверка авторизации пользователя как модератора")
            
            # Проверяем доступность элементов модерации
            if self.has_moderation_elements():
                logger.info("✅ Пользователь авторизован как модератор")
                return True
            
            # Пробуем перейти на панель модерации
            dashboard_url = f"{self.get_base_url()}/moderation/dashboard"
            self.page.goto(dashboard_url, wait_until="domcontentloaded", timeout=10000)
            
            # Проверяем, нет ли редиректа или ошибки 403/404
            if "/login" in self.page.url or "403" in self.page.content() or "404" in self.page.content():
                logger.warning("Пользователь не имеет доступа к панели модерации")
                self.take_screenshot("moderator_auth_failed.png")
                return False
            
            # Повторная проверка элементов модерации
            return self.has_moderation_elements()
            
        except Exception as e:
            logger.error(f"Ошибка при проверке авторизации модератора: {e}")
            self.take_screenshot("moderator_auth_error.png")
            return False
    
    def get_moderation_items_count(self) -> int:
        """
        Получает количество элементов для модерации.
        
        Returns:
            int: Количество элементов для модерации.
        """
        try:
            # Пытаемся найти элементы для модерации
            if self.items_for_moderation_locator.count() > 0:
                items_text = self.items_for_moderation_locator.text_content() or ""
                # Извлекаем число из текста (например, "Элементов для модерации: 15")
                import re
                match = re.search(r'\d+', items_text)
                if match:
                    count = int(match.group())
                    logger.info(f"Найдено {count} элементов для модерации")
                    return count
            
            # Если не нашли через основной локатор, считаем строки в таблице
            if self.moderation_table_locator.count() > 0:
                rows = self.page.locator("table.moderation-table tr").count()
                # Вычитаем 1 для заголовка таблицы
                count = max(0, rows - 1)
                logger.info(f"Найдено {count} строк в таблице модерации")
                return count
            
            # Если не нашли количество ни одним способом
            logger.warning("Не удалось определить количество элементов для модерации")
            return 0
            
        except Exception as e:
            logger.error(f"Ошибка при получении количества элементов для модерации: {e}")
            return 0
    
    def get_base_url(self) -> str:
        """
        Получает базовый URL из конфигурации или текущего URL страницы.
        
        Returns:
            str: Базовый URL.
        """
        # Сначала пробуем получить URL из конфигурации
        try:
            from projects.auth_management.config import config
            if hasattr(config, 'BASE_URL') and config.BASE_URL:
                return config.BASE_URL
        except ImportError:
            pass
            
        # Если не удалось получить из конфигурации, извлекаем из текущего URL
        from urllib.parse import urlparse
        parsed_url = urlparse(self.page.url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url
    
    def take_screenshot(self, path: str = "moderator_dashboard_debug.png") -> bool:
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
