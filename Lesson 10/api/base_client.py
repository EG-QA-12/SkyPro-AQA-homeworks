"""Базовый класс для API клиентов."""

from typing import Dict, Any, Optional
import requests
import allure


class BaseAPIClient:
    """
    Базовый класс для всех API клиентов.
    
    Предоставляет общие методы для выполнения HTTP запросов,
    обработки ответов и управления сессиями.
    """
    
    def __init__(self, base_url: str, timeout: int = 30) -> None:
        """
        Инициализация базового API клиента.
        
        Args:
            base_url (str): Базовый URL API
            timeout (int): Таймаут запросов в секундах
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = timeout
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    @allure.step("Выполнить GET запрос: {endpoint}")
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Выполнить GET запрос к API.
        
        Args:
            endpoint (str): Эндпоинт для запроса
            params (Optional[Dict[str, Any]]): Параметры запроса
            
        Returns:
            requests.Response: Ответ сервера
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response
    
    @allure.step("Выполнить POST запрос: {endpoint}")
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Выполнить POST запрос к API.
        
        Args:
            endpoint (str): Эндпоинт для запроса
            data (Optional[Dict[str, Any]]): Данные для отправки
            
        Returns:
            requests.Response: Ответ сервера
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response
    
    @allure.step("Выполнить PUT запрос: {endpoint}")
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Выполнить PUT запрос к API.
        
        Args:
            endpoint (str): Эндпоинт для запроса
            data (Optional[Dict[str, Any]]): Данные для обновления
            
        Returns:
            requests.Response: Ответ сервера
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.put(url, json=data)
        response.raise_for_status()
        return response
    
    @allure.step("Выполнить DELETE запрос: {endpoint}")
    def delete(self, endpoint: str) -> requests.Response:
        """
        Выполнить DELETE запрос к API.
        
        Args:
            endpoint (str): Эндпоинт для запроса
            
        Returns:
            requests.Response: Ответ сервера
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response
    
    @allure.step("Установить токен авторизации")
    def set_auth_token(self, token: str) -> None:
        """
        Установить токен авторизации для запросов.
        
        Args:
            token (str): JWT токен или другой токен авторизации
        """
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    @allure.step("Очистить токен авторизации")
    def clear_auth_token(self) -> None:
        """
        Удалить токен авторизации из заголовков.
        """
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def _build_url(self, endpoint: str) -> str:
        """
        Построить полный URL из базового URL и эндпоинта.
        
        Args:
            endpoint (str): Эндпоинт
            
        Returns:
            str: Полный URL
        """
        return f"{self.base_url}/{endpoint.lstrip('/')}"
