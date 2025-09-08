"""
Базовый API клиент для работы с административным API.

Этот клиент предоставляет унифицированный интерфейс для работы с API,
включая обработку авторизации, CSRF токенов и повторных попыток.
"""

import requests
import logging
from typing import Dict, Optional, Any, Union
from urllib.parse import urljoin, unquote
from framework.utils.auth_cookie_provider import AuthCookieProvider
from framework.utils.smart_auth_manager import SmartAuthManager

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """
    Базовый API клиент с поддержкой авторизации и обработки ошибок.
    
    Основные возможности:
    - Автоматическая авторизация и обновление кук
    - Обработка CSRF токенов
    - Retry логика для 401/419 ошибок
    - Централизованная обработка ошибок
    - Типизированные ответы
    """
    
    def __init__(self, base_url: str = "https://expert.bll.by", role: str = "admin"):
        """
        Инициализация API клиента.
        
        Args:
            base_url: Базовый URL API
            role: Роль пользователя для авторизации
        """
        self.base_url = base_url.rstrip('/')
        self.role = role
        self.session = requests.Session()
        self.auth_manager = SmartAuthManager()
        self.cookie_provider = AuthCookieProvider()
        
        # Настройка заголовков по умолчанию
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        })
        
        # Инициализация авторизации
        self._initialize_session()
    
    def _initialize_session(self) -> None:
        """Инициализация сессии с авторизационными куками."""
        session_cookie = self.auth_manager.get_valid_session_cookie(role=self.role)
        if session_cookie:
            self.session.cookies.set("test_joint_session", session_cookie)
            logger.info(f"Сессия инициализирована для роли: {self.role}")
        else:
            logger.warning(f"Не удалось инициализировать сессию для роли: {self.role}")
            
    def _clear_session_cookies(self) -> None:
        """Очистка авторизационных кук из сессии."""
        self.session.cookies.clear()
        logger.info(f"Куки сессии очищены для роли: {self.role}")
        
    def _set_session_cookie(self, session_cookie: str) -> None:
        """Установка авторизационной куки в сессию."""
        self._clear_session_cookies()
        self.session.cookies.set("test_joint_session", session_cookie)
        logger.info(f"Установлена кука сессии для роли: {self.role}")
    
    def _get_csrf_tokens(self) -> Dict[str, Optional[str]]:
        """
        Получение CSRF токенов для текущей сессии.
        
        Returns:
            Dict с токенами: xsrf_token, form_token
        """
        try:
            from framework.utils.html_parser import fetch_csrf_tokens_from_panel
            tokens = fetch_csrf_tokens_from_panel(self.session, self.base_url)
            return {
                'xsrf_token': unquote(tokens.get('xsrf_cookie') or '') if tokens.get('xsrf_cookie') else None,
                'form_token': tokens.get('form_token')
            }
        except Exception as e:
            logger.error(f"Ошибка получения CSRF токенов: {e}")
            return {'xsrf_token': None, 'form_token': None}
    
    def _refresh_session(self) -> bool:
        """
        Обновление сессии при 401/419 ошибках.
        
        Returns:
            bool: True если сессия успешно обновлена
        """
        try:
            logger.info(f"Обновление сессии для роли: {self.role}")
            new_cookie = self.auth_manager._perform_api_login(self.role)
            if new_cookie:
                self.session.cookies.clear()
                self.session.cookies.set("test_joint_session", new_cookie)
                logger.info("Сессия успешно обновлена")
                return True
            else:
                logger.error("Не удалось обновить сессию")
                return False
        except Exception as e:
            logger.error(f"Ошибка обновления сессии: {e}")
            return False
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 15,
        retry_on_auth_error: bool = True
    ) -> requests.Response:
        """
        Выполнение HTTP запроса с обработкой ошибок.
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Конечная точка API
            data: Данные для отправки в теле запроса
            params: Параметры запроса
            headers: Дополнительные заголовки
            timeout: Таймаут запроса
            retry_on_auth_error: Повторить при 401/419 ошибках
            
        Returns:
            requests.Response: Ответ сервера
            
        Raises:
            requests.RequestException: При ошибках сети
        """
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        # Объединяем заголовки
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        # Первый запрос
        try:
            response = self.session.request(
                method=method,
                url=url,
                data=data,
                params=params,
                headers=request_headers,
                timeout=timeout
            )
            
            # Обработка 401/419 ошибок
            if response.status_code in (401, 419) and retry_on_auth_error:
                logger.warning(f"Получен статус {response.status_code}, обновление сессии...")
                if self._refresh_session():
                    # Повторный запрос с обновленной сессией
                    response = self.session.request(
                        method=method,
                        url=url,
                        data=data,
                        params=params,
                        headers=request_headers,
                        timeout=timeout
                    )
            
            return response
            
        except requests.RequestException as e:
            logger.error(f"Ошибка выполнения запроса {method} {url}: {e}")
            raise
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 15
    ) -> requests.Response:
        """Выполнение GET запроса."""
        return self._make_request('GET', endpoint, params=params, headers=headers, timeout=timeout)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 15
    ) -> requests.Response:
        """Выполнение POST запроса."""
        return self._make_request('POST', endpoint, data=data, headers=headers, timeout=timeout)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 15
    ) -> requests.Response:
        """Выполнение PUT запроса."""
        return self._make_request('PUT', endpoint, data=data, headers=headers, timeout=timeout)
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict] = None,
        timeout: int = 15
    ) -> requests.Response:
        """Выполнение DELETE запроса."""
        return self._make_request('DELETE', endpoint, headers=headers, timeout=timeout)
    
    def close(self) -> None:
        """Закрытие сессии и освобождение ресурсов."""
        self.session.close()
        logger.info("API клиент закрыт")


class APIResponse:
    """
    Типизированный ответ API.
    
    Упрощает работу с ответами API, предоставляя удобные методы
    для проверки статуса и извлечения данных.
    """
    
    def __init__(self, response: requests.Response):
        """
        Инициализация ответа.
        
        Args:
            response: Ответ requests
        """
        self.response = response
        self.status_code = response.status_code
        self.headers = response.headers
        self.text = response.text
        
        # Попытка парсинга JSON
        self._json_data = None
        self._json_parsed = False
        
    @property
    def json(self) -> Optional[Dict]:
        """Получение JSON данных из ответа."""
        if not self._json_parsed:
            try:
                self._json_data = self.response.json()
            except Exception:
                self._json_data = None
            self._json_parsed = True
        return self._json_data
    
    @property
    def success(self) -> bool:
        """Проверка успешности запроса."""
        return 200 <= self.status_code < 300
    
    @property
    def is_json(self) -> bool:
        """Проверка является ли ответ JSON."""
        content_type = self.headers.get('content-type', '')
        return 'application/json' in content_type.lower()
    
    def require_success(self) -> 'APIResponse':
        """
        Проверка успешности запроса с выбросом исключения при ошибке.
        
        Returns:
            APIResponse: Текущий объект для chaining
            
        Raises:
            requests.HTTPError: При неуспешном статусе
        """
        if not self.success:
            raise requests.HTTPError(
                f"HTTP {self.status_code}: {self.text[:200]}",
                response=self.response
            )
        return self
    
    def require_json(self) -> 'APIResponse':
        """
        Проверка что ответ является JSON с выбросом исключения при ошибке.
        
        Returns:
            APIResponse: Текущий объект для chaining
            
        Raises:
            ValueError: Если ответ не является JSON
        """
        if not self.is_json:
            raise ValueError(f"Ответ не является JSON: {self.headers.get('content-type')}")
        return self
    
    def get_json_field(self, field: str, default: Any = None) -> Any:
        """
        Получение поля из JSON ответа.
        
        Args:
            field: Имя поля
            default: Значение по умолчанию
            
        Returns:
            Значение поля или default
        """
        if self.json and isinstance(self.json, dict):
            return self.json.get(field, default)
        return default
