#!/usr/bin/env python3
"""
Тесты публикации вопросов с новым фреймворком

Этот файл содержит тесты для проверки функциональности публикации 
вопросов через админ-панель с использованием нового фреймворка.

Новый подход:
- Использует базовый класс APITestBase
- Автоматическая авторизация и обработка ошибок
- Упрощенный и более читаемый код
- Встроенные вспомогательные методы
"""

import pytest
import allure
from framework.test_bases.api_test_base import APITestBase
from framework.utils.enums import QuestionStatus


class TestQuestionPublication(APITestBase):
    """Тесты для публикации вопросов."""
    
    @allure.title("Публикация вопроса через админ-панель")
    @allure.description("Проверка возможности публикации вопроса через админ-API")
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.question
    @pytest.mark.smoke
    def test_publish_question_via_admin_api(self):
        """Тест публикации вопроса через админ-панель."""
        
        with allure.step("Создание тестового вопроса"):
            test_question = self.question_factory.generate_question()
            success = self.admin_client.create_test_question(test_question)
            assert success is True, "Не удалось создать тестовый вопрос"
            
            self.logger.info(f"Создан вопрос для публикации: {test_question}")
        
        with allure.step("Поиск вопроса для публикации"):
            questions = self.moder_client.search_questions(query=test_question)
            assert questions is not None, "Поиск вернул None"
            assert len(questions) > 0, "Вопрос не найден"
            
            # Находим наш тестовый вопрос
            target_question = None
            for question in questions:
                if test_question.lower() in question["text"].lower():
                    target_question = question
                    break
            
            assert target_question is not None, "Тестовый вопрос не найден"
            question_id = target_question["id"]
            
            self.logger.info(f"Найден вопрос для публикации: ID={question_id}")
        
        with allure.step("Публикация вопроса"):
            success = self.moder_client.publish_question(question_id=question_id)
            assert success is True, "Не удалось опубликовать вопрос"
            
            self.logger.info(f"✅ Вопрос ID={question_id} успешно опубликован")
        
        with allure.step("Проверка статуса вопроса после публикации"):
            # Получаем обновленную информацию о вопросе
            updated_questions = self.moder_client.search_questions(query=test_question)
            assert updated_questions is not None, "Поиск вернул None"
            
            updated_question = None
            for question in updated_questions:
                if question["id"] == question_id:
                    updated_question = question
                    break
            
            assert updated_question is not None, "Вопрос не найден после публикации"
            assert updated_question["status"] == QuestionStatus.PUBLISHED.value, (
                f"Вопрос имеет статус {updated_question['status']}, "
                f"ожидался {QuestionStatus.PUBLISHED.value}"
            )
            
            self.logger.info(f"✅ Вопрос ID={question_id} имеет правильный статус")


class TestQuestionPublicationWorkflow(APITestBase):
    """Тесты workflow публикации вопросов."""
    
    @allure.title("Полный цикл: создание → модерация → публикация вопроса")
    @allure.description("Проверка полного цикла публикации вопроса")
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.question
    @pytest.mark.regression
    def test_full_question_publication_workflow(self):
        """Тест полного цикла публикации вопроса."""
        
        with allure.step("1. Создание вопроса администратором"):
            test_question = self.question_factory.generate_question(
                category="регистрация"
            )
            success = self.admin_client.create_test_question(test_question)
            assert success is True, "Не удалось создать вопрос"
            
            self.logger.info(f"1. Создан вопрос: {test_question}")
        
        with allure.step("2. Поиск вопроса модератором"):
            questions = self.moder_client.search_questions(query=test_question)
            assert questions is not None, "Поиск вернул None"
            assert len(questions) > 0, "Вопрос не найден"
            
            question = questions[0]
            question_id = question["id"]
            initial_status = question["status"]
            
            self.logger.info(
                f"2. Найден вопрос ID={question_id}, статус={initial_status}"
            )
        
        with allure.step("3. Взятие вопроса в работу"):
            success = self.moder_client.assign_question(question_id=question_id)
            assert success is True, "Не удалось взять вопрос в работу"
            
            self.logger.info(f"3. Вопрос ID={question_id} взят в работу")
        
        with allure.step("4. Публикация вопроса"):
            success = self.moder_client.publish_question(question_id=question_id)
            assert success is True, "Не удалось опубликовать вопрос"
            
            self.logger.info(f"4. Вопрос ID={question_id} опубликован")
        
        with allure.step("5. Проверка финального статуса"):
            # Ждем немного для обработки изменений
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
            
            assert updated_question is not None, "Вопрос не найден после публикации"
            assert updated_question["status"] == QuestionStatus.PUBLISHED.value, (
                f"Неверный статус: {updated_question['status']}, "
                f"ожидался {QuestionStatus.PUBLISHED.value}"
            )
            
            self.logger.info(
                f"5. Вопрос ID={question_id} успешно опубликован, "
                f"статус={updated_question['status']}"
            )


class TestQuestionPublicationValidation(APITestBase):
    """Тесты валидации публикации вопросов."""
    
    @allure.title("Публикация несуществующего вопроса")
    @allure.description("Проверка обработки публикации несуществующего вопроса")
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.validation
    @pytest.mark.question
    def test_publish_nonexistent_question(self):
        """Тест публикации несуществующего вопроса."""
        
        with allure.step("Попытка публикации несуществующего вопроса"):
            non_existent_id = "999999999"
            success = self.moder_client.publish_question(
                question_id=non_existent_id
            )
            # Ожидаем что система корректно обработает несуществующий ID
            assert success is False, (
                "Система должна отклонить публикацию несуществующего вопроса"
            )
            
            self.logger.info(
                f"✅ Система корректно отклонила публикацию вопроса ID={non_existent_id}"
            )


if __name__ == "__main__":
    # Запуск тестов напрямую
    # python tests/integration/test_publish_question_new.py
    pytest.main([__file__, "-v", "-s"])
