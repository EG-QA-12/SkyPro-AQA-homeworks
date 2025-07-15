"""
HTTP клиент для SSO тестирования через requests API.

Обеспечивает тестирование авторизации между доменами без использования браузера,
что значительно быстрее и надежнее для проверки работы кук авторизации.
"""
from __future__ import annotations

import requests
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


@dataclass
class SSOTestResult:
    """Результат SSO теста для одного домена."""
    domain: str
    is_authenticated_without_cookies: bool
    is_authenticated_with_cookies: bool
    response_status_without_cookies: int
    response_status_with_cookies: int
    html_without_cookies: str = ""
    html_with_cookies: str = ""
    error_message: Optional[str] = None


class SSORequestsClient:
    """
    HTTP клиент для тестирования SSO авторизации через requests.
    
    Выполняет проверку работы кук авторизации на разных доменах
    без использования браузера, что обеспечивает:
    - Высокую скорость выполнения тестов
    - Полную изоляцию между тестами
    - Простую отладку HTTP запросов
    """
    
    def __init__(self, timeout: int = 10):
        """
        Инициализирует SSO клиент.
        
        Args:
            timeout: Таймаут для HTTP запросов в секундах
        """
        self.timeout = timeout
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Настраивает requests сессию с retry политикой."""
        # Настройка retry стратегии для надежности
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Создаем новую сессию для каждого теста (изоляция)
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Настройка заголовков как у реального браузера
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def load_user_cookies(self, username: str) -> List[Dict[str, Any]]:
        """
        Загружает куки пользователя из файла.
        
        Args:
            username: Имя пользователя для загрузки кук
            
        Returns:
            Список кук в формате requests
            
        Raises:
            FileNotFoundError: Если файл кук не найден
            json.JSONDecodeError: Если файл кук поврежден
        """
        cookies_file = Path("cookies") / f"{username}_cookies.json"
        
        if not cookies_file.exists():
            raise FileNotFoundError(f"Файл кук не найден: {cookies_file}")
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # Конвертируем куки в формат requests
            requests_cookies = []
            for cookie in cookies_data:
                # Отфильтровываем только нужную куку авторизации
                if cookie.get('name') == 'test_joint_session':
                    requests_cookies.append({
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain', '.bll.by'),
                        'path': cookie.get('path', '/'),
                    })
            
            logger.info(f"Загружено {len(requests_cookies)} авторизационных кук для {username}")
            return requests_cookies
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга файла кук {cookies_file}: {e}")
            raise
    
    def set_cookies_for_domain(self, cookies: List[Dict[str, Any]], domain: str) -> None:
        """
        Устанавливает куки для конкретного домена.
        
        Args:
            cookies: Список кук для установки
            domain: Домен для установки кук
        """
        for cookie in cookies:
            self.session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                path=cookie['path']
            )
        
        logger.debug(f"Установлено {len(cookies)} кук для домена {domain}")
    
    def clear_cookies(self) -> None:
        """Очищает все куки в текущей сессии."""
        self.session.cookies.clear()
        logger.debug("Куки очищены")
    
    def make_request(self, url: str, with_cookies: bool = False) -> Tuple[int, str]:
        """
        Выполняет HTTP GET запрос.
        
        Args:
            url: URL для запроса
            with_cookies: Использовать ли куки в запросе
            
        Returns:
            Кортеж (status_code, response_text)
            
        Raises:
            requests.RequestException: При ошибке HTTP запроса
        """
        try:
            if not with_cookies:
                # Очищаем куки для запроса без авторизации
                self.clear_cookies()
            
            logger.debug(f"Выполняем {'авторизованный' if with_cookies else 'неавторизованный'} запрос к {url}")
            
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            logger.debug(f"Получен ответ: {response.status_code} от {url}")
            return response.status_code, response.text
            
        except requests.RequestException as e:
            logger.error(f"Ошибка HTTP запроса к {url}: {e}")
            raise
    
    def test_sso_domain(self, domain_url: str, user_cookies: List[Dict[str, Any]]) -> SSOTestResult:
        """
        Тестирует SSO авторизацию на одном домене.
        
        Выполняет полный цикл:
        1. Запрос без кук (должен быть неавторизован)
        2. Запрос с куками (должен быть авторизован)
        
        Args:
            domain_url: URL домена для тестирования
            user_cookies: Куки пользователя для авторизации
            
        Returns:
            Результат тестирования домена
        """
        result = SSOTestResult(
            domain=domain_url,
            is_authenticated_without_cookies=False,
            is_authenticated_with_cookies=False,
            response_status_without_cookies=0,
            response_status_with_cookies=0
        )
        
        try:
            # ШАГ 1: Запрос без кук (проверка неавторизованного состояния)
            logger.info(f"ШАГ 1: Проверка неавторизованного доступа к {domain_url}")
            status_unauth, html_unauth = self.make_request(domain_url, with_cookies=False)
            result.response_status_without_cookies = status_unauth
            
            # ШАГ 2: Установка кук и запрос с авторизацией
            logger.info(f"ШАГ 2: Установка кук и проверка авторизованного доступа к {domain_url}")
            self.set_cookies_for_domain(user_cookies, domain_url)
            status_auth, html_auth = self.make_request(domain_url, with_cookies=True)
            result.response_status_with_cookies = status_auth
            
            # Возвращаем результат с HTML для дальнейшей проверки локаторов
            result.html_without_cookies = html_unauth
            result.html_with_cookies = html_auth
            
            return result
            
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Ошибка при тестировании {domain_url}: {e}")
            return result
    
    def close(self) -> None:
        """Закрывает сессию и освобождает ресурсы."""
        if hasattr(self, 'session'):
            self.session.close()
            logger.debug("SSO сессия закрыта")


def get_available_users() -> List[str]:
    """
    Получает список доступных пользователей из файлов кук.
    
    Returns:
        Список имен пользователей, для которых есть файлы кук
    """
    cookies_dir = Path("cookies")
    if not cookies_dir.exists():
        return []
    
    cookie_files = list(cookies_dir.glob("*_cookies.json"))
    users = [f.stem.replace("_cookies", "") for f in cookie_files]
    
    logger.info(f"Найдено {len(users)} пользователей с файлами кук: {users}")
    return users


def create_isolated_sso_client(timeout: int = 10) -> SSORequestsClient:
    """
    Создает изолированный SSO клиент для тестирования.
    
    Каждый вызов создает полностью новый клиент с чистой сессией,
    обеспечивая полную изоляцию между тестами.
    
    Args:
        timeout: Таймаут для HTTP запросов
        
    Returns:
        Новый изолированный SSO клиент
    """
    return SSORequestsClient(timeout=timeout) 