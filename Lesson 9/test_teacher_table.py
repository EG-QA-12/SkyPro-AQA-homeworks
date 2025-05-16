"""Тесты для проверки операций с таблицей учителей."""

import logging
import time
import pytest
import allure
from db import get_db_connection
from test_data import (
    INVALID_EMAILS,
    INVALID_IDS
)
from faker import Faker
from faker_data import generate_teacher

fake = Faker('ru_RU')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@allure.epic("Teacher Database Management System")
@allure.feature("Teacher CRUD Operations")
class TestTeacher:
    """Класс тестов для операций с учителями."""

    @pytest.fixture(autouse=True)
    @allure.title("Очистка данных после теста")
    def setup_cleanup(self, db):
        """Фикстура для очистки данных после каждого теста."""
        with allure.step("Setting up test environment"):
            pass
        yield
        with allure.step("Cleaning up test data"):
            teachers = db.get_teacher()
            for teacher in teachers:
                db.delete(teacher[0])

    @pytest.fixture
    @allure.title("Создание подключения к БД")
    def db(self):
        """Фикстура для создания подключения к БД через отдельный модуль."""
        with allure.step("Создание подключения к базе данных через db.py"):
            connection = get_db_connection()
            allure.attach(
                str(connection),
                name="DB Connection",
                attachment_type=allure.attachment_type.TEXT
            )
            return connection

    @pytest.fixture(params=[generate_teacher() for _ in range(3)])
    def test_teacher_data(self, request):
        """Параметризованная фикстура с тестовыми данными через Faker."""
        return request.param

    @pytest.fixture
    def faker_teacher(self):
        """Фикстура для генерации случайного учителя через Faker."""
        return generate_teacher()

    @allure.story("Подключение к базе данных")
    @allure.title("Тест подключения к базе данных")
    def test_database_connection(self, db):
        with allure.step("Проверка получения учителей из БД"):
            assert db.get_teacher() is not None

    @allure.story("Добавление учителя")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Добавление нового учителя с валидными данными")
    def test_add_new_teacher(self, db, test_teacher_data):
        with allure.step("Добавление нового учителя"):
            db.add_teacher(
                teacher_id=test_teacher_data['teacher_id'],
                email=test_teacher_data['email'],
                group_id=test_teacher_data['group_id']
            )
        with allure.step("Проверка добавления учителя"):
            result = db.get_teacher()
            assert result[-1] == (
                test_teacher_data['teacher_id'],
                test_teacher_data['email'],
                test_teacher_data['group_id']
            )
        with allure.step("Очистка тестовых данных"):
            db.delete(test_teacher_data['teacher_id'])

    @allure.story("Валидация ID учителя")
    @pytest.mark.parametrize('invalid_id', INVALID_IDS)
    def test_add_teacher_with_invalid_id(self, db, invalid_id):
        with allure.step("Проверка добавления с некорректным ID (Faker):"):
            with pytest.raises(ValueError):
                db.add_teacher(
                    teacher_id=invalid_id,
                    email=generate_teacher()['email'],
                    group_id=generate_teacher()['group_id']
                )

    @allure.story("Валидация email учителя")
    @pytest.mark.parametrize('invalid_email', INVALID_EMAILS)
    def test_add_teacher_with_invalid_email(self, db, invalid_email):
        with allure.step("Проверка добавления с некорректным email (Faker):"):
            with pytest.raises(ValueError) as exc_info:
                db.add_teacher(
                    teacher_id=generate_teacher()['teacher_id'],
                    email=invalid_email,
                    group_id=generate_teacher()['group_id']
                )
            allure.attach(
                str(exc_info.value),
                name="Error Message",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("Валидация group_id учителя")
    @pytest.mark.parametrize('invalid_group_id', [
        None, 0, -1, -100, 'abc', fake.random_number(digits=10)
    ])
    def test_add_teacher_with_invalid_group_id(self, db, invalid_group_id):
        with allure.step(
            "Проверка добавления с некорректным group_id (Faker):"
        ):
            with pytest.raises(ValueError):
                db.add_teacher(
                    teacher_id=generate_teacher()['teacher_id'],
                    email=generate_teacher()['email'],
                    group_id=invalid_group_id
                )

    @allure.story("Обновление учителя")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Обновление email учителя")
    def test_update_teacher(self, db, test_teacher_data):
        with allure.step("Добавление учителя для обновления"):
            db.add_teacher(
                teacher_id=test_teacher_data['teacher_id'],
                email=test_teacher_data['email'],
                group_id=test_teacher_data['group_id']
            )
        with allure.step("Обновление email учителя"):
            db.update_teacher(
                teacher_id=test_teacher_data['teacher_id'],
                new_email=test_teacher_data['new_email']
            )
        with allure.step("Проверка обновления email учителя"):
            result = db.get_teacher()
            assert result[-1] == (
                test_teacher_data['teacher_id'],
                test_teacher_data['new_email'],
                test_teacher_data['group_id']
            )
        with allure.step("Очистка тестовых данных"):
            db.delete(test_teacher_data['teacher_id'])

    @pytest.mark.parametrize(
        'teacher_id,email,group_id',
        [
            (
                generate_teacher()['teacher_id'],
                generate_teacher()['email'],
                generate_teacher()['group_id']
            )
            for _ in range(2)
        ]
    )
    @allure.title('Параметрический тест обновления учителя (Faker)')
    def test_update_teacher_param(self, db, teacher_id, email, group_id):
        with allure.step(f'Добавляем учителя {teacher_id}'):
            db.add_teacher(
                teacher_id=teacher_id,
                email=email,
                group_id=group_id
            )
        with allure.step(f'Обновляем email учителя {teacher_id}'):
            db.update_teacher(
                teacher_id=teacher_id,
                new_email='new_' + email
            )
        with allure.step(f'Проверяем обновление учителя {teacher_id}'):
            result = db.get_teacher()
            assert (
                teacher_id,
                'new_' + email,
                group_id
            ) in result
        db.delete(teacher_id)

    @allure.story("Обновление несуществующего учителя")
    def test_update_nonexistent_teacher(self, db):
        with allure.step("Проверка обновления несуществующего учителя"):
            with pytest.raises(ValueError):
                db.update_teacher(
                    teacher_id=999999,
                    new_email='new@test.com'
                )

    @allure.story("Удаление учителя")
    @allure.title("Удаление учителя по ID")
    def test_delete_teacher(self, db, test_teacher_data):
        with allure.step("Получение списка учителей до добавления"):
            list_before = db.get_teacher()
        with allure.step("Добавление учителя для удаления"):
            db.add_teacher(
                teacher_id=test_teacher_data['teacher_id'],
                email=test_teacher_data['email'],
                group_id=test_teacher_data['group_id']
            )
            assert len(db.get_teacher()) == len(list_before) + 1
        with allure.step("Удаление учителя"):
            db.delete(test_teacher_data['teacher_id'])
            assert len(db.get_teacher()) == len(list_before)

    @pytest.mark.parametrize(
        'teacher_id,email,group_id',
        [
            (
                generate_teacher()['teacher_id'],
                generate_teacher()['email'],
                generate_teacher()['group_id']
            )
            for _ in range(2)
        ]
    )
    @allure.title('Параметрический тест удаления учителя (Faker)')
    def test_delete_teacher_param(self, db, teacher_id, email, group_id):
        with allure.step(f'Добавление учителя {teacher_id}'):
            db.add_teacher(
                teacher_id=teacher_id,
                email=email,
                group_id=group_id
            )
        with allure.step(f'Удаление учителя {teacher_id}'):
            db.delete(teacher_id)
        with allure.step(f'Проверка удаления учителя {teacher_id}'):
            result = db.get_teacher()
            assert (
                teacher_id,
                email,
                group_id
            ) not in result

    @allure.story("Удаление несуществующего учителя")
    def test_delete_nonexistent_teacher(self, db):
        with allure.step("Проверка удаления несуществующего учителя"):
            with pytest.raises(ValueError):
                db.delete(999999)

    @allure.story("Производительность")
    @pytest.mark.performance
    @allure.title("Тест производительности при массовых операциях")
    def test_batch_operations(self, db):
        teachers = [
            {'teacher_id': i, 'email': f'teacher{i}@mail.com', 'group_id': 345}
            for i in range(1000, 1100)
        ]
        try:
            with allure.step("Массовое добавление учителей"):
                start_time = time.time()
                for teacher in teachers:
                    db.add_teacher(**teacher)
                duration = time.time() - start_time
                allure.attach(
                    f"Operation took {duration:.2f} seconds",
                    name="Performance Results",
                    attachment_type=allure.attachment_type.TEXT
                )
                assert duration < 5
        finally:
            for teacher in teachers:
                try:
                    db.delete(teacher['teacher_id'])
                except Exception:
                    pass

    @allure.story("Работа с пустой таблицей")
    @allure.title("Проверка работы с пустой таблицей учителей")
    def test_empty_table(self, db):
        with allure.step("Проверка типа и содержимого списка учителей"):
            teachers = db.get_teacher()
            assert isinstance(teachers, list)
            assert len(teachers) == 0 or all(
                isinstance(t, tuple) for t in teachers
            )

    @allure.story("Откат транзакций")
    @allure.title("Тест отката транзакций при ошибке")
    def test_transaction_rollback(self, db):
        with allure.step("Проверка отката транзакции при ошибке"):
            initial_count = len(db.get_teacher())
            try:
                db.add_teacher(teacher_id=1, email='invalid', group_id=None)
            except ValueError:
                pass
            final_count = len(db.get_teacher())
            assert initial_count == final_count

    @allure.story("Массовое добавление и удаление учителей (Faker)")
    @allure.title("Тест большого объема данных (1000 записей, Faker)")
    def test_big_data(self, db):
        teachers = [generate_teacher() for _ in range(1000)]
        try:
            with allure.step("Массовое добавление учителей (Faker)"):
                for teacher in teachers:
                    db.add_teacher(**teacher)
            with allure.step("Проверка наличия всех учителей (Faker)"):
                all_teachers = db.get_teacher()
                for teacher in teachers:
                    assert (
                        teacher['teacher_id'],
                        teacher['email'],
                        teacher['group_id']
                    ) in all_teachers
        finally:
            for teacher in teachers:
                try:
                    db.delete(teacher['teacher_id'])
                except Exception:
                    pass

    @allure.story("Обработка специальных символов в email")
    @allure.title("Тест обработки специальных символов в email")
    def test_special_characters(self, db):
        special_chars_data = {
            'teacher_id': 12134,
            'email': "test.special+chars@mail.com",
            'group_id': 345
        }
        try:
            with allure.step("Добавление учителя со спецсимволами в email"):
                db.add_teacher(**special_chars_data)
            with allure.step("Проверка наличия учителя со спецсимволами"):
                result = db.get_teacher()
                assert result[-1] == (
                    special_chars_data['teacher_id'],
                    special_chars_data['email'],
                    special_chars_data['group_id']
                )
        finally:
            try:
                db.delete(special_chars_data['teacher_id'])
            except ValueError:
                pass

    @allure.story("Добавление учителя через Faker")
    @allure.title("Добавление учителя с рандомными данными (Faker)")
    def test_add_teacher_with_faker(db, faker_teacher):
        with allure.step("Добавление учителя с помощью Faker"):
            db.add_teacher(
                teacher_id=faker_teacher['teacher_id'],
                email=faker_teacher['email'],
                group_id=faker_teacher['group_id']
            )
        with allure.step("Проверка добавления учителя (Faker)"):
            teachers = db.get_teacher()
            assert any(t[0] == faker_teacher['teacher_id'] for t in teachers)
        with allure.step("Очистка тестовых данных (Faker)"):
            db.delete(faker_teacher['teacher_id'])
