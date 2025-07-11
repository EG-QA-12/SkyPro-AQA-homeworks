"""
Операции авторизации для GUI интерфейса.

Содержит логику для:
- Авторизации пользователей через браузер
- Тестирования авторизации с куками
- Проверки доступа без авторизации
- Массовой авторизации
"""

import threading
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from playwright.sync_api import sync_playwright

from src.config import config
from src.auth import load_cookies, perform_login_on_page
from framework.utils.url_utils import add_allow_session_param, is_headless


class AuthOperations:
    """Класс для выполнения операций авторизации."""
    
    def __init__(self, user_manager: Any, gui_helper: Any, progress_bar: Any):
        """
        Инициализация операций авторизации.
        
        Args:
            user_manager: Менеджер пользователей
            gui_helper: Помощник GUI для вывода сообщений
            progress_bar: Прогресс-бар для отображения процесса
        """
        self.user_manager = user_manager
        self.gui_helper = gui_helper
        self.progress_bar = progress_bar
    
    def authorize_user(self, user: Dict[str, Any], headless: bool = True, 
                      password_func: Callable[[str], Optional[str]] = None) -> None:
        """
        Авторизация конкретного пользователя через браузер.
        
        Args:
            user: Данные пользователя
            headless: Запуск браузера в headless режиме
            password_func: Функция для получения пароля пользователя
        """
        def auth_thread():
            try:
                self.gui_helper.set_status("Выполняется авторизация...", "orange")
                self.progress_bar.start()
                
                user_login = user.get('login') or user.get('username', 'неизвестный')
                self.gui_helper.add_result(f"Начинается авторизация пользователя {user_login}")
                
                # Формируем путь для сохранения куков
                cookies_path = config.COOKIES_PATH.parent / f"{user.get('login')}_cookies.json"
                
                # Проверяем корректность логина
                if not user_login or user_login == 'None' or user_login.strip() == '':
                    raise ValueError(f"Логин пользователя не указан или некорректен: '{user_login}'")
                
                # Получаем пароль
                password_to_use = password_func(user_login) if password_func else None
                if not password_to_use:
                    raise ValueError(f"Пароль для пользователя {user_login} не найден")
                
                # Выполняем авторизацию (КОПИЯ ИЗ РАБОЧЕГО КОДА)
                self.gui_helper.add_result(f"🌐 Запуск браузера (headless: {headless})")
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=headless)
                    context = browser.new_context()
                    page = context.new_page()
                    
                    self.gui_helper.add_result(f"📝 Авторизация: логин='{user_login}', пароль={'*' * len(password_to_use)}")
                    self.gui_helper.add_result(f"💾 Куки будут сохранены в: {cookies_path}")
                    
                    # Используем точно такой же вызов, как в рабочем коде
                    perform_login_on_page(
                        page=page,
                        login=user_login,
                        password=password_to_use,
                        cookies_path=cookies_path
                    )
                    
                    # Получаем куки ДО закрытия браузера (КРИТИЧНО!)
                    cookies = context.cookies()
                    browser.close()
                
                # Сохраняем куки
                if cookies:
                    success = self.user_manager.save_cookies_to_file(user_login, cookies)
                    if success:
                        self.gui_helper.add_result(f"🍪 Куки сохранены: {cookies_path}", "SUCCESS")
                        self.user_manager.update_cookie_expiry(user['id'])
                        self.gui_helper.add_result("⏰ Время истечения куков обновлено", "SUCCESS")
                    else:
                        self.gui_helper.add_result("⚠️ Ошибка сохранения куков в БД", "WARNING")
                else:
                    self.gui_helper.add_result("⚠️ Не удалось получить куки из браузера", "WARNING")
                
                self.gui_helper.add_result(f"✅ Авторизация пользователя {user_login} завершена!", "SUCCESS")
                self.gui_helper.set_status(f"✅ {user_login} авторизован успешно", "green")
                
            except Exception as e:
                error_msg = f"Ошибка авторизации: {e}"
                self.gui_helper.add_result(error_msg, "ERROR")
                self.gui_helper.set_status("Ошибка авторизации", "red")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=auth_thread, daemon=True).start()
    
    def test_authorization_with_cookies(self, user: Dict[str, Any], headless: bool = True) -> None:
        """
        Тестирование авторизации с использованием сохраненных куков.
        
        Args:
            user: Данные пользователя
            headless: Запуск браузера в headless режиме
        """
        def test_thread():
            try:
                self.gui_helper.set_status("Выполняется тестовая авторизация...", "orange")
                self.progress_bar.start()
                
                user_login = user.get('login') or user.get('username', 'unknown')
                self.gui_helper.add_result(f"🧪 Тест авторизации для: {user_login}")
                self.gui_helper.add_result(f"📧 Email: {user.get('email', 'N/A')}")
                self.gui_helper.add_result(f"👤 Роль: {user.get('role', 'N/A')}")
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=headless)
                    context = browser.new_context()
                    
                    # Загружаем куки
                    cookies_path = config.COOKIES_PATH.parent / f"{user_login}_cookies.json"
                    cookies = load_cookies(cookies_path)
                    
                    if cookies:
                        context.add_cookies(cookies)
                        self.gui_helper.add_result(f"🍪 Загружены куки ({len(cookies)} шт.)")
                    else:
                        self.gui_helper.add_result("⚠️ Куки не найдены", "WARNING")
                    
                    page = context.new_page()
                    
                    # Переходим на целевую страницу
                    self.gui_helper.add_result(f"🔗 Переход на: {add_allow_session_param(config.TARGET_URL, is_headless())}")
                    page.goto(add_allow_session_param(config.TARGET_URL, is_headless()), timeout=30000)
                    
                    try:
                        page.wait_for_load_state('domcontentloaded', timeout=3000)
                    except:
                        pass
                    
                    # Проверяем авторизацию
                    current_url = page.url
                    page_title = page.title()
                    
                    self.gui_helper.add_result(f"📍 URL: {current_url}")
                    self.gui_helper.add_result(f"📄 Заголовок: {page_title}")
                    
                    # Ищем элемент никнейма
                    auth_success = self._check_user_nickname(page, user_login)
                    
                    # Проверяем другие индикаторы
                    indicators_found = self._check_auth_indicators(page)
                    
                    # Общая оценка авторизации
                    is_authorized = (
                        auth_success or
                        config.TARGET_URL in current_url or
                        "login" not in current_url.lower() or
                        len(indicators_found) > 0
                    )
                    
                    if is_authorized:
                        self.gui_helper.add_result(f"✅ Пользователь {user_login} авторизован!", "SUCCESS")
                        self.gui_helper.set_status(f"✅ {user_login} авторизован", "green")
                    else:
                        self.gui_helper.add_result(f"❌ Пользователь {user_login} НЕ авторизован", "ERROR")
                        self.gui_helper.set_status(f"❌ {user_login} не авторизован", "red")
                    
                    browser.close()
                
            except Exception as e:
                error_msg = f"❌ Ошибка тестовой авторизации: {e}"
                self.gui_helper.add_result(error_msg, "ERROR")
                self.gui_helper.set_status("Ошибка тестовой авторизации", "red")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def test_no_authorization(self, headless: bool = True) -> None:
        """
        Тестирование сайта без авторизации.
        
        Args:
            headless: Запуск браузера в headless режиме
        """
        def test_no_auth_thread():
            try:
                self.gui_helper.set_status("Тестирование без авторизации...", "orange")
                self.progress_bar.start()
                self.gui_helper.add_result("Запуск тестирования без авторизации")
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=headless)
                    context = browser.new_context()
                    page = context.new_page()
                    
                    page.goto(config.BASE_URL, timeout=30000)
                    current_url = page.url
                    
                    if "login" in current_url.lower() or current_url == config.BASE_URL:
                        self.gui_helper.add_result("✅ Корректное перенаправление на логин", "SUCCESS")
                        self.gui_helper.set_status("Тестирование без авторизации успешно", "green")
                        
                        # Тестируем доступные страницы
                        test_pages = [config.BASE_URL, config.LOGIN_URL]
                        for test_url in test_pages:
                            try:
                                page.goto(test_url, timeout=15000)
                                self.gui_helper.add_result(f"Доступ к {test_url}: ✅")
                            except Exception:
                                self.gui_helper.add_result(f"Доступ к {test_url}: ❌", "WARNING")
                    else:
                        self.gui_helper.add_result(f"⚠️ Неожиданное поведение: {current_url}", "WARNING")
                        self.gui_helper.set_status("Неожиданное поведение", "orange")
                    
                    browser.close()
                
            except Exception as e:
                error_msg = f"Ошибка тестирования без авторизации: {e}"
                self.gui_helper.add_result(error_msg, "ERROR")
                self.gui_helper.set_status("Ошибка тестирования", "red")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=test_no_auth_thread, daemon=True).start()
    
    def authorize_all_users(self, password_func: Callable[[str], Optional[str]] = None) -> None:
        """
        Массовая авторизация всех пользователей.
        
        Args:
            password_func: Функция для получения пароля пользователя
        """
        def auth_all_thread():
            try:
                self.gui_helper.set_status("Массовая авторизация...", "orange")
                self.progress_bar.start()
                self.gui_helper.add_result("Начата массовая авторизация")
                
                users = self.user_manager.get_all_users()
                for user in users:
                    self._authorize_user_sync(user, password_func)
                
                self.gui_helper.add_result("✅ Массовая авторизация завершена", "SUCCESS")
                self.gui_helper.set_status("Массовая авторизация завершена", "green")
                
            except Exception as e:
                error_msg = f"Ошибка массовой авторизации: {e}"
                self.gui_helper.add_result(error_msg, "ERROR")
                self.gui_helper.set_status("Ошибка массовой авторизации", "red")
            finally:
                self.progress_bar.stop()
        
        threading.Thread(target=auth_all_thread, daemon=True).start()
    
    def _authorize_user_sync(self, user: Dict[str, Any], 
                            password_func: Callable[[str], Optional[str]]) -> None:
        """
        Синхронная авторизация пользователя для массовых операций.
        
        Args:
            user: Данные пользователя
            password_func: Функция для получения пароля
        """
        try:
            user_login = user.get('login')
            self.gui_helper.add_result(f"Авторизация пользователя {user_login}")
            
            cookies_path = config.COOKIES_PATH.parent / f"{user_login}_cookies.json"
            password_to_use = password_func(user_login) if password_func else None
            
            if not password_to_use:
                raise ValueError(f"Пароль для {user_login} не найден")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                perform_login_on_page(
                    page=page,
                    login=user_login,
                    password=password_to_use,
                    cookies_path=cookies_path
                )
                browser.close()
            
            self.user_manager.update_cookie_expiry(user['id'])
            self.gui_helper.add_result(f"✅ {user_login} авторизован", "SUCCESS")
            
        except Exception as e:
            self.gui_helper.add_result(f"❌ Ошибка авторизации {user.get('login')}: {e}", "ERROR")
    
    def _check_user_nickname(self, page: Any, expected_login: str) -> bool:
        """
        Проверка элемента никнейма пользователя на странице.
        
        Args:
            page: Объект страницы Playwright
            expected_login: Ожидаемый логин пользователя
            
        Returns:
            True если никнейм найден и соответствует ожидаемому
        """
        try:
            self.gui_helper.add_result("🔍 Поиск элемента .user-in__nick...")
            
            nickname_locator = page.locator('.user-in__nick')
            element_count = nickname_locator.count()
            
            self.gui_helper.add_result(f"🔢 Найдено элементов: {element_count}")
            
            if element_count > 0 and nickname_locator.first.is_visible(timeout=1000):
                nickname_text = nickname_locator.first.text_content().strip()
                self.gui_helper.add_result(f"✅ Найден никнейм: '{nickname_text}'")
                
                if nickname_text.lower() == expected_login.lower():
                    self.gui_helper.add_result(f"✅ Никнейм совпадает!", "SUCCESS")
                    return True
                else:
                    self.gui_helper.add_result(f"❌ Никнейм не совпадает", "ERROR")
            else:
                self.gui_helper.add_result("❌ Элемент никнейма не найден", "ERROR")
            
            return False
            
        except Exception as e:
            self.gui_helper.add_result(f"❌ Ошибка поиска никнейма: {e}", "ERROR")
            return False
    
    def _check_auth_indicators(self, page: Any) -> list:
        """
        Проверка индикаторов авторизации на странице.
        
        Args:
            page: Объект страницы Playwright
            
        Returns:
            Список найденных индикаторов
        """
        indicators = [
            "[data-testid='user-menu']",
            ".user-profile",
            "#logout",
            "[href*='logout']",
            ".user-name",
            "[class*='user']"
        ]
        
        found_indicators = []
        for indicator in indicators:
            try:
                if page.locator(indicator).first.is_visible(timeout=500):
                    found_indicators.append(indicator)
                    self.gui_helper.add_result(f"✅ Найден индикатор: {indicator}")
            except Exception:
                pass
        
        return found_indicators
