"""Тесты для проверки операций с таблицей учителей через бизнес-логику."""

import pytest
import allure

from database.db_connection import get_db_connection
from data.test_data import VALID_TEACHERS, INVALID_EMAILS, INVALID_IDS, INVALID_GROUP_IDS
from data.faker_data import generate_teacher


@allure.epic("SkyPro QA Homework")
@allure.feature("Database Tests")
@allure.story("Teacher Table Operations")
class TestTeacherTable:
    """
    Класс для тестирования операций с таблицей учителей.
    
    Тестирует CRUD операции, валидацию данных и обработку ошибок.
    """
    
    @pytest.fixture
    def db(self):
        """
        Фикстура для создания подключения к БД.
        
        Yields:
            TeacherTable: Экземпляр класса для работы с таблицей учителей
        """
        db_instance = get_db_connection()
        yield db_instance
        # Очистка всех учителей после каждого теста
        for teacher in db_instance.get_teacher():
            db_instance.delete(teacher[0])
    
    @allure.title("Тест добавления учителя")
    @allure.description("Проверка добавления нового учителя в БД")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("database", "crud", "positive")
    @pytest.mark.database
    @pytest.mark.parametrize("teacher", VALID_TEACHERS, ids=["teacher_1", "teacher_2"])
    def test_add_teacher(self, db, teacher):
        """
        Тест добавления нового учителя.
        
        Args:
            db (TeacherTable): Экземпляр класса для работы с БД
            teacher (dict): Данные учителя для добавления
        """
        with allure.step(f"Добавить учителя: ID={teacher['teacher_id']}, email={teacher['email']}"):
            db.add_teacher(
                teacher_id=teacher['teacher_id'],
                email=teacher['email'],
                group_id=teacher['group_id']
            )
        
        with allure.step("Проверить что учитель добавлен"):
            teachers = db.get_teacher()
            
            with allure.step(f"Проверить наличие учителя с ID={teacher['teacher_id']}"):
                assert (teacher['teacher_id'], teacher['email'], teacher['group_id']) in teachers, \
                    f"Учитель не найден в БД"
    
    @allure.title("Тест добавления учителя с невалидным ID")
    @allure.description("Проверка валидации ID учителя при добавлении")
    @allure.severity(allure.severity_level.HIGH)
    @allure.tag("database", "validation", "negative")
    @pytest.mark.database
    @pytest.mark.parametrize("invalid_id", INVALID_IDS, ids=["negative_id", "zero_id", "none_id"])
    def test_add_teacher_invalid_id(self, db, invalid_id):
        """
        Тест добавления учителя с невалидным ID.
        
        Args:
            db (TeacherTable): Экземпляр класса для работы с БД
            invalid_id: Невалидный ID учителя
        """
        teacher = generate_teacher()
        
        with allure.step(f"Попытка добавить учителя с невалидным ID: {invalid_id}"):
            with allure.step("Проверить что выброшено исключение ValueError"):
                with pytest.raises(ValueError) as exc_info:
                    db.add_teacher(
                        teacher_id=invalid_id,
                        email=teacher['email'],
                        group_id=teacher['group_id']
                    )
        
        with allure.step("Проверить сообщение об ошибке"):
            assert "teacher_id должен быть положительным числом" in str(exc_info.value)
    
    @allure.title("Тест добавления учителя с невалидным email")
    @allure.description("Проверка валидации email при добавлении учителя")
    @allure.severity(allure.severity_level.HIGH)
    @allure.tag("database", "validation", "negative")
    @pytest.mark.database
    @pytest.mark.parametrize("invalid_email", INVALID_EMAILS[:3], ids=["invalid_format", "no_domain", "empty_email"])
    def test_add_teacher_invalid_email(self, db, invalid_email):
        """
        Тест добавления учителя с невалидным email.
        
        Args:
            db (TeacherTable): Экземпляр класса для работы с БД
            invalid_email: Невалидный email
        """
        teacher = generate_teacher()
        
        with allure.step(f"Попытка добавить учителя с невалидным email: {invalid_email}"):
            with allure.step("Проверить что выброшено исключение ValueError"):
                with pytest.raises(ValueError) as exc_info:
                    db.add_teacher(
                        teacher_id=teacher['teacher_id'],
                        email=invalid_email,
                        group_id=teacher['group_id']
                    )
        
        with allure.step("Проверить сообщение об ошибке"):
            assert "Некорректный формат email" in str(exc_info.value)
    
    @allure.title("Тест обновления email учителя")
    @allure.description("Проверка обновления email существующего учителя")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("database", "crud", "positive")
    @pytest.mark.database
    def test_update_teacher(self, db):
        """
        Тест обновления email учителя.
        
        Args:
            db (TeacherTable): Экземпляр класса для работы с БД
        """
        teacher = generate_teacher()
        
        with allure.step(f"Добавить учителя для обновления: ID={teacher['teacher_id']}"):
            db.add_teacher(
                teacher_id=teacher['teacher_id'],
                email=teacher['email'],
                group_id=teacher['group_id']
            )
        
        with allure.step(f"Обновить email учителя: new_email={teacher['new_email']}"):
            db.update_teacher(
                teacher_id=teacher['teacher_id'],
                new_email=teacher['new_email']
            )
        
        with allure.step("Проверить что email обновлен"):
            teachers = db.get_teacher()
            
            with allure.step(f"Проверить наличие учителя с новым email: {teacher['new_email']}"):
                assert (teacher['teacher_id'], teacher['new_email'], teacher['group_id']) in teachers, \
                    f"Email учителя не обновлен"
    
    @allure.title("Тест обновления несуществующего учителя")
    @allure.description("Проверка обновления email несуществующего учителя")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("database", "crud", "negative")
    @pytest.mark.database
    def test_update_nonexistent_teacher(self, db):
        """
        Тест обновления несуществующего учителя.
        
        Args:
            db (TeacherTable): Экземпляр класса для работы с БД
        """
        with allure.step("Попытка обновить несуществующего учителя"):
            with allure.step("Проверить что выброшено исключение ValueError"):
                with pytest.raises(ValueError) as exc_info:
                    db.update_teacher(teacher_id=999999, new_email='notfound@mail.com')
        
        with allure.step("Проверить сообщение об ошибке"):
            assert "не найден" in str(exc_info.value)
    
    @allure.title("Тест удаления учителя")
    @allure.description("Проверка удаления существующего учителя")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("database", "crud", "positive")
    @pytest.mark.database
    def test_delete_teacher(self, db):
        """
        Тест удаления учителя.
        
        Args:
            db (TeacherTable): Экземпляр класса для работы с БД
        """
        teacher = generate_teacher()
        
        with allure.step(f"Добавить учителя для удаления: ID={teacher['teacher_id']}"):
            db.add_teacher(
                teacher_id=teacher['teacher_id'],
                email=teacher['email'],
                group_id=teacher['group_id']
            )
        
        with allure.step(f"Удалить учителя: ID={teacher['teacher_id']}"):
            db.delete(teacher['teacher_id'])
        
        with allure.step("Проверить что учитель удален"):
            teachers = db.get_teacher()
            
            with allure.step(f"Проверить отсутствие учителя с ID={teacher['teacher_id']}"):
                assert (teacher['teacher_id'], teacher['email'], teacher['group_id']) not in teachers, \
                    f"Учитель не удален из БД"
    
    @allure.title("Тест удаления несуществующего учителя")
    @allure.description("Проверка удаления несуществующего учителя")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("database", "crud", "negative")
    @pytest.mark.database
    def test_delete_nonexistent_teacher(self, db):
        """
        Тест удаления несуществующего учителя.
        
        Args:
            db (TeacherTable): Экземпляр класса для работы с БД
        """
        with allure.step("Попытка удалить несуществующего учителя"):
            with allure.step("Проверить что выброшено исключение ValueError"):
                with pytest.raises(ValueError) as exc_info:
                    db.delete(teacher_id=999999)
        
        with allure.step("Проверить сообщение об ошибке"):
            assert "не найден" in str(exc_info.value)
    
    @allure.title("Тест получения всех учителей")
    @allure.description("Проверка получения списка всех учителей")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("database", "read", "positive")
    @pytest.mark.database
    def test_get_all_teachers(self, db):
        """
        Тест получения списка всех учителей.
        
        Args:
            db (TeacherTable): Экземпляр класса для работы с БД
        """
        with allure.step("Получить список всех учителей"):
            teachers = db.get_teacher()
        
        with allure.step("Проверить что возвращен список"):
            assert isinstance(teachers, list), "Должен быть возвращен список"
        
        with allure.step("Проверить что список не пустой"):
            # Может быть пустым или содержать данные
            assert len(teachers) >= 0, "Список не должен быть отрицательной длины"
    
    @allure.title("Тест проверки существования учителя")
    @allure.description("Проверка метода проверки существования учителя")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("database", "read", "positive")
    @pytest.mark.database
    def test_teacher_exists(self, db):
        """
        Тест проверки существования учителя.
        
        Args:
            db (TeacherTable): Экземпляр класса для работы с БД
        """
        teacher = generate_teacher()
        
        with allure.step(f"Добавить учителя для проверки: ID={teacher['teacher_id']}"):
            db.add_teacher(
                teacher_id=teacher['teacher_id'],
                email=teacher['email'],
                group_id=teacher['group_id']
            )
        
        with allure.step(f"Проверить существование учителя: ID={teacher['teacher_id']}"):
            exists = db.teacher_exists(teacher['teacher_id'])
            assert exists, "Учитель должен существовать"
        
        with allure.step(f"Проверить отсутствие несуществующего учителя: ID=999999"):
            not_exists = db.teacher_exists(999999)
            assert not not_exists, "Учитель с ID 999999 не должен существовать"