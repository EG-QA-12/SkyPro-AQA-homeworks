"""Класс для работы с таблицей учителей в базе данных."""

import re
from typing import List, Tuple, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import allure

from config.db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


class TeacherTable:
    """
    Класс для работы с таблицей учителей в базе данных PostgreSQL.
    
    Предоставляет CRUD операции для управления записями учителей,
    а также методы валидации данных.
    """
    
    def __init__(self, connection_string: Optional[str] = None) -> None:
        """
        Инициализация подключения к базе данных.
        
        Args:
            connection_string (Optional[str]): Строка подключения к БД.
                Если не указана, используется конфигурация по умолчанию.
        """
        if not connection_string:
            connection_string = (
                f"postgresql://{DB_USER}:{DB_PASSWORD}@"
                f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
            )
        self.__engine = create_engine(connection_string)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()

    @staticmethod
    @allure.step("Валидация email: {email}")
    def validate_email(email: str) -> None:
        """
        Проверить корректность email адреса.
        
        Args:
            email (str): Email для проверки
            
        Raises:
            ValueError: если email некорректный
        """
        if email is None:
            raise ValueError("Email не может быть None")
            
        if len(email) > 254:
            raise ValueError("Длина email не может превышать 254 символа")
            
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Некорректный формат email")

    @staticmethod
    @allure.step("Валидация ID группы: {group_id}")
    def validate_group_id(group_id: int) -> None:
        """
        Проверить корректность ID группы.
        
        Args:
            group_id (int): ID группы для проверки
            
        Raises:
            ValueError: если group_id некорректный
        """
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValueError("group_id должен быть положительным числом")
    
    @allure.step("Получить всех учителей")
    def get_teacher(self) -> List[Tuple]:
        """
        Получить список всех учителей из базы данных.
        
        Returns:
            List[Tuple]: Список кортежей с данными учителей
        """
        result = self.__session.execute(text("SELECT * FROM teacher"))
        return result.fetchall()
    
    @allure.step("Добавить учителя: ID={teacher_id}, email={email}, group={group_id}")
    def add_teacher(self, teacher_id: int, email: str, group_id: int) -> None:
        """
        Добавить нового учителя в базу данных.
        
        Args:
            teacher_id (int): ID учителя
            email (str): Email учителя
            group_id (int): ID группы
            
        Raises:
            ValueError: если параметры некорректны
        """
        if not teacher_id or teacher_id <= 0:
            raise ValueError("teacher_id должен быть положительным числом")
        
        self.validate_email(email)
        self.validate_group_id(group_id)
            
        query = text(
            "INSERT INTO teacher(teacher_id, email, group_id) "
            "VALUES (:teacher_id, :email, :group_id)"
        )
        try:
            self.__session.execute(
                query,
                {
                    'teacher_id': teacher_id,
                    'email': email,
                    'group_id': group_id
                }
            )
            self.__session.commit()
        except Exception:
            self.__session.rollback()
            raise

    @allure.step("Обновить email учителя: ID={teacher_id}, new_email={new_email}")
    def update_teacher(self, teacher_id: int, new_email: str) -> None:
        """
        Обновить email учителя по ID.
        
        Args:
            teacher_id (int): ID учителя для обновления
            new_email (str): Новый email
            
        Raises:
            ValueError: если параметры некорректны или учитель не найден
        """
        if not teacher_id or teacher_id <= 0:
            raise ValueError("teacher_id должен быть положительным числом")
            
        self.validate_email(new_email)
        
        query = text(
            "UPDATE teacher SET email = :new_email "
            "WHERE teacher_id = :teacher_id"
        )
        try:
            result = self.__session.execute(
                query,
                {
                    'teacher_id': teacher_id,
                    'new_email': new_email
                }
            )
            self.__session.commit()
            if result.rowcount == 0:
                raise ValueError(f"Учитель с ID {teacher_id} не найден")
        except Exception:
            self.__session.rollback()
            raise

    @allure.step("Удалить учителя: ID={teacher_id}")
    def delete(self, teacher_id: int) -> None:
        """
        Удалить учителя по ID.
        
        Args:
            teacher_id (int): ID учителя для удаления
            
        Raises:
            ValueError: если teacher_id некорректный или учитель не найден
        """
        if not teacher_id or teacher_id <= 0:
            raise ValueError("teacher_id должен быть положительным числом")
            
        query = text("DELETE FROM teacher WHERE teacher_id = :teacher_id")
        try:
            result = self.__session.execute(query, {'teacher_id': teacher_id})
            self.__session.commit()
            if result.rowcount == 0:
                raise ValueError(f"Учитель с ID {teacher_id} не найден")
        except Exception:
            self.__session.rollback()
            raise
    
    @allure.step("Проверить существование учителя: ID={teacher_id}")
    def teacher_exists(self, teacher_id: int) -> bool:
        """
        Проверить существование учителя по ID.
        
        Args:
            teacher_id (int): ID учителя для проверки
            
        Returns:
            bool: True если учитель существует, иначе False
        """
        query = text("SELECT COUNT(*) FROM teacher WHERE teacher_id = :teacher_id")
        result = self.__session.execute(query, {'teacher_id': teacher_id})
        count = result.scalar()
        return count > 0
    
    def __del__(self) -> None:
        """
        Закрыть сессию при удалении объекта.
        """
        if hasattr(self, '_TeacherTable__session'):
            self.__session.close()
