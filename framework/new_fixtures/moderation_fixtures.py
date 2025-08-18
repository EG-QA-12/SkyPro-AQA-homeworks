"""
Фикстуры для работы с панелью модерации.

Этот модуль предоставляет удобные фикстуры для тестирования
функциональности панели модерации и работы с вопросами/ответами.
"""

import pytest
import logging
from typing import Dict, List, Optional, Any
from framework.api.admin_client import AdminAPIClient
from framework.utils.question_factory import QuestionFactory
from framework.utils.enums import AnswerPublicationType

logger = logging.getLogger(__name__)


@pytest.fixture
def question_factory() -> QuestionFactory:
    """
    Фикстура для получения фабрики вопросов.
    
    Returns:
        QuestionFactory: Фабрика для генерации тестовых вопросов
    """
    return QuestionFactory()


@pytest.fixture
def moderation_helper(admin_client: AdminAPIClient) -> 'ModerationTestHelper':
    """
    Фикстура для получения помощника тестов модерации.
    
    Args:
        admin_client: Административный клиент
        
    Returns:
        ModerationTestHelper: Помощник тестов модерации
    """
    return ModerationTestHelper(admin_client)


class ModerationTestHelper:
    """
    Вспомогательный класс для тестов модерации.
    
    Предоставляет удобные методы для работы с панелью модерации,
    поиска записей и выполнения типичных операций.
    """
    
    def __init__(self, client: AdminAPIClient):
        """
        Инициализация помощника.
        
        Args:
            client: Административный клиент
        """
        self.client = client
    
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
    
    def find_question_by_marker(self, marker: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        Поиск вопроса по маркеру.
        
        Args:
            marker: Фрагмент текста для поиска
            limit: Лимит записей для поиска
            
        Returns:
            Optional[Dict]: Найденный вопрос или None
        """
        return self.client.find_question(mode="by_marker", marker=marker, limit=limit)
    
    def find_answer_by_marker(self, marker: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        Поиск ответа по маркеру.
        
        Args:
            marker: Фрагмент текста для поиска
            limit: Лимит записей для поиска
            
        Returns:
            Optional[Dict]: Найденный ответ или None
        """
        return self.client.find_answer(mode="by_marker", marker=marker, limit=limit)
    
    def find_question_by_user(self, user: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        Поиск вопроса по пользователю.
        
        Args:
            user: Имя пользователя
            limit: Лимит записей для поиска
            
        Returns:
            Optional[Dict]: Найденный вопрос или None
        """
        return self.client.find_question(mode="by_user", user=user, limit=limit)
    
    def find_answer_by_user(self, user: str, limit: int = 100) -> Optional[Dict[str, Any]]:
        """
        Поиск ответа по пользователю.
        
        Args:
            user: Имя пользователя
            limit: Лимит записей для поиска
            
        Returns:
            Optional[Dict]: Найденный ответ или None
        """
        return self.client.find_answer(mode="by_user", user=user, limit=limit)
    
    def get_panel_entries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Получение записей из панели модерации.
        
        Args:
            limit: Максимальное количество записей
            
        Returns:
            List[Dict]: Список записей
        """
        return self.client.get_moderation_panel_data(limit=limit)
    
    def publish_question(
        self,
        question_id: str,
        status_id: int = 3,
        post_type_id: int = 1
    ) -> bool:
        """
        Публикация вопроса.
        
        Args:
            question_id: ID вопроса
            status_id: ID статуса
            post_type_id: ID типа поста
            
        Returns:
            bool: True если успешно опубликован
        """
        try:
            response = self.client.publish_question(
                question_id=question_id,
                status_id=status_id,
                post_type_id=post_type_id
            )
            return response.success and response.get_json_field('success', False)
        except Exception as e:
            logger.error(f"Ошибка публикации вопроса {question_id}: {e}")
            return False
    
    def publish_answer(
        self,
        answer_id: str,
        publication_type: AnswerPublicationType = AnswerPublicationType.ANSWER
    ) -> bool:
        """
        Публикация ответа.
        
        Args:
            answer_id: ID ответа
            publication_type: Тип публикации
            
        Returns:
            bool: True если успешно опубликован
        """
        try:
            response = self.client.publish_answer(
                answer_id=answer_id,
                publication_type=publication_type
            )
            return response.success and response.get_json_field('success', False)
        except Exception as e:
            logger.error(f"Ошибка публикации ответа {answer_id}: {e}")
            return False
    
    def assign_entry(self, entry_id: str) -> bool:
        """
        Взятие записи в работу.
        
        Args:
            entry_id: ID записи
            
        Returns:
            bool: True если успешно взята в работу
        """
        try:
            response = self.client.assign_entry(entry_id)
            return response.success
        except Exception as e:
            logger.error(f"Ошибка взятия записи {entry_id} в работу: {e}")
            return False
    
    def submit_test_question(self, question_text: str) -> Optional[str]:
        """
        Отправка тестового вопроса.
        
        Args:
            question_text: Текст вопроса
            
        Returns:
            Optional[str]: ID вопроса или None при ошибке
        """
        try:
            response = self.client.submit_question(question_text)
            if response.success:
                # Здесь можно добавить логику извлечения ID из ответа
                return "temp_question_id"  # Заглушка
            return None
        except Exception as e:
            logger.error(f"Ошибка отправки вопроса: {e}")
            return None
    
    def submit_test_answer(self, question_id: str, answer_text: str) -> bool:
        """
        Отправка тестового ответа.
        
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
            logger.error(f"Ошибка отправки ответа на вопрос {question_id}: {e}")
            return False


# Удобные фикстуры для часто используемых сценариев

@pytest.fixture
def fresh_question(moderation_helper: ModerationTestHelper) -> Dict[str, Any]:
    """
    Фикстура для получения свежего вопроса из панели модерации.
    
    Args:
        moderation_helper: Помощник тестов модерации
        
    Returns:
        Dict[str, Any]: Свежий вопрос
        
    Raises:
        pytest.fail: Если не найден вопрос
    """
    question = moderation_helper.get_latest_question()
    if not question:
        pytest.fail("Не найден свежий вопрос в панели модерации")
    return question


@pytest.fixture
def fresh_answer(moderation_helper: ModerationTestHelper) -> Dict[str, Any]:
    """
    Фикстура для получения свежего ответа из панели модерации.
    
    Args:
        moderation_helper: Помощник тестов модерации
        
    Returns:
        Dict[str, Any]: Свежий ответ
        
    Raises:
        pytest.fail: Если не найден ответ
    """
    answer = moderation_helper.get_latest_answer()
    if not answer:
        pytest.fail("Не найден свежий ответ в панели модерации")
    return answer


@pytest.fixture
def panel_entries(moderation_helper: ModerationTestHelper) -> List[Dict[str, Any]]:
    """
    Фикстура для получения записей из панели модерации.
    
    Args:
        moderation_helper: Помощник тестов модерации
        
    Returns:
        List[Dict[str, Any]]: Список записей
    """
    return moderation_helper.get_panel_entries()


# Параметризованные фикстуры для тестирования разных типов публикаций

@pytest.fixture(params=[
    AnswerPublicationType.PUBLISHED,
    AnswerPublicationType.DRAFT,
    AnswerPublicationType.REJECTED
])
def publication_type(request) -> AnswerPublicationType:
    """
    Параметризованная фикстура для тестирования разных типов публикаций.
    
    Args:
        request: Объект запроса pytest
        
    Returns:
        AnswerPublicationType: Тип публикации
    """
    return request.param
