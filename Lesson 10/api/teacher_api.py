"""API клиент для работы с учителями."""

from typing import Dict, Any, List, Optional
import allure

from .base_client import BaseAPIClient


class TeacherAPI(BaseAPIClient):
    """
    API клиент для работы с учителями через REST API.
    
    Предоставляет методы для CRUD операций с учителями,
    а также дополнительные методы для работы с данными.
    """
    
    def __init__(self, base_url: str = "http://localhost:8080/api/v1") -> None:
        """
        Инициализация API клиента для учителей.
        
        Args:
            base_url (str): Базовый URL API учителей
        """
        super().__init__(base_url)
    
    @allure.step("Получить всех учителей")
    def get_all_teachers(self) -> List[Dict[str, Any]]:
        """
        Получить список всех учителей.
        
        Returns:
            List[Dict[str, Any]]: Список словарей с данными учителей
        """
        response = self.get("teachers")
        return response.json()
    
    @allure.step("Получить учителя по ID: {teacher_id}")
    def get_teacher_by_id(self, teacher_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить данные учителя по ID.
        
        Args:
            teacher_id (int): ID учителя
            
        Returns:
            Optional[Dict[str, Any]]: Данные учителя или None если не найден
        """
        try:
            response = self.get(f"teachers/{teacher_id}")
            return response.json()
        except Exception:
            return None
    
    @allure.step("Создать учителя")
    def create_teacher(self, teacher_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создать нового учителя.
        
        Args:
            teacher_data (Dict[str, Any]): Данные нового учителя
            
        Returns:
            Dict[str, Any]: Данные созданного учителя
        """
        response = self.post("teachers", data=teacher_data)
        return response.json()
    
    @allure.step("Обновить учителя: ID={teacher_id}")
    def update_teacher(self, teacher_id: int, teacher_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновить данные учителя.
        
        Args:
            teacher_id (int): ID учителя для обновления
            teacher_data (Dict[str, Any]): Новые данные учителя
            
        Returns:
            Dict[str, Any]: Обновленные данные учителя
        """
        response = self.put(f"teachers/{teacher_id}", data=teacher_data)
        return response.json()
    
    @allure.step("Обновить email учителя: ID={teacher_id}, new_email={new_email}")
    def update_teacher_email(self, teacher_id: int, new_email: str) -> Dict[str, Any]:
        """
        Обновить email учителя.
        
        Args:
            teacher_id (int): ID учителя для обновления
            new_email (str): Новый email
            
        Returns:
            Dict[str, Any]: Обновленные данные учителя
        """
        return self.update_teacher(teacher_id, {"email": new_email})
    
    @allure.step("Удалить учителя: ID={teacher_id}")
    def delete_teacher(self, teacher_id: int) -> bool:
        """
        Удалить учителя по ID.
        
        Args:
            teacher_id (int): ID учителя для удаления
            
        Returns:
            bool: True если удален успешно
        """
        try:
            self.delete(f"teachers/{teacher_id}")
            return True
        except Exception:
            return False
    
    @allure.step("Проверить существование учителя: ID={teacher_id}")
    def teacher_exists(self, teacher_id: int) -> bool:
        """
        Проверить существование учителя по ID.
        
        Args:
            teacher_id (int): ID учителя для проверки
            
        Returns:
            bool: True если учитель существует
        """
        teacher = self.get_teacher_by_id(teacher_id)
        return teacher is not None
    
    @allure.step("Получить учителей по группе: {group_id}")
    def get_teachers_by_group(self, group_id: int) -> List[Dict[str, Any]]:
        """
        Получить список учителей по ID группы.
        
        Args:
            group_id (int): ID группы
            
        Returns:
            List[Dict[str, Any]]: Список учителей группы
        """
        response = self.get("teachers", params={"group_id": group_id})
        return response.json()
    
    @allure.step("Поиск учителей по email: {email}")
    def search_teachers_by_email(self, email: str) -> List[Dict[str, Any]]:
        """
        Поиск учителей по email.
        
        Args:
            email (str): Email для поиска
            
        Returns:
            List[Dict[str, Any]]: Список найденных учителей
        """
        response = self.get("teachers", params={"email": email})
        return response.json()
