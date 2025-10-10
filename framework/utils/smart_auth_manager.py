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
from typing import Optional, Dict

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

    def get_valid_session_cookie(self, role: str = "admin") -> Optional[Dict]:
        """
        Получает куку с минимальной проверкой по времени
        
        Args:
            role: Роль пользователя (admin, user)
            
        Returns:
            Optional[Dict]: Полная информация о куке или None
        """
        existing = get_auth_cookies(role)
        if existing:
            cookie = existing[0]
            # Проверить возраст куки - если старше 1 часа, обновить
            if self._is_cookie_too_old(role):
                logger.info("Кука старше 1 часа, обновляем через API")
                return self._perform_auth_and_get_cookie(role)
            logger.info("Используем существующую куку")
            return cookie
        
        # Куки нет в файле - вызвать авторизацию
        logger.info("Куки нет в файле, выполняем авторизацию")
        return self._perform_auth_and_get_cookie(role)

    def _is_cookie_too_old(self, role: str) -> bool:
        """
        Проверяет, старше ли кука 1 часа по времени модификации файла
        
        Args:
            role: Роль пользователя
            
        Returns:
            bool: True если кука старше 1 часа
        """
        try:
            import os
            from pathlib import Path
            
            # Проверяем время модификации файлов куки для данной роли
            project_root = Path(__file__).parent.parent.parent
            cookies_dir = project_root / "cookies"
            
            # Проверяем оба возможных формата файлов куки
            txt_file = cookies_dir / f"{role}_session.txt"
            json_file = cookies_dir / f"{role}_cookies.json"
            
            latest_mod_time = 0
            
            # Проверяем текстовый файл
            if txt_file.exists():
                mod_time = os.path.getmtime(txt_file)
                latest_mod_time = max(latest_mod_time, mod_time)
            
            # Проверяем JSON файл
            if json_file.exists():
                mod_time = os.path.getmtime(json_file)
                latest_mod_time = max(latest_mod_time, mod_time)
            
            # Если ни один файл не найден, считаем куку "свежей"
            if latest_mod_time == 0:
                return False
            
            # Проверяем, старше ли файл 1 часа (3600 секунд)
            return (time.time() - latest_mod_time) > 3600
            
        except Exception as e:
            logger.warning(f"Не удалось проверить возраст куки: {e}")
            return False  # если не можем проверить - считаем свежей

    def _perform_auth_and_get_cookie(self, role: str) -> Optional[Dict]:
        """
        Выполняет таргетированную авторизацию и возвращает куку
        
        Args:
            role: Роль пользователя
            
        Returns:
            Optional[Dict]: Полная информация о куке или None
        """
        try:
            # Загружаем пользователей
            test_users = SecretsManager.load_users_from_csv()
            if not test_users:
                logger.error("Нет тестовых пользователей")
                return None
            
            # Находим пользователя с нужной ролью
            target_user = next((user for user in test_users if user.get('role') == role), None)
            
            if target_user:
                # Таргетированная авторизация только нужного пользователя
                logger.info(f"Выполняем таргетированную авторизацию для {role}")
                mass_api_auth(users=[target_user], threads=1)
            else:
                # Массовая авторизация всех пользователей
                logger.info("Выполняем массовую авторизацию")
                mass_api_auth(users=test_users, threads=5)
            
            # Получаем обновленную куку
            cookies = get_auth_cookies(role)
            session_cookie = next(
                (cookie for cookie in cookies
                 if cookie['name'] == "test_joint_session"),
                None
            )

            if session_cookie:
                logger.info("Успешно получена новая кука")
                return {
                    "name": "test_joint_session",
                    "value": session_cookie["value"],
                    "domain": ".bll.by",
                    "path": "/",
                    "sameSite": "Lax"  # по умолчанию
                }
            else:
                logger.error("Не удалось получить куку после авторизации")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при авторизации: {e}")
            return None

    def get_browser_context_config(self, headless: bool = False) -> tuple:
        """
        Возвращает конфигурацию браузера с anti-bot защитой
        
        Args:
            headless: Режим работы (headless или GUI)
            
        Returns:
            tuple: (context_args, cookie_same_site, cookie_secure)
        """
        # Базовая конфигурация контекста
        user_agent = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        context_args = {
            'user_agent': user_agent,
            'viewport': {'width': 1920, 'height': 1080},
            'locale': 'ru-RU',
            'timezone_id': 'Europe/Minsk',
            'ignore_https_errors': True,
            'bypass_csp': True,
        }

        # sameSite политика в зависимости от режима (из sso_cookies_debug.py)
        if headless:
            cookie_same_site = 'None'  # для headless обход cross-site ограничений
            cookie_secure = True
        else:
            cookie_same_site = 'Lax'   # для GUI как раньше
            cookie_secure = True

        return context_args, cookie_same_site, cookie_secure

    def get_browser_launch_args(self, headless: bool = False) -> Dict:
        """
        Возвращает аргументы запуска браузера с anti-bot защитой
        
        Args:
            headless: Режим работы (headless или GUI)
            
        Returns:
            Dict: Аргументы запуска браузера
        """
        launch_args = [
            '--disable-web-security',  # КРИТИЧНО для cross-domain cookies
            '--disable-blink-features=AutomationControlled',  # Anti-detection
        ]

        if headless:
            # Новый headless режим с лучшей поддержкой кук (из sso_cookies_debug.py)
            launch_args.append('--headless=new')
            disable_features = '--disable-features=IsolateOrigins,site-per-process'
            launch_args.append(disable_features)

        # builtin headless отключаем, управляем через args
        return {
            "headless": False,
            "args": launch_args,
            "slow_mo": 0,
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
