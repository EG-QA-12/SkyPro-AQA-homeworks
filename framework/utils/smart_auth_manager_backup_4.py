#!/usr/bin/env python3
"""
Умный менеджер авторизации - УПРОЩЕННАЯ ВЕРСИЯ

Простая система авторизации с минимальной проверкой по времени.
- Получает куки из файлов
- Если кука старше 1 часа - обновляет через API
- Использует ca.bll.by как центр авторизации
- Включает важные anti-bot защиты из sso_cookies_debug.py
"""

import time
import requests
import logging
from typing import Optional, Dict, List

from config.secrets_manager import SecretsManager
from framework.utils.simple_api_auth import mass_api_auth
from framework.utils.auth_cookie_provider import get_auth_cookies

logger = logging.getLogger(__name__)


class SmartAuthManager:
    """
    Упрощенный менеджер авторизации
    
    Принцип работы:
    - Берет куки из файлов
    - Проверяет возраст (старше 1 часа - обновить через API)
    - Использует ca.bll.by как центр авторизации
    """
    
    def __init__(self):
        """Инициализация менеджера"""
        self.session = requests.Session()
        self.base_url = "https://expert.bll.by"  # Экспертная система

        # Базовые anti-detection заголовки (без сложных Sec-Fetch)
        basic_headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;'
                'q=0.9,image/webp,*/*;q=0.8'
            ),
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.session.headers.update(basic_headers)

    def get_valid_session_cookie(self, role: str = "admin") -> Optional[str]:
        """
        Получает строковое значение куки для API клиентов (обратная совместимость)

        Args:
            role: Роль пользователя (admin, user)

        Returns:
            Optional[str]: Строковое значение куки или None
        """
        storage_state = self.get_valid_storage_state(role)
        if storage_state and "cookies" in storage_state:
            # Извлекаем значение куки из storage_state
            for cookie in storage_state["cookies"]:
                if cookie.get("name") == "test_joint_session":
                    return cookie.get("value")
        return None

    def get_valid_storage_state(self, role: str = "admin") -> Optional[Dict]:
        """
        Получает storage_state с минимальной проверкой по времени

        Args:
            role: Роль пользователя (admin, user)

        Returns:
            Optional[Dict]: Полное storage_state или None
        """
        logger.info(f"[DEBUG] get_valid_storage_state called for role: {role}")

        # Проверка наличия и актуальности storage_state
        is_too_old = self._is_storage_state_too_old(role)
        logger.info(f"[DEBUG] _is_storage_state_too_old result: {is_too_old}")

        if is_too_old:
            logger.info("Storage state старше 1 часа, обновляем через Playwright")
            result = self._perform_auth_and_get_storage_state(role)
            logger.info(f"[DEBUG] _perform_auth_and_get_storage_state result: {result is not None}")
            return result

        logger.info("Используем существующее storage_state")
        result = self._load_storage_state(role)
        logger.info(f"[DEBUG] _load_storage_state result: {result is not None}")
        return result

    def get_valid_cookies_list(self, role: str = "admin") -> Optional[List[Dict]]:
        """
        Получает список кук в формате Playwright для браузерных тестов

        ИСПРАВЛЕНИЕ: Теперь возвращает куки из ПОЛНОГО storage_state
        (включая правильную sameSite политику для headless режима)

        Args:
            role: Роль пользователя (admin, user)

        Returns:
            Optional[List[Dict]]: Список кук для context.add_cookies() или None
        """
        logger.info(f"[DEBUG] get_valid_cookies_list called for role: {role}")
        storage_state = self.get_valid_storage_state(role)
        logger.info(f"[DEBUG] storage_state result: {storage_state is not None}")

        if storage_state and "cookies" in storage_state:
            cookies_count = len(storage_state["cookies"])
            logger.info(f"[DEBUG] Found {cookies_count} cookies in FULL storage_state")

            # ДОБАВЛЕНО: Проверяем правильность sameSite для headless режима
            for cookie in storage_state["cookies"]:
                if cookie.get('name') == 'test_joint_session':
                    logger.info(f"[COOKIE_CHECK] Session cookie sameSite: {cookie.get('sameSite')}, "
                              f"secure: {cookie.get('secure')}, domain: {cookie.get('domain')}")

            return storage_state["cookies"]

        logger.warning(f"[DEBUG] No cookies found in FULL storage_state for role {role}")
        return None

    def _is_storage_state_too_old(self, role: str) -> bool:
        """
        Проверяет, старше ли куки 1 часа по времени модификации файла

        Args:
            role: Роль пользователя

        Returns:
            bool: True если куки старше 1 часа
        """
        try:
            import os
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            cookies_dir = project_root / "cookies"
            cookie_file = cookies_dir / f"{role}_cookies.json"

            if cookie_file.exists():
                mod_time = os.path.getmtime(cookie_file)
                age_hours = (time.time() - mod_time) / 3600
                logger.info(".1f")
                return age_hours > 1  # Старше 1 часа

            return True  # Если файла нет, считаем что нужно обновить

        except Exception as e:
            logger.error(f"Ошибка при проверке возраста кук: {e}")
            return True

    def _perform_auth_and_get_storage_state(self, role: str) -> Optional[Dict]:
        """
        Выполняет авторизацию через Playwright и возвращает ПОЛНЫЙ storage_state

        КЛЮЧЕВЫЕ ИСПРАВЛЕНИЯ (из sso_cookies_debug.py):
        - Использует ПОЛНЫЙ storage_state вместо простых кук
        - Упрощенная проверка авторизации (ищет профиль, а не конкретный URL)
        - Правильная sameSite политика для headless режима
        - Увеличенные таймауты

        Args:
            role: Роль пользователя

        Returns:
            Optional[Dict]: Полное storage_state или None
        """
        try:
            import nest_asyncio
            nest_asyncio.apply()

            import asyncio
            from rebrowser_playwright.async_api import async_playwright
            from config.secrets_manager import SecretsManager

            # Загружаем пользователей
            test_users = SecretsManager.load_users_from_csv()
            if not test_users:
                logger.error("Нет тестовых пользователей")
                return None

            # Находим пользователя с нужной ролью
            target_user = next(
                (user for user in test_users if user.get('role') == role), None
            )
            if not target_user:
                logger.error(f"Не найден пользователь с ролью {role}")
                return None

            logger.info(f"Выполняем Playwright авторизацию для {role}")

            # Асинхронная функция авторизации (КОПИЯ ИЗ РАБОЧЕГО СКРИПТА)
            async def _async_auth():
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        **self.get_browser_launch_args(headless=True)
                    )
                    context = await browser.new_context(
                        user_agent=(
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        ),
                        viewport={"width": 1920, "height": 1080},
                        locale="ru-RU",
                        timezone_id="Europe/Minsk",
                        ignore_https_errors=True,
                        bypass_csp=True,
                    )
                    page = await context.new_page()

                    # Anti-detection script - помогает обходить защиту от ботов
                    await page.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                    """)

                    # Переход на страницу входа
                    await page.goto(
                        "https://ca.bll.by/login", wait_until="domcontentloaded"
                    )

                    # Заполнение формы
                    await page.fill('input[name="lgn"]', target_user['login'])
                    await page.fill(
                        'input[name="password"]', target_user['password']
                    )
                    await page.click('input[type="submit"]')

                    # УМНОЕ ОЖИДАНИЕ РЕЗУЛЬТАТА АВТОРИЗАЦИИ (вместо sleep)
                    # Ждем ЛИБО изменение URL, ЛИБО появление профиля
                    try:
                        await page.wait_for_function("""
                            () => {
                                // Успех: URL изменился (редирект после авторизации)
                                if (!window.location.href.includes('/login')) {
                                    return true;
                                }
                                // Успех: профиль появился
                                if (document.querySelector('a[class*="top-nav__item top-nav__profile"]')) {
                                    return true;
                                }
                                // Продолжаем проверку (функция вернет undefined, продолжая ожидание)
                                return false;
                            }
                        """, timeout=5000)  # Максимум 5 сек

                        logger.info("[AUTH_CHECK] Auth result detected")

                    except Exception as e:
                        logger.error(f"[AUTH_TIMEOUT] Auth check timeout: {e}")
                        return None

                    # ФИНАЛЬНАЯ ПРОВЕРКА АВТОРИЗАЦИИ
                    current_url = page.url
                    logger.info(f"[AUTH_CHECK] Final URL: {current_url}")

                    # Проверяем успешную авторизацию
                    if "login" not in current_url:
                        # Подтверждаем наличие профиля
                        profile_selector = 'a[class*="top-nav__item top-nav__profile"]'
                        try:
                            profile_element = await page.wait_for_selector(
                                profile_selector, timeout=8000  # Уменьшен до 8 сек
                            )
                            if profile_element:
                                logger.info("[AUTH_SUCCESS] Profile confirmed - auth successful")
                            else:
                                logger.error("[AUTH_FAIL] Profile not found after URL change")
                                return None
                        except Exception as e:
                            logger.error(f"[AUTH_FAIL] Error confirming profile: {e}")
                            return None
                    else:
                        logger.error("[AUTH_FAIL] Still on login page - auth failed")
                        return None

                    # Сохраняем ПОЛНЫЙ storage_state (как в рабочем скрипте)
                    storage_state = await context.storage_state()
                    logger.info(f"[STORAGE] Captured full storage_state: "
                              f"{len(storage_state.get('cookies', []))} cookies")

                    await browser.close()
                    return storage_state

            # Запускаем асинхронную авторизацию
            storage_state = asyncio.run(_async_auth())

            if storage_state:
                logger.info("Успешно получено ПОЛНОЕ storage_state")

                # Сохраняем storage_state в файл
                self._save_storage_state(role, storage_state)
                return storage_state
            else:
                logger.error("Не удалось получить storage_state")
                return None

        except Exception as e:
            logger.error(f"Ошибка при авторизации: {e}")
            return None

    def _load_storage_state(self, role: str) -> Optional[Dict]:
        """
        Загружает ПОЛНЫЙ storage_state из файла storage/{role}_storage_state.json

        ИСПРАВЛЕНИЕ: Теперь загружает полный storage_state (cookies + origins + storage)
        вместо простого массива кук

        Args:
            role: Роль пользователя

        Returns:
            Optional[Dict]: Полный storage state в формате Playwright или None
        """
        try:
            import json
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            storage_dir = project_root / "storage"
            storage_file = storage_dir / f"{role}_storage_state.json"

            if storage_file.exists():
                with open(storage_file, 'r', encoding='utf-8') as f:
                    storage_state = json.load(f)

                cookies_count = len(storage_state.get('cookies', []))
                origins_count = len(storage_state.get('origins', []))

                logger.info(f"Загружен ПОЛНЫЙ storage_state из: {storage_file}")
                logger.info(f"Storage state содержит: {cookies_count} куков, {origins_count} origins")

                return storage_state

            logger.info(f"Файл storage_state не найден: {storage_file}")
            return None

        except Exception as e:
            logger.error(f"Ошибка при загрузке ПОЛНОГО storage_state: {e}")
            return None

    def _save_storage_state(self, role: str, storage_state: Dict) -> bool:
        """
        Сохраняет ПОЛНЫЙ storage_state в файл storage/{role}_storage_state.json

        ИСПРАВЛЕНИЕ: Теперь сохраняет полный storage_state (cookies + origins + storage)
        в правильную директорию storage/

        Args:
            role: Роль пользователя
            storage_state: Полный storage state для сохранения

        Returns:
            bool: True если сохранение успешно
        """
        try:
            import json
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            storage_dir = project_root / "storage"
            storage_dir.mkdir(exist_ok=True)

            storage_file = storage_dir / f"{role}_storage_state.json"

            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(storage_state, f, indent=2, ensure_ascii=False)

            cookies_count = len(storage_state.get('cookies', []))
            origins_count = len(storage_state.get('origins', []))

            logger.info(f"ПОЛНЫЙ storage_state сохранен: {storage_file}")
            logger.info(f"Сохранено: {cookies_count} куков, {origins_count} origins")

            return True

        except Exception as e:
            logger.error(f"Ошибка при сохранении ПОЛНОГО storage_state: {e}")
            return False

    def get_browser_launch_args(self, headless: bool = False) -> Dict:
        """
        Возвращает оптимизированные аргументы запуска браузера для скорости

        Args:
            headless: Режим работы (headless или GUI)

        Returns:
            Dict: Аргументы запуска браузера
        """
        launch_args = [
            '--disable-web-security',  # КРИТИЧНО для cross-domain cookies
            '--disable-blink-features=AutomationControlled',  # Anti-detection
            '--disable-features=VizDisplayCompositor',  # Чистая визуализация
            '--disable-dev-shm-usage',  # Экономия памяти
            '--no-first-run',  # Пропуск первого запуска
            '--disable-default-apps',  # Отключить дефолтные приложения
            '--disable-extensions',  # Отключить расширения
            '--disable-background-timer-throttling',  # Таймеры в фоне
            '--disable-backgrounding-occluded-windows',  # Фоновые окна
            '--disable-renderer-backgrounding',  # Фоновый рендеринг
        ]

        if headless:
            # Оптимизированный headless режим для скорости
            launch_args.extend([
                '--headless=new',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',  # Для headless стабильности
                '--disable-gpu',  # Отключить GPU в headless
                '--disable-software-rasterizer',  # Отключить software rasterizer
                '--disable-background-networking',  # Отключить фоновые сети
            ])

        return {
            "headless": False,  # Управляем через аргументы
            "args": launch_args,
            "slow_mo": 0,  # Без задержек
            "chromium_sandbox": not headless,
        }

    def test_question_submission(self, session_cookie: str, question_text: str) -> Dict:
        """
        Тестирует отправку вопроса для проверки валидности куки
        
        Args:
            session_cookie: Сессионная кука
            question_text: Текст вопроса для тестирования
            
        Returns:
            Dict: Результат тестирования
        """
        try:
            from requests_toolbelt import MultipartEncoder
            
            # Создаем form-data
            form_data = MultipartEncoder(
                fields={'p': question_text}
            )
            
            # Настраиваем заголовки
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                'Referer': f'{self.base_url}/',
                'Origin': self.base_url,
                'Content-Type': form_data.content_type
            }
            
            # Извлекаем значение куки из словаря если необходимо
            if isinstance(session_cookie, dict):
                cookie_value = session_cookie.get("value")
            else:
                cookie_value = session_cookie
            
            # Отправляем запрос
            response = self.session.post(
                f"{self.base_url}/questions?allow-session=2",
                data=form_data,
                cookies={"test_joint_session": cookie_value},
                headers=headers
            )
            
            # Анализируем результат
            if response.status_code == 200:
                # Упрощенная проверка: считаем успехом любой ответ 200
                logger.info(f"Получен ответ при отправке вопроса: статус {response.status_code}")
                
                # Сохраняем первые 200 символов ответа для отладки
                logger.debug(f"Текст ответа: {response.text[:200]}...")
                
                # Для отладки - печатаем информацию о запросе
                print(f"\nОтправлен запрос на URL: {self.base_url}/questions?allow-session=2")
                print(f"Заголовки запроса: {headers}")
                print(f"Текст вопроса: {question_text}")
                
                return {
                    "valid": True,
                    "success": True,  # Считаем успешной любую отправку с кодом 200
                    "status_code": response.status_code,
                    "message": "Успешная отправка"
                }
            else:
                return {
                    "valid": False,
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Ошибка при тестировании отправки вопроса: {e}")
            return {
                "valid": False,
                "success": False,
                "status_code": 0,
                "message": str(e)
            }
