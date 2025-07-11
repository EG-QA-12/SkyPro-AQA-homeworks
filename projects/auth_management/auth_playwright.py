#!/usr/bin/env python3
"""
Модуль авторизации на базе Playwright для высокопроизводительного тестирования.

Обеспечивает:
- Быструю авторизацию пользователей
- Параллельную обработку
- Стабильную работу с современными веб-приложениями
- Эффективное управление ресурсами
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .config import config
from .logger import setup_logger


class PlaywrightAuthenticator:
    """
    Класс для авторизации пользователей через Playwright.
    
    Преимущества перед Selenium:
    - Быстрее в 2-3 раза
    - Лучшая стабильность
    - Нативная поддержка асинхронности
    - Меньшее потребление ресурсов
    """

    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Инициализирует аутентификатор.
        
        Args:
            headless: Запускать браузер в headless режиме
            timeout: Таймаут для операций (мс)
        """
        self.headless = headless
        self.timeout = timeout
        self.logger = setup_logger(__name__)
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход."""
        await self.start_browser()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход."""
        await self.close_browser()
        
    async def start_browser(self) -> None:
        """Запускает браузер и создает контекст."""
        try:
            self.playwright = await async_playwright().start()
            
            # Используем Chromium для лучшей совместимости
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
            
            # Создаем контекст браузера
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # Устанавливаем таймауты
            self.context.set_default_timeout(self.timeout)
            self.context.set_default_navigation_timeout(self.timeout)
            
            self.logger.info("Playwright браузер успешно запущен")
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска браузера: {e}")
            raise
            
    async def close_browser(self) -> None:
        """Закрывает браузер и освобождает ресурсы."""
        try:
            if self.context:
                await self.context.close()
                
            if self.browser:
                await self.browser.close()
                
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
                
            self.logger.info("Playwright браузер закрыт")
            
        except Exception as e:
            self.logger.error(f"Ошибка закрытия браузера: {e}")
            
    async def authenticate_user(self, username: str, password: str, 
                              user_id: Optional[int] = None) -> Tuple[bool, Dict]:
        """
        Выполняет авторизацию пользователя.
        
        Args:
            username: Имя пользователя
            password: Пароль
            user_id: ID пользователя (опционально)
            
        Returns:
            tuple: (успех, данные_сессии)
        """
        start_time = time.time()
        
        try:
            # Создаем новую страницу
            page = await self.context.new_page()
            
            # Переходим на страницу входа
            await page.goto(config.LOGIN_URL, wait_until='networkidle')
            
            # Ожидаем загрузки формы входа (более универсальные селекторы)
            login_selectors = [
                'input[name="login"]',
                'input[name="username"]', 
                'input[type="text"]',
                '#login',
                '#username',
                '.login-input'
            ]
            
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                '#password',
                '.password-input'
            ]
            
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                '.btn-login',
                '.submit-btn',
                'button:has-text("Войти")',
                'button:has-text("Login")',
                'form button'
            ]
            
            # Ищем поле логина
            login_input = None
            for selector in login_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    login_input = selector
                    break
                except:
                    continue
            
            if not login_input:
                raise Exception("Не найдено поле для ввода логина")
                
            # Ищем поле пароля
            password_input = None
            for selector in password_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    password_input = selector
                    break
                except:
                    continue
                    
            if not password_input:
                raise Exception("Не найдено поле для ввода пароля")
            
            # Заполняем форму
            await page.fill(login_input, username)
            await page.fill(password_input, password)
            
            # Ищем кнопку отправки
            submit_button = None
            for selector in submit_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=2000)
                    submit_button = selector
                    break
                except:
                    continue
                    
            if not submit_button:
                # Пробуем отправить форму через Enter
                await page.press(password_input, 'Enter')
            else:
                await page.click(submit_button)
            
            # Ожидаем редиректа или сообщения об ошибке
            try:
                # Ожидаем успешной авторизации (редирект на главную)
                await page.wait_for_url('**/main', timeout=10000)
                auth_success = True
                
            except Exception:
                # Проверяем наличие сообщения об ошибке
                error_element = await page.query_selector('.error-message, .alert-danger, [class*="error"]')
                if error_element:
                    error_text = await error_element.text_content()
                    self.logger.warning(f"Ошибка авторизации для {username}: {error_text}")
                    auth_success = False
                else:
                    # Возможно, медленная загрузка - даем еще время
                    await asyncio.sleep(2)
                    current_url = page.url
                    auth_success = '/main' in current_url or '/dashboard' in current_url
            
            if auth_success:
                # Получаем cookies
                cookies = await self.context.cookies()
                
                # Получаем информацию о пользователе
                user_info = await self._extract_user_info(page)
                
                execution_time = time.time() - start_time
                
                session_data = {
                    'user_id': user_id or user_info.get('id'),
                    'username': username,
                    'cookies': cookies,
                    'user_info': user_info,
                    'timestamp': int(time.time()),
                    'execution_time': execution_time,
                    'browser_type': 'playwright-chromium'
                }
                
                self.logger.info(f"Пользователь {username} успешно авторизован за {execution_time:.2f}с")
                await page.close()
                return True, session_data
                
            else:
                await page.close()
                return False, {'error': 'Неверные учетные данные'}
                
        except Exception as e:
            self.logger.error(f"Ошибка авторизации {username}: {e}")
            return False, {'error': str(e)}
            
    async def _extract_user_info(self, page: Page) -> Dict:
        """
        Извлекает информацию о пользователе со страницы.
        
        Args:
            page: Страница Playwright
            
        Returns:
            dict: Информация о пользователе
        """
        try:
            # Пытаемся получить данные из различных возможных источников
            user_info = {}
            
            # Попытка получить данные из JavaScript
            try:
                js_user_data = await page.evaluate("""
                    () => {
                        // Поиск данных пользователя в глобальных переменных
                        if (window.currentUser) return window.currentUser;
                        if (window.user) return window.user;
                        if (window.userData) return window.userData;
                        
                        // Поиск в localStorage
                        const stored = localStorage.getItem('user') || localStorage.getItem('currentUser');
                        if (stored) {
                            try {
                                return JSON.parse(stored);
                            } catch (e) {
                                return {};
                            }
                        }
                        
                        return {};
                    }
                """)
                
                if js_user_data:
                    user_info.update(js_user_data)
                    
            except Exception:
                pass
            
            # Попытка получить данные из элементов страницы
            try:
                # Ищем элементы с информацией о пользователе
                selectors = [
                    '[data-user-id]',
                    '[data-username]', 
                    '.user-info',
                    '.profile-info',
                    '#user-data'
                ]
                
                for selector in selectors:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        # Получаем атрибуты data-*
                        attrs = await element.evaluate('el => Array.from(el.attributes).map(attr => [attr.name, attr.value])')
                        for attr_name, attr_value in attrs:
                            if attr_name.startswith('data-user-'):
                                key = attr_name.replace('data-user-', '')
                                user_info[key] = attr_value
                                
            except Exception:
                pass
                
            return user_info
            
        except Exception as e:
            self.logger.debug(f"Не удалось извлечь информацию о пользователе: {e}")
            return {}
            
    async def batch_authenticate(self, users: List[Dict]) -> List[Tuple[bool, Dict]]:
        """
        Выполняет пакетную авторизацию пользователей.
        
        Args:
            users: Список пользователей для авторизации
            
        Returns:
            list: Результаты авторизации
        """
        results = []
        
        for i, user in enumerate(users):
            username = user.get('username', user.get('login', ''))
            password = user.get('password', '')
            user_id = user.get('id')
            
            if not username or not password:
                self.logger.warning(f"Пропущен пользователь {i+1}: отсутствует username или password")
                results.append((False, {'error': 'Отсутствуют учетные данные'}))
                continue
                
            self.logger.info(f"Авторизация пользователя {i+1}/{len(users)}: {username}")
            
            success, session_data = await self.authenticate_user(username, password, user_id)
            results.append((success, session_data))
            
            # Небольшая пауза между авторизациями
            await asyncio.sleep(0.5)
            
        return results


class PlaywrightAuthManager:
    """
    Менеджер для управления авторизацией через Playwright.
    """
    
    def __init__(self, headless: bool = True):
        """
        Инициализирует менеджер.
        
        Args:
            headless: Запускать браузер в headless режиме
        """
        self.headless = headless
        self.logger = setup_logger(__name__)
        
    async def authenticate_users_from_csv(self, csv_path: str, 
                                        force_reauth: bool = False) -> Dict:
        """
        Авторизует пользователей из CSV файла.
        
        Args:
            csv_path: Путь к CSV файлу
            force_reauth: Принудительная переавторизация
            
        Returns:
            dict: Результаты авторизации
        """
        import csv
        
        # Загружаем пользователей из CSV
        users = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                users = list(reader)
                
        except Exception as e:
            self.logger.error(f"Ошибка чтения CSV: {e}")
            return {'success': [], 'failed': [], 'error': str(e)}
        
        if not users:
            return {'success': [], 'failed': [], 'error': 'CSV файл пуст'}
            
        self.logger.info(f"Начинаем обработку {len(users)} пользователей из CSV")
        
        # Выполняем авторизацию
        async with PlaywrightAuthenticator(headless=self.headless) as auth:
            results = await auth.batch_authenticate(users)
            
        # Обрабатываем результаты
        successful = []
        failed = []
        
        for i, (success, session_data) in enumerate(results):
            username = users[i].get('username', users[i].get('login', f'user_{i}'))
            
            if success:
                successful.append(username)
                # Сохраняем cookies и данные сессии
                await self._save_session_data(username, session_data)
            else:
                failed.append(username)
                
        self.logger.info(f"CSV обработка завершена. Успешно: {len(successful)}, Ошибок: {len(failed)}")
        
        return {
            'success': successful,
            'failed': failed,
            'total': len(users)
        }
        
    async def _save_session_data(self, username: str, session_data: Dict) -> None:
        """
        Сохраняет данные сессии пользователя.
        
        Args:
            username: Имя пользователя
            session_data: Данные сессии
        """
        try:
            # Сохраняем cookies в файл
            cookies_dir = Path('data')
            cookies_dir.mkdir(exist_ok=True)
            
            cookies_file = cookies_dir / f"{username}_cookies.json"
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Данные сессии для {username} сохранены в {cookies_file}")
            
            # Здесь можно добавить сохранение в БД
            # await self._save_to_database(session_data)
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения данных для {username}: {e}")


# Функция для совместимости с существующим кодом
async def authenticate_user_playwright(username: str, password: str, 
                                     headless: bool = True) -> Tuple[bool, Dict]:
    """
    Совместимая функция для авторизации одного пользователя.
    
    Args:
        username: Имя пользователя
        password: Пароль
        headless: Headless режим
        
    Returns:
        tuple: (успех, данные_сессии)
    """
    async with PlaywrightAuthenticator(headless=headless) as auth:
        return await auth.authenticate_user(username, password)
