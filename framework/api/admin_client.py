"""
Административный API клиент для работы с панелью модерации.

Этот клиент предоставляет удобный интерфейс для работы с административными
функциями сайта, включая публикацию вопросов и ответов, работу с панелью модерации.
"""

import logging
from typing import Dict, Optional, List, Any, Union
from framework.api.base_client import BaseAPIClient, APIResponse
from framework.utils.html_parser import ModerationPanelParser
from framework.utils.enums import AnswerPublicationType

logger = logging.getLogger(__name__)


class AdminAPIClient(BaseAPIClient):
    """
    Административный API клиент для работы с панелью модерации.
    
    Предоставляет удобные методы для:
    - Работы с панелью модерации
    - Публикации вопросов и ответов
    - Взятия записей в работу
    - Поиска записей по различным критериям
    """
    
    def __init__(self, role: str = "admin"):
        """
        Инициализация административного клиента.
        
        Args:
            role: Роль пользователя (по умолчанию "admin")
        """
        super().__init__(base_url="https://expert.bll.by", role=role)
        self.parser = ModerationPanelParser()
    
    def get_moderation_panel_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Получение данных из панели модерации.
        
        Args:
            limit: Максимальное количество записей
            
        Returns:
            List[Dict]: Список записей из панели модерации
        """
        session_cookie = self.session.cookies.get("test_joint_session")
        if not session_cookie:
            raise ValueError("Отсутствует сессионная кука")
        
        entries = self.parser.get_moderation_panel_data(session_cookie, limit=limit)
        logger.info(f"Получено {len(entries)} записей из панели модерации")
        return entries
    
    def find_question(
        self,
        mode: str = "latest",
        marker: Optional[str] = None,
        user: Optional[str] = None,
        limit: int = 100
    ) -> Optional[Dict[str, Any]]:
        """
        Поиск вопроса по различным критериям.
        
        Args:
            mode: Режим поиска ("latest", "by_marker", "by_user")
            marker: Фрагмент текста для поиска (для by_marker)
            user: Имя пользователя (для by_user)
            limit: Лимит записей для поиска
            
        Returns:
            Optional[Dict]: Найденный вопрос или None
        """
        entries = self.get_moderation_panel_data(limit=limit)
        
        # Фильтруем только вопросы (тип '?')
        questions = [e for e in entries if e.get('type') == '?']
        
        if not questions:
            logger.warning("Не найдено вопросов для публикации")
            return None
        
        # Выбор по маркеру
        if mode == "by_marker" and marker:
            marker_lower = marker.lower()
            for q in questions:
                if 'text' in q and marker_lower in q['text'].lower():
                    return q
            logger.warning(f"Не найден вопрос с маркером: {marker}")
            return None
        
        # Выбор по пользователю
        if mode == "by_user" and user:
            user_lower = user.lower()
            for q in questions:
                if 'user' in q and user_lower in q['user'].lower():
                    return q
            logger.warning(f"Не найден вопрос от пользователя: {user}")
            return None
        
        # Выбор самого свежего вопроса
        if questions:
            sorted_questions = sorted(
                questions,
                key=lambda x: (x.get('timestamp', 0), int(x.get('id', 0)) if x.get('id') and x.get('id').isdigit() else 0),
                reverse=True
            )
            return sorted_questions[0] if sorted_questions else None
        
        return None
    
    def find_answer(
        self,
        mode: str = "latest",
        marker: Optional[str] = None,
        user: Optional[str] = None,
        limit: int = 100
    ) -> Optional[Dict[str, Any]]:
        """
        Поиск ответа по различным критериям.
        
        Args:
            mode: Режим поиска ("latest", "by_marker", "by_user")
            marker: Фрагмент текста для поиска (для by_marker)
            user: Имя пользователя (для by_user)
            limit: Лимит записей для поиска
            
        Returns:
            Optional[Dict]: Найденный ответ или None
        """
        entries = self.get_moderation_panel_data(limit=limit)
        
        # Фильтруем только ответы (тип 'П')
        answers = [e for e in entries if e.get('type') == 'П']
        
        if not answers:
            logger.warning("Не найдено ответов для публикации")
            return None
        
        # Выбор по маркеру
        if mode == "by_marker" and marker:
            marker_lower = marker.lower()
            for a in answers:
                if 'text' in a and marker_lower in a['text'].lower():
                    return a
            logger.warning(f"Не найден ответ с маркером: {marker}")
            return None
        
        # Выбор по пользователю
        if mode == "by_user" and user:
            user_lower = user.lower()
            for a in answers:
                if 'user' in a and user_lower in a['user'].lower():
                    return a
            logger.warning(f"Не найден ответ от пользователя: {user}")
            return None
        
        # Выбор самого свежего ответа
        if answers:
            sorted_answers = sorted(
                answers,
                key=lambda x: (x.get('timestamp', 0), int(x.get('id', 0)) if x.get('id') and x.get('id').isdigit() else 0),
                reverse=True
            )
            return sorted_answers[0] if sorted_answers else None
        
        return None
    
    def publish_question(
        self,
        question_id: Union[str, int],
        status_id: int = 3,
        post_type_id: int = 1,
        **kwargs
    ) -> APIResponse:
        """
        Публикация вопроса через админ-панель.
        
        Args:
            question_id: ID вопроса
            status_id: ID статуса (по умолчанию 3 - опубликован)
            post_type_id: ID типа поста (по умолчанию 1)
            **kwargs: Дополнительные параметры
            
        Returns:
            APIResponse: Ответ API
        """
        # Получаем CSRF токены
        tokens = self._get_csrf_tokens()
        
        # Формируем данные для запроса
        data = {
            'id': str(question_id),
            'post_type_id': str(post_type_id),
            'status_id': str(status_id),
            'answered': '0',
            'rejection_reason_id': '0',
            'moder_msg': '',
            'delete_reason': '0',
            'hand_over_moderator': '',
        }
        
        # Добавляем sub_theme_id (1-65)
        for i in range(1, 66):
            data[f'sub_theme_id[]'] = str(i)
        
        # Добавляем CSRF токен если есть
        if tokens.get('form_token'):
            data['_token'] = tokens['form_token']
        
        # Добавляем дополнительные параметры
        data.update(kwargs)
        
        # Устанавливаем заголовки
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'{self.base_url}/admin/posts/new',
        }
        
        if tokens.get('xsrf_token'):
            headers['X-XSRF-TOKEN'] = tokens['xsrf_token']
        if tokens.get('form_token'):
            headers['X-CSRF-TOKEN'] = tokens['form_token']
        
        # Выполняем запрос
        response = self.post(
            '/admin/posts/update',
            data=data,
            headers=headers
        )
        
        logger.info(f"Публикация вопроса {question_id}: статус {response.status_code}")
        return APIResponse(response)
    
    def publish_answer(
        self,
        answer_id: Union[str, int],
        publication_type: AnswerPublicationType,
        **kwargs
    ) -> APIResponse:
        """
        Публикация ответа через админ-панель.
        
        Args:
            answer_id: ID ответа
            publication_type: Тип публикации (AnswerPublicationType)
            **kwargs: Дополнительные параметры
            
        Returns:
            APIResponse: Ответ API
        """
        # Получаем CSRF токены
        tokens = self._get_csrf_tokens()
        
        # Формируем данные для запроса
        data = {
            'id': str(answer_id),
            'status_id': str(publication_type.value),
            'rejection_reason_id': '0',
            'moder_msg': '',
            'delete_reason': '0',
        }
        
        # Добавляем CSRF токен если есть
        if tokens.get('form_token'):
            data['_token'] = tokens['form_token']
        
        # Добавляем дополнительные параметры
        data.update(kwargs)
        
        # Устанавливаем заголовки
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'{self.base_url}/admin/posts/new',
        }
        
        if tokens.get('xsrf_token'):
            headers['X-XSRF-TOKEN'] = tokens['xsrf_token']
        if tokens.get('form_token'):
            headers['X-CSRF-TOKEN'] = tokens['form_token']
        
        # Выполняем запрос
        response = self.post(
            '/admin/posts/update',
            data=data,
            headers=headers
        )
        
        logger.info(f"Публикация ответа {answer_id}: статус {response.status_code}")
        return APIResponse(response)
    
    def assign_entry(self, entry_id: Union[str, int]) -> APIResponse:
        """
        Взятие записи в работу.
        
        Args:
            entry_id: ID записи
            
        Returns:
            APIResponse: Ответ API
        """
        # Получаем CSRF токены
        tokens = self._get_csrf_tokens()
        
        # Формируем данные для запроса
        data = {
            'id': str(entry_id),
            'hand_over_moderator': self.role,  # или конкретное имя модератора
        }
        
        # Добавляем CSRF токен если есть
        if tokens.get('form_token'):
            data['_token'] = tokens['form_token']
        
        # Устанавливаем заголовки
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'{self.base_url}/admin/posts/new',
        }
        
        if tokens.get('xsrf_token'):
            headers['X-XSRF-TOKEN'] = tokens['xsrf_token']
        if tokens.get('form_token'):
            headers['X-CSRF-TOKEN'] = tokens['form_token']
        
        # Выполняем запрос
        response = self.post(
            '/admin/posts/update',
            data=data,
            headers=headers
        )
        
        logger.info(f"Взятие записи {entry_id} в работу: статус {response.status_code}")
        return APIResponse(response)
    
    def search_questions(self, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Поиск вопросов в панели модерации.
        
        Args:
            query: Текст для поиска (опционально)
            limit: Максимальное количество записей
            
        Returns:
            List[Dict]: Список найденных вопросов
        """
        try:
            entries = self.get_moderation_panel_data(limit=limit)
            # Фильтруем только вопросы (тип '?')
            questions = [e for e in entries if e.get('type') == '?']
            
            if query:
                # Фильтруем по тексту запроса
                query_lower = query.lower()
                questions = [q for q in questions if query_lower in q.get('text', '').lower()]
            
            return questions
        except Exception as e:
            logger.error(f"Ошибка поиска вопросов: {e}")
            return []
    
    def assign_question(self, question_id: Union[str, int]) -> bool:
        """
        Взятие вопроса в работу.
        
        Args:
            question_id: ID вопроса
            
        Returns:
            bool: True если успешно взят в работу
        """
        try:
            response = self.assign_entry(question_id)
            return response.success if hasattr(response, 'success') else response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка взятия вопроса {question_id} в работу: {e}")
            return False
    
    def submit_question(
        self,
        question_text: str,
        allow_session: bool = True
    ) -> APIResponse:
        """
        Отправка вопроса через публичный endpoint.
        
        Args:
            question_text: Текст вопроса
            allow_session: Использовать allow-session параметр
            
        Returns:
            APIResponse: Ответ API
        """
        data = {'p': question_text}
        
        headers = {
            'Referer': f'{self.base_url}/',
            'Origin': self.base_url,
        }
        
        # Формируем URL с параметром allow-session если нужно
        endpoint = '/questions'
        if allow_session:
            endpoint += '?allow-session=2'
        
        response = self.post(endpoint, data=data, headers=headers)
        
        logger.info(f"Отправка вопроса: статус {response.status_code}")
        return APIResponse(response)
    
    def create_test_question(
        self,
        question_text: str,
        allow_session: bool = True
    ) -> bool:
        """
        Создание тестового вопроса через публичный endpoint.
        
        Args:
            question_text: Текст вопроса
            allow_session: Использовать allow-session параметр
            
        Returns:
            bool: True если вопрос успешно создан
        """
        try:
            data = {'p': question_text}
            
            headers = {
                'Referer': f'{self.base_url}/',
                'Origin': self.base_url,
            }
            
            # Формируем URL с параметром allow-session если нужно
            endpoint = '/questions'
            if allow_session:
                endpoint += '?allow-session=2'
            
            response = self.post(endpoint, data=data, headers=headers)
            
            logger.info(f"Создание тестового вопроса: статус {response.status_code}")
            # Проверяем успешность по статусу
            return response.status_code in [200, 201, 302]
        except Exception as e:
            logger.error(f"Ошибка создания тестового вопроса: {e}")
            return False
    
    def answer_question(
        self,
        question_id: Union[str, int],
        answer_text: str,
        publication_type: AnswerPublicationType = AnswerPublicationType.ANSWER,
        allow_session: bool = True
    ) -> bool:
        """
        Ответ на вопрос через админ-панель.
        
        Args:
            question_id: ID вопроса
            answer_text: Текст ответа
            publication_type: Тип публикации ответа
            allow_session: Использовать allow-session параметр
            
        Returns:
            bool: True если ответ успешно отправлен
        """
        try:
            # Получаем CSRF токены
            tokens = self._get_csrf_tokens()
            
            # Формируем данные для запроса
            data = {
                'id': str(question_id),
                'status_id': str(publication_type.value),
                'rejection_reason_id': '0',
                'moder_msg': answer_text,  # Текст ответа в moder_msg
                'delete_reason': '0',
            }
            
            # Добавляем CSRF токен если есть
            if tokens.get('form_token'):
                data['_token'] = tokens['form_token']
            
            # Устанавливаем заголовки
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': f'{self.base_url}/admin/posts/new',
            }
            
            if tokens.get('xsrf_token'):
                headers['X-XSRF-TOKEN'] = tokens['xsrf_token']
            if tokens.get('form_token'):
                headers['X-CSRF-TOKEN'] = tokens['form_token']
            
            # Выполняем запрос
            response = self.post(
                '/admin/posts/update',
                data=data,
                headers=headers
            )
            
            logger.info(f"Ответ на вопрос {question_id}: статус {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка ответа на вопрос {question_id}: {e}")
            return False
    
    def submit_answer(
        self,
        question_id: Union[str, int],
        answer_text: str,
        allow_session: bool = True
    ) -> APIResponse:
        """
        Отправка ответа на вопрос.
        
        Args:
            question_id: ID вопроса
            answer_text: Текст ответа
            allow_session: Использовать allow-session параметр
            
        Returns:
            APIResponse: Ответ API
        """
        data = {'p': answer_text}
        
        headers = {
            'Referer': f'{self.base_url}/questions/{question_id}',
            'Origin': self.base_url,
        }
        
        # Формируем URL с параметром allow-session если нужно
        endpoint = f'/questions/answers/{question_id}'
        if allow_session:
            endpoint += '?allow-session=2'
        
        response = self.post(endpoint, data=data, headers=headers)
        
        logger.info(f"Отправка ответа на вопрос {question_id}: статус {response.status_code}")
        return APIResponse(response)


# Удобные функции для часто используемых операций

def publish_latest_question(client: AdminAPIClient) -> APIResponse:
    """
    Публикация самого свежего вопроса.
    
    Args:
        client: Административный клиент
        
    Returns:
        APIResponse: Результат публикации
        
    Raises:
        ValueError: Если не найден вопрос для публикации
    """
    question = client.find_question(mode="latest")
    if not question:
        raise ValueError("Не найден вопрос для публикации")
    
    return client.publish_question(question['id'])


def publish_latest_answer(
    client: AdminAPIClient,
    publication_type: AnswerPublicationType = AnswerPublicationType.ANSWER
) -> APIResponse:
    """
    Публикация самого свежего ответа.
    
    Args:
        client: Административный клиент
        publication_type: Тип публикации
        
    Returns:
        APIResponse: Результат публикации
        
    Raises:
        ValueError: Если не найден ответ для публикации
    """
    answer = client.find_answer(mode="latest")
    if not answer:
        raise ValueError("Не найден ответ для публикации")
    
    return client.publish_answer(answer['id'], publication_type)
