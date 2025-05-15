import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


class TeacherTable:
    """Класс для работы с таблицей учителей в базе данных."""

    def __init__(self, connection_string=None):
        """
        Инициализация подключения к базе данных.
        
        Args:
            connection_string (str, optional): Строка подключения к БД.
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
    def validate_email(email):
        """
        Проверка корректности email адреса.
        
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
    def validate_group_id(group_id):
        """
        Проверка корректности ID группы.
        
        Args:
            group_id (int): ID группы
            
        Raises:
            ValueError: если group_id некорректный
        """
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValueError("group_id должен быть положительным числом")
        
    def get_teacher(self):
        """
        Получить список всех учителей.
        
        Returns:
            list: Список кортежей с данными учителей
        """
        return self.__session.execute(text("SELECT * FROM teacher")).fetchall()

    def add_teacher(
            self,
            teacher_id,
            email,
            group_id
    ):
        """
        Добавить нового учителя.
        
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
        except:
            self.__session.rollback()
            raise

    def update_teacher(
            self,
            teacher_id,
            new_email
    ):
        """
        Обновить email учителя.
        
        Args:
            teacher_id (int): ID учителя для обновления
            new_email (str): Новый email
            
        Raises:
            ValueError: если параметры некорректны
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
        except:
            self.__session.rollback()
            raise

    def delete(self, teacher_id):
        """
        Удалить учителя по ID.
        
        Args:
            teacher_id (int): ID учителя для удаления
            
        Raises:
            ValueError: если teacher_id некорректный
        """
        if not teacher_id or teacher_id <= 0:
            raise ValueError("teacher_id должен быть положительным числом")
            
        query = text("DELETE FROM teacher WHERE teacher_id = :teacher_id")
        try:
            result = self.__session.execute(query, {'teacher_id': teacher_id})
            self.__session.commit()
            if result.rowcount == 0:
                raise ValueError(f"Учитель с ID {teacher_id} не найден")
        except:
            self.__session.rollback()
            raise
            
    def __del__(self):
        """Закрываем сессию при удалении объекта."""
        if hasattr(self, '_TeacherTable__session'):
            self.__session.close()
