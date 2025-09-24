"""
Page Object для бургер-меню сайта bll.by

Содержит методы для взаимодействия с бургер-меню, включая открытие,
закрытие, навигацию по ссылкам и проверку структуры меню.
"""
import logging
import json
from pathlib import Path
from typing import List, Tuple, Optional
import allure
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError


class BurgerMenuPage:
    """
    Page Object для работы с бургер-меню сайта bll.by
    """
    
    def __init__(self, page: Page):
        """
        Инициализация BurgerMenuPage
        
        Args:
            page: Экземпляр страницы Playwright
        """
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Загружаем локаторы из JSON файла
        self.locators = self._load_locators()
        
        # Основные селекторы для бургер-меню
        self.burger_button_selector = "a.menu-btn.menu-btn_new"
        self.menu_container_selector = ".new-menu.new-menu_main"
        self.menu_link_selector = "a.menu_item_link"
        self.menu_item_selector = "a.menu_item_link, a.menu-bl-item__link"
        
        # Инициализируем локаторы
        self.burger_button = self.page.locator(self.burger_button_selector)
        self.menu_container = self.page.locator(self.menu_container_selector)
        self.menu_links = self.page.locator(self.menu_link_selector)
        self.menu_items = self.page.locator(self.menu_item_selector)

    def _load_locators(self) -> dict:
        """
        Загружает локаторы из JSON файла с аутентифицированными локаторами
        
        Returns:
            dict: Словарь с локаторами для элементов меню
        """
        try:
            locators_path = Path("authenticated_ui_locators_bll_by.json")
            if locators_path.exists():
                with open(locators_path, 'r', encoding='utf-8') as f:
                    locators_data = json.load(f)
                
                # Фильтруем только локаторы, относящиеся к бургер-меню
                burger_locators = {}
                for item in locators_data:
                    if any(keyword in item.get('description', '').lower() 
                          for keyword in ['burger', 'menu', 'ссылка', 'link']):
                        key = item.get('description', '').replace(' ', '_').lower()
                        burger_locators[key] = item.get('selector', '')
                
                return burger_locators
            else:
                self.logger.warning(f"Файл локаторов не найден: {locators_path}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке локаторов: {e}")
            return {}

    @allure.step("Открытие бургер-меню")
    def open_menu(self, timeout: int = 1000) -> bool:
        """
        Открывает бургер-меню кликом по кнопке
        
        Args:
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если меню успешно открыто
        """
        try:
            self.logger.info("Попытка открытия бургер-меню")
            
            # Проверяем видимость кнопки меню
            self.burger_button.wait_for(state="visible", timeout=timeout)
            
            # Кликаем по кнопке меню
            self.burger_button.click(timeout=timeout)
            
            # Ожидаем появления элементов меню
            self.menu_items.first.wait_for(state="visible", timeout=timeout)
            
            self.logger.info("Бургер-меню успешно открыто")
            return True
            
        except PlaywrightTimeoutError:
            self.logger.error(f"Таймаут при открытии бургер-меню за {timeout}мс")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при открытии бургер-меню: {e}")
            return False

    @allure.step("Закрытие бургер-меню")
    def close_menu(self, timeout: int = 10000) -> bool:
        """
        Закрывает бургер-меню кликом по кнопке
        
        Args:
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если меню успешно закрыто
        """
        try:
            self.logger.info("Попытка закрытия бургер-меню")
            
            # Проверяем видимость кнопки меню (она должна быть активной когда меню открыто)
            self.burger_button.wait_for(state="visible", timeout=timeout)
            
            # Кликаем по кнопке меню для закрытия
            self.burger_button.click(timeout=timeout)
            
            # Ожидаем исчезновения элементов меню
            try:
                self.menu_items.first.wait_for(state="hidden", timeout=timeout)
            except PlaywrightTimeoutError:
                # Если элементы уже скрыты, это нормально
                pass
            
            self.logger.info("Бургер-меню успешно закрыто")
            return True
            
        except PlaywrightTimeoutError:
            self.logger.error(f"Таймаут при закрытии бургер-меню за {timeout}мс")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии бургер-меню: {e}")
            return False

    @allure.step("Проверка открытия меню")
    def is_menu_open(self, timeout: int = 5000) -> bool:
        """
        Проверяет, открыто ли бургер-меню
        
        Args:
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если меню открыто
        """
        try:
            # Проверяем наличие видимых элементов меню
            return self.menu_items.first.is_visible(timeout=timeout)
        except PlaywrightTimeoutError:
            return False

    @allure.step("Получение всех элементов меню")
    def get_all_menu_items(self) -> List[Tuple[str, str]]:
        """
        Получает все элементы меню с их текстом и href
        
        Returns:
            List[Tuple[str, str]]: Список кортежей (текст, href) для всех элементов меню
        """
        items = []
        
        # Получаем количество элементов
        count = self.menu_links.count()
        
        for i in range(count):
            try:
                link = self.menu_links.nth(i)
                
                # Получаем текст и href
                text = link.text_content().strip() if link.text_content() else ""
                href = link.get_attribute("href") or ""
                
                if text and href:  # Добавляем только если оба значения есть
                    items.append((text, href))
                    
            except Exception as e:
                self.logger.warning(f"Ошибка при получении элемента меню {i}: {e}")
                continue
        
        self.logger.info(f"Найдено {len(items)} элементов меню")
        return items

    @allure.step("Клик по ссылке меню по тексту: {text}")
    def click_link_by_text(self, text: str, timeout: int = 10000) -> bool:
        """
        Кликает по ссылке в меню по тексту
        
        Args:
            text: Текст ссылки для поиска
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если клик выполнен успешно
        """
        try:
            self.logger.info(f"Поиск и клик по ссылке с текстом: '{text}'")
            
            # Сначала проверяем, что меню открыто
            if not self.is_menu_open():
                if not self.open_menu():
                    self.logger.error("Не удалось открыть меню для клика по ссылке")
                    return False
            
            # Ищем ссылку по тексту
            link = self.page.locator(f"a.menu_item_link:has-text('{text}')").first
            
            # Ждем видимости элемента
            link.wait_for(state="visible", timeout=timeout)
            
            # Кликаем по ссылке
            link.click(timeout=timeout)
            
            self.logger.info(f"Успешно кликнули по ссылке: '{text}'")
            return True
            
        except PlaywrightTimeoutError:
            self.logger.error(f"Таймаут при поиске или клике по ссылке '{text}' за {timeout}мс")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при клике по ссылке '{text}': {e}")
            return False

    @allure.step("Клик по ссылке меню по href: {href}")
    def click_link_by_href(self, href: str, timeout: int = 10000) -> bool:
        """
        Кликает по ссылке в меню по href
        
        Args:
            href: URL ссылки для поиска
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если клик выполнен успешно
        """
        try:
            self.logger.info(f"Поиск и клик по ссылке с href: '{href}'")
            
            # Сначала проверяем, что меню открыто
            if not self.is_menu_open():
                if not self.open_menu():
                    self.logger.error("Не удалось открыть меню для клика по ссылке")
                    return False
            
            # Ищем ссылку по href
            link = self.page.locator(f"a.menu_item_link[href='{href}']").first
            
            # Если не нашли точное совпадение, ищем по частичному совпадению
            if link.count() == 0:
                link = self.page.locator(f"a.menu_item_link[href*='{href.split('/')[-1]}']").first
            
            # Ждем видимости элемента
            link.wait_for(state="visible", timeout=timeout)
            
            # Кликаем по ссылке
            link.click(timeout=timeout)
            
            self.logger.info(f"Успешно кликнули по ссылке: '{href}'")
            return True
            
        except PlaywrightTimeoutError:
            self.logger.error(f"Таймаут при поиске или клике по ссылке '{href}' за {timeout}мс")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при клике по ссылке '{href}': {e}")
            return False

    @allure.step("Получение элемента меню по тексту: {text}")
    def get_menu_item_by_text(self, text: str, timeout: int = 5000) -> Optional[Locator]:
        """
        Получает локатор элемента меню по тексту
        
        Args:
            text: Текст элемента для поиска
            timeout: Время ожидания в миллисекундах
            
        Returns:
            Optional[Locator]: Локатор элемента или None если не найден
        """
        try:
            locator = self.page.locator(f"a.menu_item_link:has-text('{text}')").first
            locator.wait_for(state="visible", timeout=timeout)
            return locator
        except PlaywrightTimeoutError:
            self.logger.warning(f"Элемент меню с текстом '{text}' не найден")
            return None

    @allure.step("Получение элемента меню по href: {href}")
    def get_menu_item_by_href(self, href: str, timeout: int = 5000) -> Optional[Locator]:
        """
        Получает локатор элемента меню по href
        
        Args:
            href: URL элемента для поиска
            timeout: Время ожидания в миллисекундах
            
        Returns:
            Optional[Locator]: Локатор элемента или None если не найден
        """
        try:
            locator = self.page.locator(f"a.menu_item_link[href='{href}']").first
            locator.wait_for(state="visible", timeout=timeout)
            return locator
        except PlaywrightTimeoutError:
            # Пробуем найти по частичному совпадению
            try:
                locator = self.page.locator(f"a.menu_item_link[href*='{href.split('/')[-1]}']").first
                locator.wait_for(state="visible", timeout=timeout)
                return locator
            except PlaywrightTimeoutError:
                self.logger.warning(f"Элемент меню с href '{href}' не найден")
                return None

    @allure.step("Ожидание загрузки меню")
    def wait_for_menu_loaded(self, timeout: int = 10000) -> bool:
        """
        Ожидает полной загрузки бургер-меню
        
        Args:
            timeout: Время ожидания в миллисекундах
            
        Returns:
            bool: True если меню загружено
        """
        try:
            # Ждем появления контейнера меню
            self.menu_container.wait_for(state="visible", timeout=timeout)
            
            # Ждем появления хотя бы одного элемента меню
            self.menu_items.first.wait_for(state="visible", timeout=timeout)
            
            self.logger.info("Бургер-меню полностью загружено")
            return True
            
        except PlaywrightTimeoutError:
            self.logger.error(f"Меню не загрузилось за {timeout}мс")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при ожидании загрузки меню: {e}")
            return False

    @allure.step("Проверка структуры меню")
    def validate_menu_structure(self, expected_categories: List[str]) -> dict:
        """
        Проверяет структуру меню на наличие ожидаемых категорий
        
        Args:
            expected_categories: Список ожидаемых категорий меню
            
        Returns:
            dict: Результат проверки с информацией о найденных и отсутствующих категориях
        """
        result = {
            'found_categories': [],
            'missing_categories': [],
            'total_found': 0,
            'total_expected': len(expected_categories)
        }
        
        try:
            # Получаем все элементы меню
            all_items = self.get_all_menu_items()
            menu_texts = [item[0] for item in all_items]
            
            for category in expected_categories:
                if any(category.lower() in text.lower() for text in menu_texts):
                    result['found_categories'].append(category)
                else:
                    result['missing_categories'].append(category)
            
            result['total_found'] = len(result['found_categories'])
            self.logger.info(f"Проверка структуры меню: найдено {result['total_found']}/{result['total_expected']} категорий")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке структуры меню: {e}")
            return result