"""
Базовый класс для API тестов.

Этот модуль предоставляет базовую инфраструктуру для написания
API тестов с использованием унифицированного фреймворка.
"""

import pytest
import logging
from typing import Optional, Dict, Any
from framework.api.admin_client import AdminAPIClient
from framework.utils.question_factory import QuestionFactory

logger = logging.getLogger(__name__)


class APITestBase:
    """
    Базовый класс для API тестов.
    
    Предоставляет общую инфраструктуру и вспомогательные методы
    для тестирования API функциональности.
    """
    
    # Классовые атрибуты для настройки тестов
    ROLE = "admin"
    BASE_URL = "https://expert.bll.by"
    
    def setup_method(self) -> None:
        """Настройка перед каждым тестовым методом."""
        self.client = AdminAPIClient(role=self.ROLE)
        self.admin_client = AdminAPIClient(role="admin")
        self.moder_client = AdminAPIClient(role="moderator")
        self.user_client = AdminAPIClient(role="user")
        self.question_factory = QuestionFactory()
        self.logger = logging.getLogger(self.__class__.__name__)
        logger.info(f"Инициализирован тестовый клиент для роли: {self.ROLE}")
    
    def teardown_method(self) -> None:
        """Очистка после каждого тестового метода."""
        clients_to_close = ['client', 'admin_client', 'moder_client', 'user_client']
        for client_name in clients_to_close:
            if hasattr(self, client_name):
                client = getattr(self, client_name)
                if client and hasattr(client, 'close'):
                    client.close()
        logger.info("Все тестовые клиенты закрыты")
    
    def generate_test_question(self, category: Optional[str] = None) -> str:
        """
        Генерация тестового вопроса.
        
        Args:
            category: Категория вопроса
            
        Returns:
            str: Сгенерированный вопрос
        """
        return self.question_factory.generate_question(category=category)
    
    def generate_multiple_questions(self, count: int = 5, category: Optional[str] = None) -> list:
        """
        Генерация нескольких тестовых вопросов.
        
        Args:
            count: Количество вопросов
            category: Категория вопросов
            
        Returns:
            list: Список сгенерированных вопросов
        """
        return self.question_factory.generate_multiple_questions(count=count, category=category)
    
    def assert_api_success(self, response, message: str = "API запрос не удался") -> None:
        """
        Проверка успешности API ответа.
        
        Args:
            response: Ответ API
            message: Сообщение об ошибке
            
        Raises:
            AssertionError: Если ответ не успешный
        """
        assert response.success, f"{message}: статус {response.status_code}, ответ: {response.text[:200]}"
    
    def assert_json_response(self, response, message: str = "Ответ не является JSON") -> None:
        """
        Проверка что ответ является JSON.
        
        Args:
            response: Ответ API
            message: Сообщение об ошибке
            
        Raises:
            AssertionError: Если ответ не JSON
        """
        assert response.is_json, f"{message}: content-type {response.headers.get('content-type')}"
    
    def assert_json_field(self, response, field: str, expected_value: Any, message: str = None) -> None:
        """
        Проверка значения поля в JSON ответе.
        
        Args:
            response: Ответ API
            field: Имя поля
            expected_value: Ожидаемое значение
            message: Сообщение об ошибке
            
        Raises:
            AssertionError: Если значение поля не совпадает
        """
        actual_value = response.get_json_field(field)
        if message is None:
            message = f"Поле '{field}' имеет значение '{actual_value}', ожидается '{expected_value}'"
        assert actual_value == expected_value, message
    
    def assert_json_field_exists(self, response, field: str, message: str = None) -> None:
        """
        Проверка существования поля в JSON ответе.
        
        Args:
            response: Ответ API
            field: Имя поля
            message: Сообщение об ошибке
            
        Raises:
            AssertionError: Если поле отсутствует
        """
        json_data = response.json
        if message is None:
            message = f"Поле '{field}' отсутствует в ответе"
        assert json_data is not None and field in json_data, message


class AdminAPITestBase(APITestBase):
    """
    Базовый класс для административных API тестов.
    
    Предоставляет специализированную инфраструктуру для тестирования
    административной функциональности.
    """
    
    ROLE = "admin"
    
    def setup_method(self) -> None:
        """Настройка перед каждым тестовым методом."""
        super().setup_method()
        logger.info("Инициализирован административный тестовый клиент")
    
    def get_latest_question(self, limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        Получение самого свежего вопроса.
        
        Args:
            limit: Лимит записей для поиска
            
        Returns:
            Optional[Dict]: Самый свежий вопрос или None
        """
        return self.client.find_question(mode="latest", limit=limit)
    
    def get_latest_answer(self, limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        Получение самого свежего ответа.
        
        Args:
            limit: Лимит записей для поиска
            
        Returns:
            Optional[Dict]: Самый свежий ответ или None
        """
        return self.client.find_answer(mode="latest", limit=limit)
    
    def publish_question(self, question_id: str, **kwargs) -> bool:
        """
        Публикация вопроса.
        
        Args:
            question_id: ID вопроса
            **kwargs: Дополнительные параметры
            
        Returns:
            bool: True если успешно опубликован
        """
        try:
            response = self.client.publish_question(question_id, **kwargs)
            return response.success and response.get_json_field('success', False)
        except Exception as e:
            logger.error(f"Ошибка публикации вопроса {question_id}: {e}")
            return False
    
    def publish_answer(self, answer_id: str, **kwargs) -> bool:
        """
        Публикация ответа.
        
        Args:
            answer_id: ID ответа
            **kwargs: Дополнительные параметры
            
        Returns:
            bool: True если успешно опубликован
        """
        try:
            response = self.client.publish_answer(answer_id, **kwargs)
            return response.success and response.get_json_field('success', False)
        except Exception as e:
            logger.error(f"Ошибка публикации ответа {answer_id}: {e}")
            return False


class UserAPITestBase(APITestBase):
    """
    Базовый класс для пользовательских API тестов.
    
    Предоставляет специализированную инфраструктуру для тестирования
    пользовательской функциональности.
    """
    
    ROLE = "user"
    
    def setup_method(self) -> None:
        """Настройка перед каждым тестовым методом."""
        super().setup_method()
        logger.info("Инициализирован пользовательский тестовый клиент")
    
    def submit_question(self, question_text: str) -> bool:
        """
        Отправка вопроса.
        
        Args:
            question_text: Текст вопроса
            
        Returns:
            bool: True если успешно отправлен
        """
        try:
            response = self.client.submit_question(question_text)
            return response.success
        except Exception as e:
            logger.error(f"Ошибка отправки вопроса: {e}")
            return False
    
    def submit_answer(self, question_id: str, answer_text: str) -> bool:
        """
        Отправка ответа.
        
        Args:
            question_id: ID вопроса
            answer_text: Текст ответа
            
        Returns:
            bool: True если успешно отправлен
        """
        try:
            response = self.client.submit_answer(question_id, answer_text)
            return response.success
        except Exception as e:
            logger.error(f"Ошибка отправки ответа: {e}")
            return False


# Удобные миксины для часто используемых функциональностей

class QuestionSubmissionMixin:
    """Миксин для тестов отправки вопросов."""
    
    def submit_and_verify_question(self, question_text: str) -> bool:
        """
        Отправка вопроса и проверка успешности.
        
        Args:
            question_text: Текст вопроса
            
        Returns:
            bool: True если успешно отправлен и проверен
        """
        if not hasattr(self, 'client'):
            raise AttributeError("Клиент не инициализирован")
        
        response = self.client.submit_question(question_text)
        return response.success


class AnswerSubmissionMixin:
    """Миксин для тестов отправки ответов."""
    
    def submit_and_verify_answer(self, question_id: str, answer_text: str) -> bool:
        """
        Отправка ответа и проверка успешности.
        
        Args:
            question_id: ID вопроса
            answer_text: Текст ответа
            
        Returns:
            bool: True если успешно отправлен и проверен
        """
        if not hasattr(self, 'client'):
            raise AttributeError("Клиент не инициализирован")
        
        response = self.client.submit_answer(question_id, answer_text)
        return response.success


class ModerationMixin:
    """Миксин для тестов модерации."""
    
    def verify_in_moderation_panel(self, text_fragment: str, entry_type: str = '?') -> bool:
        """
        Проверка наличия записи в панели модерации.
        
        Args:
            text_fragment: Фрагмент текста для поиска
            entry_type: Тип записи ('?' для вопросов, 'П' для ответов)
            
        Returns:
            bool: True если запись найдена
        """
        if not hasattr(self, 'client'):
            raise AttributeError("Клиент не инициализирован")
        
        entries = self.client.get_moderation_panel_data(limit=50)
        for entry in entries:
            if (entry.get('type') == entry_type and 
                text_fragment.lower() in entry.get('text', '').lower()):
                return True
        return False
