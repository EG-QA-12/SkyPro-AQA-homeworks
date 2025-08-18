#!/usr/bin/env python3
"""
Тест ответа на вопрос с новым фреймворком

Этот файл демонстрирует использование нового фреймворка для тестирования
функциональности ответа на вопросы в панели модерации.

Новый подход:
- Использует централизованные фикстуры
- Автоматическая авторизация и обработка ошибок
- Упрощенный и более читаемый код
- Встроенные вспомогательные методы
"""

import pytest
import allure
from framework.utils.enums import QuestionStatus


@allure.title("Ответ на вопрос модератором")
@allure.description(
    "Проверка возможности ответа на вопрос через панель модерации"
)
@pytest.mark.api
@pytest.mark.moderation
@pytest.mark.question
def test_answer_question_by_moderator(moder_client):
    """Тест ответа на вопрос модератором."""
    
    with allure.step("Генерация тестового вопроса"):
        test_question = "Тестовый вопрос для проверки ответа?"
        success = moder_client.create_test_question(test_question)
        assert success, "Не удалось создать тестовый вопрос"
    
    with allure.step("Поиск вопроса для ответа"):
        questions = moder_client.search_questions(query=test_question)
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
    
    with allure.step("Ответ на вопрос"):
        answer_text = "Это тестовый ответ на вопрос."
        success = moder_client.answer_question(
            question_id=question_id,
            answer_text=answer_text
        )
        assert success, "Не удалось ответить на вопрос"
    
    with allure.step("Проверка статуса вопроса после ответа"):
        # Получаем обновленную информацию о вопросе
        updated_questions = moder_client.search_questions(query=test_question)
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


@allure.title("Ответ на вопрос с пустым текстом")
@allure.description("Проверка обработки пустого ответа на вопрос")
@pytest.mark.api
@pytest.mark.moderation
@pytest.mark.validation
@pytest.mark.question
def test_answer_question_with_empty_text(moder_client):
    """Тест ответа на вопрос с пустым текстом."""
    
    with allure.step("Генерация тестового вопроса"):
        test_question = "Тестовый вопрос для проверки пустого ответа?"
        success = moder_client.create_test_question(test_question)
        assert success, "Не удалось создать тестовый вопрос"
    
    with allure.step("Поиск вопроса для ответа"):
        questions = moder_client.search_questions(query=test_question)
        assert questions is not None, "Поиск вернул None"
        assert len(questions) > 0, "Вопрос не найден"
        
        question_id = questions[0]["id"]
    
    with allure.step("Попытка ответа с пустым текстом"):
        success = moder_client.answer_question(
            question_id=question_id,
            answer_text=""
        )
        # Ожидаем что система корректно обработает пустой ответ
        # (может быть как ошибка, так и автоматическое отклонение)
        assert not success or success is False, (
            "Система должна отклонить пустой ответ"
        )


@allure.title("Ответ на несуществующий вопрос")
@allure.description("Проверка обработки ответа на несуществующий вопрос")
@pytest.mark.api
@pytest.mark.moderation
@pytest.mark.validation
@pytest.mark.question
def test_answer_nonexistent_question(moder_client):
    """Тест ответа на несуществующий вопрос."""
    
    with allure.step("Попытка ответа на несуществующий вопрос"):
        non_existent_id = "999999999"
        success = moder_client.answer_question(
            question_id=non_existent_id,
            answer_text="Тестовый ответ"
        )
        # Ожидаем что система корректно обработает несуществующий ID
        assert not success or success is False, (
            "Система должна отклонить ответ на несуществующий вопрос"
        )


if __name__ == "__main__":
    # Этот блок позволяет запускать тесты напрямую
    # python tests/integration/test_question_answer_new.py
    pytest.main([__file__, "-v", "-s"])
