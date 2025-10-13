"""
Page Object для бургер-меню сайта bll.by

Содержит методы для взаимодействия с бургер-меню, включая открытие,
закрытие, навигацию по ссылкам и проверку структуры меню.
"""

import logging
import json
import re
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
        self.burger_button_selector = ".menu-gumb_new.menu-mobile"
        self.alternative_button_selector = ".menu-btn"  # Альтернативная видимая кнопка
        self.menu_container_selector = ".new-menu.new-menu_main"
        self.menu_link_selector = "a.menu_item_link"
        self.menu_item_selector = "a.menu_item_link, a.menu-bl-item__link"

        # Инициализируем локаторы
        self.burger_button = self.page.locator(self.burger_button_selector)
        self.alternative_button = self.page.locator(self.alternative_button_selector)
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
            locators_path = Path("config/locators/authenticated_ui_locators_bll_by.json")
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
            bool: True если меню успешно открыто или уже открыто
        """
        try:
            self.logger.info("Попытка открытия бургер-меню")

            # Сначала проверяем, не открыто ли меню уже
            if self.is_menu_open(timeout=2000):
                self.logger.info("Бургер-меню уже открыто")
                return True

            # Проверяем, есть ли видимые элементы меню без клика
            menu_items_count = self.menu_items.count()
            visible_items = sum(1 for item in self.menu_items.all() if item.is_visible())

            self.logger.info(f"Найдено элементов меню: {menu_items_count}, видимых: {visible_items}")

            if visible_items > 0:
                self.logger.info("Меню уже открыто - видимые элементы найдены")
                return True

            # Пробуем кликнуть по кнопке меню
            # Сначала пробуем основную кнопку
            burger_visible = self.burger_button.is_visible()
            self.logger.info(f"Основная кнопка бургер-меню видима: {burger_visible}")

            if burger_visible:
                self.burger_button.click(timeout=timeout)
                self.logger.info("Клик по основной кнопке бургер-меню выполнен")
            else:
                # Пробуем альтернативную кнопку
                alt_visible = self.alternative_button.is_visible()
                self.logger.info(f"Альтернативная кнопка (.menu-btn) видима: {alt_visible}")

                if alt_visible:
                    self.alternative_button.click(timeout=timeout)
                    self.logger.info("Клик по альтернативной кнопке бургер-меню выполнен")
                else:
                    self.logger.warning("Ни одна кнопка меню не видима")

                    # Последняя проверка - может меню открывается автоматически
                    # Умное ожидание вместо жесткого таймаута
                    try:
                        self.page.wait_for_selector(self.menu_item_selector, timeout=2000)
                        self.logger.info("Меню открылось автоматически после умного ожидания")
                        return True
                    except PlaywrightTimeoutError:
                        pass

                    return False

            # Ожидаем появления элементов меню
            try:
                self.menu_items.first.wait_for(state="visible", timeout=timeout)
                self.logger.info("Бургер-меню успешно открыто")
                return True
            except PlaywrightTimeoutError:
                # Даже если таймаут, проверяем еще раз - может элементы появились
                visible_after_click = sum(1 for item in self.menu_items.all() if item.is_visible())
                if visible_after_click > 0:
                    self.logger.info("Элементы меню появились после клика (несмотря на таймаут)")
                    return True

                self.logger.error(f"Элементы меню не появились после клика за {timeout}мс")
                return False

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
    def click_link_by_text(self, text: str, timeout: int = 5000) -> bool:
        """
        Простой и стабильный клик по ссылке в меню по тексту.

        Args:
            text: Текст ссылки для поиска
            timeout: Уменьшенное время ожидания для стабильности

        Returns:
            bool: True если клик выполнен успешно
        """
        try:
            self.logger.info(f"Простой клик по тексту: '{text}'")

            # Ищем ссылку по тексту и кликаем - просто и эффективно
            link = self.page.locator(f"a:has-text('{text}')").first

            # Ждем элемент и кликаем с force=True для стабильности
            link.wait_for(state="attached", timeout=timeout)
            link.click(force=True, timeout=timeout)

            self.logger.info(f"Успешно кликнули: '{text}'")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка клика по '{text}': {e}")
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

            # Ищем ссылку по href - сначала по частичному совпадению
            link = self.page.locator(f"a[href*='{href}']").first

            # Пробуем разные стратегии прокрутки и поиска элемента
            success = False

            # Стратегия 1: Прокрутка к элементу
            try:
                link.scroll_into_view_if_needed(timeout=timeout)
                self.page.wait_for_timeout(1000)
            except Exception:
                # Стратегия 2: Прокрутка всей страницы для отображения правых колонок
                try:
                    self.page.evaluate("""
                        // Прокручиваем вправо для отображения правых колонок
                        window.scrollTo({ left: 1000, behavior: 'smooth' });
                    """)
                    self.page.wait_for_timeout(1000)

                    # Пробуем прокрутить конкретный элемент в видимую область
                    self.page.evaluate("""
                        const element = document.querySelector('a[href*='{href}']');
                        if (element) {{
                            element.scrollIntoView({{ behavior: 'smooth', block: 'center', inline: 'center' }});
                        }}
                    """.format(href=href.replace("'", "\\'")))
                    self.page.wait_for_timeout(100)
                except Exception as e:
                    self.logger.warning(f"Прокрутка не удалась: {e}")

            # Ждем, что элемент будет в DOM и попробуем кликнуть даже если не видим
            try:
                link.wait_for(state="attached", timeout=timeout)

                # Проверяем, видим ли элемент
                if link.is_visible():
                    link.click(timeout=timeout)
                else:
                    # Если не видим, пробуем кликнуть с force=True
                    self.logger.warning(f"Элемент не видим, пробуем force click для '{href}'")
                    link.click(force=True, timeout=timeout)

                success = True
            except PlaywrightTimeoutError:
                # Если обычный клик не сработал, пробуем найти элемент по тексту
                self.logger.warning(f"Пытаемся найти элемент по тексту для '{href}'")
                text_elements = self.page.locator(f"a:has-text('{href.split('/')[-1]}')").all()

                for element in text_elements:
                    try:
                        if element.is_visible():
                            element.click(timeout=timeout)
                            success = True
                            break
                        else:
                            element.click(force=True, timeout=timeout)
                            success = True
                            break
                    except Exception:
                        continue

            if success:
                self.logger.info(f"Успешно кликнули по ссылке: '{href}'")
                return True
            else:
                self.logger.error(f"Не удалось кликнуть по ссылке '{href}'")
                return False

        except Exception as e:
            self.logger.error(f"Ошибка при клике по ссылке '{href}': {e}")
            return False

    @allure.step("Клик по ссылке меню по тексту и классу: {text}")
    def click_link_by_text_and_class(self, text: str, css_class: str = "menu_item_link", timeout: int = 10000) -> bool:
        """
        Кликает по ссылке в меню по тексту и CSS классу (более точный селектор)

        Args:
            text: Текст ссылки для поиска
            css_class: CSS класс элемента
            timeout: Время ожидания в миллисекундах

        Returns:
            bool: True если клик выполнен успешно
        """
        try:
            self.logger.info(f"Поиск и клик по ссылке с текстом: '{text}' и классом: '{css_class}'")

            if not self.is_menu_open():
                if not self.open_menu():
                    self.logger.error("Не удалось открыть меню для клика по ссылке")
                    return False

            # Используем более точный селектор с текстом и классом
            link = self.page.locator(f"a.{css_class}:has-text('{text}')").first

            # Прокручиваем к элементу
            try:
                link.scroll_into_view_if_needed(timeout=timeout)
                self.page.wait_for_timeout(1000)
            except Exception:
                # Альтернативная прокрутка
                self.page.evaluate(f"""
                    const element = document.querySelector('a.{css_class}:has-text('{text.replace("'", "\\'")}')');
                    if (element) {{
                        element.scrollIntoView({{ behavior: 'smooth', block: 'center', inline: 'center' }});
                    }}
                """)
                self.page.wait_for_timeout(1000)

            # Ждем прикрепления элемента и пробуем кликнуть
            link.wait_for(state="attached", timeout=timeout)

            if link.is_visible():
                link.click(timeout=timeout)
            else:
                self.logger.warning(f"Элемент не видим, пробуем force click для '{text}'")
                link.click(force=True, timeout=timeout)

            self.logger.info(f"Успешно кликнули по ссылке: '{text}'")
            return True

        except Exception as e:
            self.logger.error(f"Ошибка при клике по ссылке '{text}': {e}")
            return False

    @allure.step("Клик по ссылке меню по ARIA роли и имени: {name}")
    def click_link_by_role(self, name: str, timeout: int = 10000) -> bool:
        """
        Кликает по ссылке в меню по ARIA роли (link) и имени (более надежный селектор)

        Args:
            name: Имя/текст ссылки
            timeout: Время ожидания в миллисекундах

        Returns:
            bool: True если клик выполнен успешно
        """
        try:
            self.logger.info(f"Поиск и клик по ссылке с ARIA ролью link и именем: '{name}'")

            if not self.is_menu_open():
                if not self.open_menu():
                    self.logger.error("Не удалось открыть меню для клика по ссылке")
                    return False

            # Используем ARIA роль - самый надежный способ
            link = self.page.get_by_role("link", name=name)

            # Пробуем разные стратегии поиска и клика
            success = False

            # Стратегия 1: Обычный поиск по ARIA роли с force кликом для скрытых элементов
            try:
                link.wait_for(state="attached", timeout=timeout//3)
                # Всегда используем force=True для правой колонки (элементы могут быть скрыты)
                link.click(force=True, timeout=timeout//3)
                success = True
                self.logger.info(f"Успешно кликнули по ссылке '{name}' с force=True")
            except Exception as e1:
                self.logger.warning(f"ARIA роль с force кликом не сработала для '{name}': {e1}")

            if not success:
                # Стратегия 2: Поиск по тексту с force click
                try:
                    text_link = self.page.locator(f"a:has-text('{name}')").first
                    text_link.wait_for(state="attached", timeout=timeout//3)
                    # Всегда используем force=True для правой колонки
                    text_link.click(force=True, timeout=timeout//3)
                    success = True
                    self.logger.info(f"Успешно кликнули по ссылке '{name}' по тексту с force=True")
                except Exception as e2:
                    self.logger.warning(f"Поиск по тексту с force кликом не сработал для '{name}': {e2}")

            if not success:
                # Стратегия 3: Поиск по CSS селектору с force кликом
                try:
                    # Пробуем найти элемент по CSS селектору
                    css_selectors = [
                        f"a.menu_item_link:has-text('{name}')",
                        f".menu_item_link:has-text('{name}')",
                        f"a:has-text('{name}')",
                    ]

                    for selector in css_selectors:
                        try:
                            css_link = self.page.locator(selector).first
                            css_link.wait_for(state="attached", timeout=timeout//3)

                            # Всегда используем force=True для правой колонки
                            css_link.click(force=True, timeout=timeout//3)
                            success = True
                            self.logger.info(f"Успешно кликнули по ссылке '{name}' по CSS селектору с force=True")
                            break
                        except Exception as e3:
                            self.logger.warning(f"CSS селектор '{selector}' не сработал для '{name}': {e3}")
                            continue
                except Exception as e:
                    self.logger.warning(f"CSS селекторы не сработали для '{name}': {e}")

            if not success:
                # Стратегия 4: JavaScript клик для скрытых элементов правой колонки
                try:
                    self.logger.warning(f"Пробуем JavaScript клик для скрытых элементов правой колонки '{name}'")

                    # Прокручиваем вправо для отображения правых колонок
                    self.page.evaluate("window.scrollTo({ left: 1000, behavior: 'smooth' });")
                    self.page.wait_for_timeout(1000)

                    # Ищем элемент по тексту
                    js_selector = f"a:has-text('{name}')"
                    js_link = self.page.locator(js_selector).first

                    if js_link.count() > 0:
                        # Получаем href элемента
                        href = js_link.get_attribute('href') or ""
                        self.logger.info(f"Найден элемент с href: {href}")

                        # Используем JavaScript для клика по скрытому элементу
                        js_click_result = self.page.evaluate(f"""
                            // Ищем элемент по тексту
                            const elements = document.querySelectorAll('a');
                            let clicked = false;
                            for (let elem of elements) {{
                                const text = elem.textContent || '';
                                const href = elem.href || '';
                                if ((text.includes('{name}') || href.includes('{href.split('/')[-1] if href else ''}'))) {{
                                    // Используем JavaScript клик
                                    try {{
                                        elem.click();
                                        clicked = true;
                                        console.log('JS click successful for element:', text);
                                        break;
                                    }} catch (clickError) {{
                                        console.log('JS click failed, trying dispatchEvent:', clickError);
                                        try {{
                                            const event = new MouseEvent('click', {{
                                                bubbles: true,
                                                cancelable: true,
                                                view: window
                                            }});
                                            elem.dispatchEvent(event);
                                            clicked = true;
                                            console.log('dispatchEvent successful for element:', text);
                                            break;
                                        }} catch (eventError) {{
                                            console.log('dispatchEvent failed:', eventError);
                                        }}
                                    }}
                                    break;
                                }}
                            }}
                            // Возвращаем результат клика
                            clicked;
                        """)

                        self.logger.info(f"JavaScript клик вернул результат: {js_click_result}")

                        if js_click_result:
                            success = True
                            self.logger.info(f"Успешно кликнули по скрытому элементу '{name}' через JavaScript")
                        else:
                            self.logger.warning(f"JavaScript клик не удался для '{name}'")

                        if js_click_result:
                            success = True
                            self.logger.info(f"Успешно кликнули по скрытому элементу '{name}' через JavaScript")
                        else:
                            self.logger.warning(f"JavaScript клик не удался для '{name}'")
                    else:
                        self.logger.warning(f"Элемент '{name}' не найден для JavaScript клика")

                except Exception as js_error:
                    self.logger.error(f"JavaScript клик не сработал для '{name}': {js_error}")

            if success:
                # Ждем перехода на новую страницу после клика
                try:
                    self.page.wait_for_load_state("domcontentloaded", timeout=5000)
                    self.logger.info(f"Страница загрузилась после клика по '{name}'")
                except Exception as e:
                    self.logger.warning(f"Не удалось дождаться загрузки страницы после клика: {e}")

                # Дополнительное ожидание для завершения всех сетевых запросов
                try:
                    self.page.wait_for_load_state("networkidle", timeout=3000)
                except Exception:
                    pass  # networkidle может не наступить, это нормально

                self.logger.info(f"Успешно кликнули по ссылке: '{name}'")
                return True
            else:
                self.logger.error(f"Не удалось кликнуть по ссылке '{name}' всеми стратегиями")
                return False

        except Exception as e:
            self.logger.error(f"Ошибка при клике по ссылке '{name}': {e}")
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
            locator = self.page.locator(f"a:has-text('{text}')").first
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
            locator = self.page.locator(f"a[href*='{href}']").first
            locator.wait_for(state="visible", timeout=timeout)
            return locator
        except PlaywrightTimeoutError:
            # Пробуем найти по частичному совпадению
            try:
                locator = self.page.locator(f"a[href*='{href.split('/')[-1]}']").first
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

    @allure.step("Извлечение ID из URL типа docs")
    def extract_docs_id_from_url(self, url: str) -> Optional[str]:
        """
        Извлекает ID из URL типа https://bll.by/docs/perechen-tem-chek-list-dokumentov-487105

        Args:
            url: URL для анализа

        Returns:
            Optional[str]: ID документа или None если не найден
        """
        # Регулярное выражение для поиска ID в конце URL (после последнего дефиса)
        match = re.search(r'-(\d+)$', url)
        if match:
            return match.group(1)
        return None

    @allure.step("Сравнение URL с учетом ID для docs")
    def compare_docs_url_with_id(self, actual_url: str, expected_id: str) -> bool:
        """
        Сравнивает URL типа docs по ID, игнорируя текстовую часть

        Args:
            actual_url: Фактический URL
            expected_id: Ожидаемый ID документа

        Returns:
            bool: True если ID совпадает
        """
        actual_id = self.extract_docs_id_from_url(actual_url)
        return actual_id == expected_id

    @allure.step("Умная проверка URL")
    def validate_navigation_url(self, actual_url: str, expected_url: str) -> bool:
        """
        Умная проверка URL с учетом специфики разных типов страниц

        Для URL типа docs (https://bll.by/docs/...-ID) сравнивает только ID
        Для остальных URL сравнивает полностью

        Args:
            actual_url: Фактический URL после перехода
            expected_url: Ожидаемый URL или паттерн

        Returns:
            bool: True если URL корректный
        """
        # Если expected_url содержит паттерн с ID
        docs_patterns = ['-20', '-14', '-22', '-40', '-48']
        if any(pattern in expected_url for pattern in docs_patterns):
            # Это docs URL - сравниваем по ID
            expected_id = self.extract_docs_id_from_url(expected_url)
            if expected_id:
                return self.compare_docs_url_with_id(actual_url, expected_id)

        # Для остальных URL - точное сравнение или regex паттерн
        if expected_url.startswith('https://') or expected_url.startswith('http://'):
            # Точное сравнение для полных URL
            return actual_url == expected_url
        else:
            # Regex паттерн
            return bool(re.search(expected_url, actual_url))

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
    @allure.step("Умное ожидание готовности страницы")
    def smart_wait_for_page_ready(self, timeout: int = 5000) -> bool:
        """
        Умное ожидание готовности страницы вместо жесткого wait_for_timeout(500).

        Ждет загрузки DOM и network idle состояния.

        Args:
            timeout: Максимальное время ожидания в миллисекундах

        Returns:
            bool: True если страница готова
        """
        try:
            self.logger.info("Умное ожидание готовности страницы")

            # Ждем загрузки DOM
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout//2)

            # Ждем завершения сетевых запросов (но не дольше половины таймаута)
            try:
                self.page.wait_for_load_state("networkidle", timeout=timeout//2)
            except PlaywrightTimeoutError:
                # Networkidle может не наступить, это нормально
                self.logger.info("Network idle не наступил, но DOM загружен")

            self.logger.info("Страница готова к взаимодействию")
            return True

        except PlaywrightTimeoutError:
            self.logger.error(f"Страница не загрузилась за {timeout}мс")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка при ожидании готовности страницы: {e}")
            return False
            return result