"""
Page Object для главной страницы сайта bll.by

Содержит методы для взаимодействия с главной страницей,
включая открытие бургер-меню и проверку основных элементов.
"""
import logging
from typing import Optional
import allure
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from framework.app.pages.base_page import BasePage
from .burger_menu_page import BurgerMenuPage
from framework.utils.url_utils import add_allow_session_param


class MainPage(BasePage):
    """
    Page Object для работы с главной страницей сайта bll.by
    """
    
    def __init__(self, page: Page):
        """
        Инициализация MainPage
        
        Args:
            page: Экземпляр страницы Playwright
        """
        super().__init__(page)
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Основные селекторы для главной страницы
        self.burger_button_selector = "a.menu-btn.menu-btn_new"
        self.main_content_selector = "main, .main-content, [data-testid='main-content']"
        self.header_selector = "header, .header, .page-header"
        self.footer_selector = "footer, .footer"
        
        # Инициализируем локаторы
        self.burger_button = self.page.locator(self.burger_button_selector)
        self.main_content = self.page.locator(self.main_content_selector)
        self.header = self.page.locator(self.header_selector)
        self.footer = self.page.locator(self.footer_selector)
        
        # Создаем экземпляр BurgerMenuPage
        self.burger_menu = BurgerMenuPage(page)

    @allure.step("Переход на главную страницу")
    def navigate_to_main(self, timeout: int = 15000) -> bool:
        """
        Переходит на главную страницу сайта
        
        Args:
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если переход выполнен успешно
        """
        try:
            self.logger.info("Переход на главную страницу")
            
            # Используем метод из BasePage для добавления параметра allow-session
            main_url = "https://bll.by/"
            url_with_param = add_allow_session_param(main_url, headless=True)
            
            self.page.goto(url_with_param, wait_until="domcontentloaded", timeout=timeout)
            
            # Ждем загрузки основного контента
            self.main_content.wait_for(state="visible", timeout=timeout)
            
            self.logger.info("Успешно перешли на главную страницу")
            return True
            
        except PlaywrightTimeoutError:
            self.logger.error(f"Таймаут при переходе на главную страницу за {timeout}мс")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при переходе на главную страницу: {e}")
            return False

    @allure.step("Клик по кнопке бургер-меню")
    def click_burger_menu_button(self, timeout: int = 10000) -> bool:
        """
        Кликает по кнопке бургер-меню на главной странице
        
        Args:
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если клик выполнен успешно
        """
        try:
            self.logger.info("Попытка клика по кнопке бургер-меню")
            
            # Ждем видимости кнопки меню
            self.burger_button.wait_for(state="visible", timeout=timeout)
            
            # Кликаем по кнопке
            self.burger_button.click(timeout=timeout)
            
            self.logger.info("Успешно кликнули по кнопке бургер-меню")
            return True
            
        except PlaywrightTimeoutError:
            self.logger.error(f"Таймаут при клике по кнопке бургер-меню за {timeout}мс")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при клике по кнопке бургер-меню: {e}")
            return False

    @allure.step("Проверка видимости бургер-меню")
    def is_burger_menu_visible(self, timeout: int = 5000) -> bool:
        """
        Проверяет видимость кнопки бургер-меню
        
        Args:
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если кнопка меню видима
        """
        try:
            return self.burger_button.is_visible(timeout=timeout)
        except PlaywrightTimeoutError:
            return False

    @allure.step("Проверка заголовка страницы")
    def verify_page_title(self, expected_title_part: str, timeout: int = 5000) -> bool:
        """
        Проверяет заголовок страницы на наличие ожидаемой части текста
        
        Args:
            expected_title_part: Ожидаемая часть заголовка
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если заголовок содержит ожидаемую часть
        """
        try:
            # Ждем немного для стабильности
            self.page.wait_for_timeout(1000)
            
            actual_title = self.page.title()
            is_present = expected_title_part.lower() in actual_title.lower()
            
            if is_present:
                self.logger.info(f"Заголовок содержит '{expected_title_part}': {actual_title}")
            else:
                self.logger.warning(f"Заголовок не содержит '{expected_title_part}': {actual_title}")
            
            return is_present
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке заголовка страницы: {e}")
            return False

    @allure.step("Проверка основных элементов страницы")
    def verify_main_elements_present(self, timeout: int = 10000) -> dict:
        """
        Проверяет наличие основных элементов на главной странице
        
        Args:
            timeout: Время ожидания в миллисекундах
            
        Returns:
            dict: Результат проверки с информацией о найденных элементах
        """
        result = {
            'header_present': False,
            'footer_present': False,
            'burger_menu_present': False,
            'main_content_present': False,
            'all_elements_present': False
        }
        
        try:
            # Проверяем наличие заголовка
            result['header_present'] = self.header.is_visible(timeout=timeout)
            
            # Проверяем наличие подвала
            result['footer_present'] = self.footer.is_visible(timeout=timeout)
            
            # Проверяем наличие кнопки бургер-меню
            result['burger_menu_present'] = self.burger_button.is_visible(timeout=timeout)
            
            # Проверяем наличие основного контента
            result['main_content_present'] = self.main_content.is_visible(timeout=timeout)
            
            # Проверяем, все ли элементы присутствуют
            result['all_elements_present'] = all([
                result['header_present'],
                result['footer_present'], 
                result['burger_menu_present'],
                result['main_content_present']
            ])
            
            self.logger.info(f"Проверка основных элементов: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке основных элементов: {e}")
            return result

    @allure.step("Открытие бургер-меню с главной страницы")
    def open_burger_menu(self, timeout: int = 10000) -> bool:
        """
        Открывает бургер-меню с главной страницы
        
        Args:
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если меню успешно открыто
        """
        try:
            self.logger.info("Попытка открытия бургер-меню с главной страницы")
            
            # Кликаем по кнопке меню
            if not self.click_burger_menu_button(timeout):
                return False
            
            # Ждем открытия меню
            if self.burger_menu.wait_for_menu_loaded(timeout):
                self.logger.info("Бургер-меню успешно открыто с главной страницы")
                return True
            else:
                self.logger.error("Меню не загрузилось после клика")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при открытии бургер-меню: {e}")
            return False

    @allure.step("Проверка доступности ссылок в меню")
    def check_menu_links_accessibility(self, timeout: int = 10000) -> dict:
        """
        Проверяет доступность ссылок в бургер-меню
        
        Args:
            timeout: Время ожидания в миллисекундах
            
        Returns:
            dict: Результат проверки доступности ссылок
        """
        result = {
            'total_links': 0,
            'accessible_links': 0,
            'inaccessible_links': 0,
            'accessibility_rate': 0.0
        }
        
        try:
            # Открываем меню
            if not self.open_burger_menu(timeout):
                self.logger.error("Не удалось открыть меню для проверки ссылок")
                return result
            
            # Получаем все элементы меню
            menu_items = self.burger_menu.get_all_menu_items()
            result['total_links'] = len(menu_items)
            
            accessible_count = 0
            inaccessible_count = 0
            
            for text, href in menu_items:
                try:
                    # Проверяем видимость ссылки
                    link_locator = self.page.locator(f"a.menu_item_link:has-text('{text}')").first
                    is_visible = link_locator.is_visible(timeout=1000)  # короткий таймаут для проверки
                    
                    if is_visible:
                        accessible_count += 1
                    else:
                        inaccessible_count += 1
                        
                except Exception:
                    # Если возникла ошибка при проверке, считаем ссылку недоступной
                    inaccessible_count += 1
            
            result['accessible_links'] = accessible_count
            result['inaccessible_links'] = inaccessible_count
            
            if result['total_links'] > 0:
                result['accessibility_rate'] = (accessible_count / result['total_links']) * 10
            
            self.logger.info(f"Проверка доступности ссылок: {accessible_count}/{result['total_links']} доступны")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке доступности ссылок: {e}")
            return result