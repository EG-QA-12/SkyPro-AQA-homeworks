#!/usr/bin/env python3
"""
API-клиент для работы с вопросами на сайте expert.bll.by

Следует принципу слоев абстракции - инкапсулирует детали работы с API
в строго типизированный клиент.
"""

import requests
from typing import Dict, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class QuestionSubmissionRequest:
    """Модель данных для отправки вопроса"""
    text: str
    session_cookie: str
    
    def validate(self) -> bool:
        """Валидация данных запроса"""
        if not self.text or len(self.text.strip()) < 10:
            logger.error("Текст вопроса должен содержать минимум 10 символов")
            return False
        if not self.session_cookie:
            logger.error("Сессионная кука обязательна")
            return False
        return True


@dataclass
class QuestionSubmissionResponse:
    """Модель данных ответа сервера"""
    success: bool
    question_id: Optional[str] = None
    error_message: Optional[str] = None
    status_code: int = 0


class QuestionAPIClient:
    """
    API-клиент для работы с вопросами
    
    Инкапсулирует детали работы с API вопросов, предоставляя
    простой и понятный интерфейс для тестов.
    """
    
    def __init__(self, base_url: str = "https://expert.bll.by"):
        """
        Инициализация клиента
        
        Args:
            base_url: Базовый URL API
        """
        self.base_url = base_url
        self.session = requests.Session()
        
        # Настройка заголовков по умолчанию
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'{base_url}/',
            'Origin': base_url
        })
    
    def submit_question(self, request: QuestionSubmissionRequest) -> QuestionSubmissionResponse:
        """
        Отправка вопроса на сервер
        
        Args:
            request: Данные для отправки вопроса
            
        Returns:
            QuestionSubmissionResponse: Результат отправки
            
        Raises:
            ValueError: При невалидных данных запроса
            requests.RequestException: При ошибках сети
        """
        # Валидация входных данных
        if not request.validate():
            raise ValueError("Невалидные данные запроса")
        
        # Настройка куки для запроса
        self.session.cookies.set("test_joint_session", request.session_cookie)
        
        try:
            # Отправка запроса
            response = self.session.post(
                f"{self.base_url}/questions?allow-session=2",
                data={"P": request.text}
            )
            
            # Обработка ответа
            return self._parse_response(response)
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при отправке вопроса: {e}")
            return QuestionSubmissionResponse(
                success=False,
                error_message=str(e),
                status_code=0
            )
    
    def _parse_response(self, response: requests.Response) -> QuestionSubmissionResponse:
        """
        Парсинг ответа сервера
        
        Args:
            response: Ответ от сервера
            
        Returns:
            QuestionSubmissionResponse: Структурированный ответ
        """
        try:
            # Проверяем статус код
            if response.status_code == 200:
                # Успешный ответ
                data = response.json()
                return QuestionSubmissionResponse(
                    success=data.get("success", False),
                    question_id=data.get("question_id"),
                    status_code=response.status_code
                )
            else:
                # Ошибка сервера
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                return QuestionSubmissionResponse(
                    success=False,
                    error_message=error_data.get("message", f"HTTP {response.status_code}"),
                    status_code=response.status_code
                )
                
        except Exception as e:
            logger.error(f"Ошибка при парсинге ответа: {e}")
            return QuestionSubmissionResponse(
                success=False,
                error_message=f"Ошибка парсинга: {e}",
                status_code=response.status_code
            ) 