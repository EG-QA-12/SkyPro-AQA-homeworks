#!/usr/bin/env python3
"""
Тесты публикации ответов с новым фреймворком

Этот файл содержит тесты для проверки функциональности публикации 
ответов на вопросы через админ-панель с использованием нового фреймворка.

Новый подход:
- Использует базовый класс APITestBase
- Автоматическая авторизация и обработка ошибок
- Упрощенный и более читаемый код
- Встроенные вспомогательные методы
"""

import pytest
import allure
from framework.test_bases.api_test_base import APITestBase
from framework.utils.enums import QuestionStatus, AnswerPublicationType


class TestAnswerPublication(APITestBase):
    """Тесты для публикации ответов."""
    
    @allure.title("Публикация ответа на вопрос")
    @allure.description("Проверка возможности публикации ответа через админ-API")
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.answer
    @pytest.mark.smoke
    def test_publish_answer_to_question(self):
        """Тест публикации ответа на вопрос."""
        
        with allure.step("Создание тестового вопроса"):
            test_question = self.question_factory.generate_question()
            success = self.admin_client.create_test_question(test_question)
            assert success is True, "Не удалось создать тестовый вопрос"
            
            self.logger.info(f"Создан вопрос для ответа: {test_question}")
        
        with allure.step("Поиск вопроса для ответа"):
            questions = self.moder_client.search_questions(query=test_question)
            assert questions is not None, "Поиск вернул None"
            assert len(questions) > 0, "Вопрос не найден"
            
            question_id = questions[0]["id"]
            self.logger.info(f"Найден вопрос для ответа: ID={question_id}")
        
        with allure.step("Ответ на вопрос"):
            answer_text = "Это подробный ответ на ваш вопрос. Спасибо за обращение!"
            success = self.moder_client.answer_question(
                question_id=question_id,
                answer_text=answer_text
            )
            assert success is True, "Не удалось ответить на вопрос"
            
            self.logger.info(f"✅ Ответ на вопрос ID={question_id} отправлен")
        
        with allure.step("Проверка статуса вопроса после ответа"):
            # Получаем обновленную информацию о вопросе
            updated_questions = self.moder_client.search_questions(query=test_question)
            assert updated_questions is not None, "Поиск вернул None"
            
            updated_question = None
            for question in updated_questions:
                if question["id"] == question_id:
                    updated_question = question
                    break
            
            assert updated_question is not None, "Вопрос не найден после ответа"
            assert updated_question["status"] == QuestionStatus.PUBLISHED.value, (
                f"Вопрос имеет статус {updated_question['status']}, "
                f"ожидался {QuestionStatus.PUBLISHED.value}"
            )
            
            self.logger.info(f"✅ Вопрос ID={question_id} имеет правильный статус")


class TestAnswerPublicationTypes(APITestBase):
    """Тесты различных типов публикации ответов."""
    
    @allure.title("Публикация ответа с типом {answer_type}")
    @allure.description("Проверка публикации ответа с различными типами")
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.answer
    @pytest.mark.parametrize("answer_type", [
        AnswerPublicationType.ANSWER,
        AnswerPublicationType.SUPPORTIVE,
        AnswerPublicationType.MAXIMUM,
    ], ids=["answer", "supportive", "maximum"])
    def test_publish_answer_with_different_types(self, answer_type):
        """Тест публикации ответа с различными типами."""
        
        with allure.step(f"Создание тестового вопроса для типа {answer_type.name}"):
            test_question = self.question_factory.generate_question()
            success = self.admin_client.create_test_question(test_question)
            assert success is True, "Не удалось создать тестовый вопрос"
        
        with allure.step("Поиск вопроса для ответа"):
            questions = self.moder_client.search_questions(query=test_question)
            assert questions is not None, "Поиск вернул None"
            assert len(questions) > 0, "Вопрос не найден"
            
            question_id = questions[0]["id"]
        
        with allure.step(f"Ответ на вопрос с типом {answer_type.name}"):
            answer_text = f"Ответ типа {answer_type.name}. Подробная информация..."
            success = self.moder_client.answer_question(
                question_id=question_id,
                answer_text=answer_text,
                publication_type=answer_type
            )
            assert success is True, f"Не удалось ответить с типом {answer_type.name}"
            
            self.logger.info(
                f"✅ Ответ типа {answer_type.name} на вопрос ID={question_id} отправлен"
            )


class TestAnswerPublicationWorkflow(APITestBase):
    """Тесты workflow публикации ответов."""
    
    @allure.title("Полный цикл: создание → ответ → публикация")
    @allure.description("Проверка полного цикла публикации ответа на вопрос")
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.answer
    @pytest.mark.regression
    def test_full_answer_publication_workflow(self):
        """Тест полного цикла публикации ответа."""
        
        with allure.step("1. Создание вопроса"):
            test_question = self.question_factory.generate_question(
                category="договоры"
            )
            success = self.admin_client.create_test_question(test_question)
            assert success is True, "Не удалось создать вопрос"
            
            self.logger.info(f"1. Создан вопрос: {test_question}")
        
        with allure.step("2. Поиск вопроса для ответа"):
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
        
        with allure.step("4. Ответ на вопрос"):
            answer_text = (
                "Спасибо за ваш вопрос. Мы внимательно изучили ваш запрос "
                "и готовы предоставить подробную информацию. "
                "Вот наш ответ на ваш вопрос о договорах..."
            )
            success = self.moder_client.answer_question(
                question_id=question_id,
                answer_text=answer_text
            )
            assert success is True, "Не удалось ответить на вопрос"
            
            self.logger.info(f"4. Ответ на вопрос ID={question_id} отправлен")
        
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
            
            assert updated_question is not None, "Вопрос не найден после ответа"
            assert updated_question["status"] == QuestionStatus.PUBLISHED.value, (
                f"Неверный статус: {updated_question['status']}, "
                f"ожидался {QuestionStatus.PUBLISHED.value}"
            )
            
            self.logger.info(
                f"5. Вопрос ID={question_id} успешно опубликован, "
                f"статус={updated_question['status']}"
            )


class TestAnswerPublicationValidation(APITestBase):
    """Тесты валидации публикации ответов."""
    
    @allure.title("Ответ на несуществующий вопрос")
    @allure.description("Проверка обработки ответа на несуществующий вопрос")
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.validation
    @pytest.mark.answer
    def test_answer_nonexistent_question(self):
        """Тест ответа на несуществующий вопрос."""
        
        with allure.step("Попытка ответа на несуществующий вопрос"):
            non_existent_id = "999999999"
            success = self.moder_client.answer_question(
                question_id=non_existent_id,
                answer_text="Тестовый ответ"
            )
            # Ожидаем что система корректно обработает несуществующий ID
            assert success is False, (
                "Система должна отклонить ответ на несуществующий вопрос"
            )
            
            self.logger.info(
                f"✅ Система корректно отклонила ответ на вопрос ID={non_existent_id}"
            )
    
    @allure.title("Ответ с пустым текстом")
    @allure.description("Проверка обработки пустого ответа")
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.validation
    @pytest.mark.answer
    def test_answer_with_empty_text(self):
        """Тест ответа с пустым текстом."""
        
        with allure.step("Создание тестового вопроса"):
            test_question = self.question_factory.generate_question()
            success = self.admin_client.create_test_question(test_question)
            assert success is True, "Не удалось создать тестовый вопрос"
        
        with allure.step("Поиск вопроса для ответа"):
            questions = self.moder_client.search_questions(query=test_question)
            assert questions is not None, "Поиск вернул None"
            assert len(questions) > 0, "Вопрос не найден"
            
            question_id = questions[0]["id"]
        
        with allure.step("Попытка ответа с пустым текстом"):
            success = self.moder_client.answer_question(
                question_id=question_id,
                answer_text=""
            )
            # Ожидаем что система корректно обработает пустой ответ
            assert success is False, (
                "Система должна отклонить пустой ответ"
            )
            
            self.logger.info(
                f"✅ Система корректно отклонила пустой ответ на вопрос ID={question_id}"
            )


if __name__ == "__main__":
    # Запуск тестов напрямую
    # python tests/integration/test_publish_answer_new.py
    pytest.main([__file__, "-v", "-s"])
