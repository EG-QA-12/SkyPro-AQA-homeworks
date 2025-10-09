#!/usr/bin/env python3
"""
Умный менеджер авторизации

Проверяет валидность существующей куки перед выполнением массовой авторизации.
Выполняет таргетированную авторизацию только нужного пользователя.
"""

import os
import requests
import logging
from typing import Optional, Dict, List
from config.secrets_manager import SecretsManager
from framework.utils.simple_api_auth import mass_api_auth
from framework.utils.auth_cookie_provider import get_auth_cookies

logger = logging.getLogger(__name__)


class SmartAuthManager:
    """
    Умный менеджер авторизации
    
    Оптимизирует процесс авторизации:
    - Проверяет валидность существующей куки
    - Выполняет массовую авторизацию только при необходимости
    - Поддерживает таргетированную авторизацию
    """
    
    def __init__(self):
        """Инициализация менеджера"""
        self.session = requests.Session()
        # 🔄 МЕНЯЕМ: отделяем URL авторизации и URL отправки вопросов
        self.auth_base_url = "https://ca.bll.by"  # ✅ Центр Авторизации
        self.question_base_url = "https://expert.bll.by"  # ✅ Сайт для вопросов

        # Настройка заголовков
        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36'),
            'Accept': ('text/html,application/xhtml+xml,application/xml;'
                       'q=0.9,*/*;q=0.8'),
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # ✨ ДОБАВЛЯЕМ: Anti-detection заголовки
        self._setup_requests_anti_detection()

    @property
    def base_url(self):
        """Backward compatibility: возвращает URL для вопросов"""
        return self.question_base_url

    def _setup_requests_anti_detection(self):
        """
        Настраивает anti-detection для requests (HTTP API)
        
        Добавляет реалистичные заголовки из sso_cookies_debug.py 
        и simple_api_auth.py для обхода антибот защиты.
        """
        anti_detection_headers = {
            # ✨ Из sso_cookies_debug.py и simple_api_auth.py:
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;'
                'q=0.9,image/webp,*/*;q=0.8'
            ),
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        self.session.headers.update(anti_detection_headers)
        logger.info("🛡️ Anti-detection для requests настроен")

    def _is_headless(self) -> bool:
        """
        Проверяет, запущен ли тест в headless режиме

        Returns:
            bool: True если headless, False если GUI режим
        """
        return os.getenv('HEADLESS', 'false').lower() == 'true'
    
    def check_cookie_validity(self, session_cookie: str) -> bool:
        """
        Проверяет валидность сессионной куки
        
        Args:
            session_cookie: Значение сессионной куки
            
        Returns:
            bool: True если кука валидна, False если нет
        """
        try:
            # Устанавливаем куку
            self.session.cookies.set("test_joint_session", session_cookie)
            
            # Делаем тестовый запрос к защищенной странице
            response = self.session.get(f"{self.base_url}/questions", allow_redirects=False)
            
            # Анализируем ответ
            if response.status_code == 200:
                # Проверяем, что это не страница входа
                if "войти" not in response.text.lower() and "login" not in response.text.lower():
                    logger.info("Кука валидна - авторизация не требуется")
                    return True
                else:
                    logger.warning("Кука невалидна - обнаружена страница входа")
                    return False
            elif response.status_code == 302:
                # Редирект на страницу входа
                logger.warning("Кука невалидна - редирект на страницу входа")
                return False
            else:
                logger.warning(f"Неожиданный статус код: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при проверке куки: {e}")
            return False
    
    def get_valid_session_cookie(self, role: str = "admin", force_check: bool = False) -> Optional[Dict]:
        """
        Получает валидную сессионную куку с полной информацией

        В GUI режиме проверяет валидность куки и при необходимости обновляет через API.
        В headless режиме проверяет валидность куки и выполняет авторизацию если нужно.

        Args:
            role: Роль пользователя (admin, user)
            force_check: Принудительная проверка валидности куки даже в GUI режиме

        Returns:
            Optional[Dict]: Полная информация о куке или None
        """
        # GUI режим: проверяем валидность куки и обновляем при необходимости
        if not self._is_headless() or force_check:
            logger.info("GUI режим: проверяем валидность куки")
            try:
                existing_cookies = get_auth_cookies(role=role)
                session_cookie = next(
                    (cookie for cookie in existing_cookies
                     if cookie['name'] == "test_joint_session"),
                    None
                )

                if session_cookie:
                    # Проверяем валидность куки в GUI режиме
                    if self.check_cookie_validity(session_cookie["value"]):
                        logger.info("Кука валидна - используем существующую")
                        return {
                            "name": "test_joint_session",
                            "value": session_cookie["value"],
                            "domain": ".bll.by",
                            "path": "/",
                            "sameSite": "Lax"
                        }
                    else:
                        logger.warning("Кука невалидна - выполняем авторизацию")
                        # Кука невалидна, выполняем авторизацию
                        return self._perform_auth_and_get_cookie(role)
                else:
                    logger.warning("Кука не найдена в файлах - выполняем авторизацию")
                    return self._perform_auth_and_get_cookie(role)

            except Exception as e:
                logger.error(f"Ошибка при чтении файла куки: {e}")
                return None

        # Headless режим: полная проверка и авторизация
        logger.info("Headless режим: полная проверка и авторизация")
        try:
            existing_cookies = get_auth_cookies(role=role)
            session_cookie = next(
                (cookie for cookie in existing_cookies
                 if cookie['name'] == "test_joint_session"),
                None
            )

            if session_cookie and self.check_cookie_validity(session_cookie["value"]):
                logger.info("Используем существующую валидную куку")
                return {
                    "name": "test_joint_session",
                    "value": session_cookie["value"],
                    "domain": ".bll.by",
                    "path": "/",
                    "sameSite": "Lax"
                }

        except Exception as e:
            logger.warning(f"Ошибка при получении существующей куки: {e}")

        # Выполняем авторизацию
        return self._perform_auth_and_get_cookie(role)
    
    def _perform_auth_and_get_cookie(self, role: str) -> Optional[str]:
        """
        Выполняет авторизацию и получает куку
        
        Args:
            role: Роль пользователя
            
        Returns:
            Optional[str]: Сессионная кука или None
        """
        try:
            # Загружаем пользователей
            test_users = SecretsManager.load_users_from_csv()
            if not test_users:
                logger.error("Нет тестовых пользователей")
                return None
            
            # Находим пользователя с нужной ролью
            target_user = None
            for user in test_users:
                if user.get('role') == role:
                    target_user = user
                    break
            
            if target_user:
                # Таргетированная авторизация только нужного пользователя
                logger.info(f"Выполняем таргетированную авторизацию для {role}")
                mass_api_auth(users=[target_user], threads=1)
            else:
                # Массовая авторизация всех пользователей
                logger.info("Выполняем массовую авторизацию")
                mass_api_auth(users=test_users, threads=5)
            
            # Получаем куку после авторизации
            cookies = get_auth_cookies(role=role)
            session_cookie = next(
                (cookie for cookie in cookies
                 if cookie['name'] == "test_joint_session"),
                None
            )

            if session_cookie:
                logger.info("Успешно получена новая кука")
                # Возвращаем полную информацию о куке
                return {
                    "name": "test_joint_session",
                    "value": session_cookie["value"],
                    "domain": ".bll.by",
                    "path": "/",
                    "sameSite": "Lax"
                }
            else:
                logger.error("Не удалось получить куку после авторизации")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при авторизации: {e}")
            return None
    
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
            cookie_value = session_cookie.get("value") if isinstance(session_cookie, dict) else session_cookie

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
