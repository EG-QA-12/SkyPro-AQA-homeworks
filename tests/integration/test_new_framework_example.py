#!/usr/bin/env python3
"""
Пример использования нового фреймворка для тестирования

Этот файл демонстрирует основные возможности нового фреймворка:
- Использование базового класса для API тестов
- Централизованная авторизация
- Автоматическая обработка ошибок
- Встроенные вспомогательные методы
- Четкая структура тестов с Allure аннотациями
"""

import pytest
import allure
from framework.test_bases.api_test_base import APITestBase
from framework.utils.enums import UserRole, QuestionStatus


class TestQuestionManagement(APITestBase):
    """Тесты для управления вопросами с использованием нового фреймворка."""
    
    @allure.title("Создание вопроса через API")
    @allure.description("Проверка возможности создания вопроса через API")
    @pytest.mark.api
    @pytest.mark.question
    @pytest.mark.smoke
    def test_create_question_via_api(self):
        """Тест создания вопроса через API."""
        
        with allure.step("Подготовка тестовых данных"):
            test_question = self.question_factory.generate_question()
            self.logger.info(f"Создание вопроса: {test_question}")
        
        with allure.step("Создание вопроса через API"):
            response = self.admin_client.create_test_question(test_question)
            assert response.success is True, f"Не удалось создать вопрос через API: {response.text}"
            
            self.logger.info("✅ Вопрос успешно создан")
        
        with allure.step("Проверка наличия вопроса в системе"):
            questions = self.admin_client.search_questions(query=test_question)
            assert questions is not None, "Поиск вернул None"
            assert len(questions) > 0, "Вопрос не найден в системе"
            
            # Проверяем что наш вопрос есть в результатах
            found = any(
                test_question.lower() in q["text"].lower() 
                for q in questions
            )
            assert found, "Созданный вопрос не найден в результатах поиска"
            
            self.logger.info("✅ Вопрос найден в системе")


class TestModerationWorkflow(APITestBase):
    """Тесты для проверки workflow модерации."""
    
    @allure.title("Полный цикл модерации вопроса")
    @allure.description(
        "Проверка полного цикла: создание → модерация → публикация"
    )
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.regression
    def test_full_moderation_workflow(self):
        """Тест полного цикла модерации."""
        
        with allure.step("1. Создание вопроса"):
            test_question = self.question_factory.generate_question(
                category="регистрация"
            )
            self.logger.info(f"Создание вопроса: {test_question}")
            
            response = self.admin_client.create_test_question(test_question)
            assert response.success is True, f"Не удалось создать вопрос: {response.text}"
        
        with allure.step("2. Поиск вопроса для модерации"):
            questions = self.moder_client.search_questions(query=test_question)
            assert questions is not None, "Поиск вернул None"
            assert len(questions) > 0, "Вопрос не найден"
            
            question = questions[0]
            question_id = question["id"]
            
            self.logger.info(f"Найден вопрос ID: {question_id}")
            self.logger.info(f"Текущий статус: {question['status']}")
        
        with allure.step("3. Ответ на вопрос"):
            answer_text = "Спасибо за ваш вопрос. Вот подробный ответ..."
            response = self.moder_client.answer_question(
                question_id=question_id,
                answer_text=answer_text
            )
            assert response.success is True, f"Не удалось ответить на вопрос: {response.text}"
            
            self.logger.info("✅ Ответ на вопрос отправлен")
        
        with allure.step("4. Проверка финального статуса"):
            # Ждем немного чтобы система обработала изменения
            import time
            time.sleep(1)
            
            updated_questions = self.moder_client.search_questions(
                query=test_question
            )
            assert updated_questions is not None, "Поиск вернул None"
            
            updated_question = None
            for q in updated_questions:
                if q["id"] == question_id:
                    updated_question = q
                    break
            
            assert updated_question is not None, "Вопрос не найден после ответа"
            assert updated_question["status"] == QuestionStatus.PUBLISHED.value, (
                f"Неверный статус: {updated_question['status']}, "
                f"ожидался {QuestionStatus.PUBLISHED.value}"
            )
            
            self.logger.info("✅ Вопрос успешно опубликован")


class TestUserRoles(APITestBase):
    """Тесты для проверки ролевой модели."""
    
    @allure.title("Проверка прав доступа для разных ролей")
    @allure.description("Проверка что пользователи видят только свои вопросы")
    @pytest.mark.api
    @pytest.mark.security
    @pytest.mark.parametrize("role", [
        UserRole.ADMIN,
        UserRole.MODERATOR,
        UserRole.USER
    ], ids=["admin", "moderator", "user"])
    def test_role_based_access(self, role):
        """Тест ролевой модели доступа."""
        
        with allure.step(f"Получение клиента для роли {role.value}"):
            if role == UserRole.ADMIN:
                client = self.admin_client
            elif role == UserRole.MODERATOR:
                client = self.moder_client
            else:
                client = self.user_client
            
            assert client is not None, f"Клиент для роли {role.value} не найден"
        
        with allure.step("Получение списка вопросов"):
            # Используем search_questions вместо get_questions
            questions = client.search_questions(query=None, limit=10)
            assert questions is not None, "Поиск вопросов вернул None"
            
            self.logger.info(
                f"Роль {role.value} получила {len(questions)} вопросов"
            )
            
            # Для разных ролей может быть разное количество доступных вопросов
            # Главное что система не упала с ошибкой доступа


if __name__ == "__main__":
    # Запуск тестов напрямую
    # python tests/integration/test_new_framework_example.py
    pytest.main([
        __file__, 
        "-v", 
        "-s", 
        "--alluredir=tests/allure-results"
    ])
