#!/usr/bin/env python3
"""
Тесты поиска и фильтрации вопросов с новым фреймворком

Этот файл содержит тесты для проверки функциональности поиска 
и фильтрации вопросов в панели модерации.

Новый подход:
- Использует централизованные фикстуры
- Автоматическая авторизация и обработка ошибок
- Упрощенный и более читаемый код
- Встроенные вспомогательные методы
"""

import pytest
import allure

# Импортируем новые компоненты фреймворка
from framework.utils.enums import QuestionStatus


@allure.title("Поиск вопросов по тексту")
@allure.description(
    "Проверка возможности поиска вопросов по тексту содержимого"
)
@pytest.mark.api
@pytest.mark.search
@pytest.mark.question
def test_search_questions_by_text(admin_client):
    """Тест поиска вопросов по тексту содержимого."""
    
    with allure.step("Генерация тестового вопроса"):
        test_text = "тестовый вопрос для поиска"
        # Создаем тестовый вопрос
        success = admin_client.create_test_question(test_text)
        assert success, "Не удалось создать тестовый вопрос"
    
    with allure.step("Поиск вопросов по тексту"):
        questions = admin_client.search_questions(query=test_text)
        assert questions is not None, "Поиск вернул None"
        assert len(questions) > 0, "Поиск не нашел вопросов"
        
        # Проверяем что найденные вопросы содержат искомый текст
        found_question = None
        for question in questions:
            if test_text.lower() in question["text"].lower():
                found_question = question
                break
        
        assert found_question is not None, (
            f"Вопрос с текстом '{test_text}' не найден в результатах поиска"
        )
    
    with allure.step("Проверка точности поиска"):
        # Поиск по несуществующему тексту должен вернуть пустой результат
        non_existent_questions = admin_client.search_questions(
            query="несуществующийтекст12345"
        )
        assert non_existent_questions is not None, "Поиск вернул None"
        assert len(non_existent_questions) == 0, (
            "Поиск по несуществующему тексту вернул результаты"
        )


@allure.title("Фильтрация вопросов по статусу")
@allure.description("Проверка фильтрации вопросов по различным статусам")
@pytest.mark.api
@pytest.mark.filter
@pytest.mark.question
@pytest.mark.parametrize("status", [
    QuestionStatus.PENDING,
    QuestionStatus.PUBLISHED,
    QuestionStatus.ARCHIVED,
], ids=["pending", "published", "archived"])
def test_filter_questions_by_status(admin_client, status):
    """Тест фильтрации вопросов по статусу."""
    
    with allure.step(f"Получение вопросов со статусом {status.value}"):
        questions = admin_client.get_questions_by_status(status=status)
        
        # Проверяем что все вопросы имеют правильный статус
        if questions:
            for question in questions[:5]:  # Проверяем первые 5 вопросов
                assert question["status"] == status.value, (
                    f"Вопрос имеет статус {question['status']}, "
                    f"ожидался {status.value}"
                )


@allure.title("Сортировка вопросов по дате")
@allure.description("Проверка сортировки вопросов по дате создания")
@pytest.mark.api
@pytest.mark.sort
@pytest.mark.question
def test_sort_questions_by_date(admin_client):
    """Тест сортировки вопросов по дате создания."""
    
    with allure.step("Получение вопросов с сортировкой по дате"):
        questions = admin_client.get_questions_sorted_by_date(order="desc")
        assert questions is not None, "Получение вопросов вернуло None"
        assert len(questions) > 0, "Нет вопросов для сортировки"
    
    with allure.step("Проверка правильности сортировки"):
        # Проверяем что вопросы отсортированы по дате (новые первыми)
        if len(questions) > 1:
            for i in range(len(questions) - 1):
                current_date = questions[i].get("created_at")
                next_date = questions[i + 1].get("created_at")
                
                if current_date and next_date:
                    # Для строковых дат используем лексикографическое сравнение
                    assert current_date >= next_date, \
                        f"Вопросы не отсортированы по дате: {current_date} < {next_date}"


@allure.title("Комбинированный поиск и фильтрация")
@allure.description("Проверка комбинированного поиска с фильтрацией по статусу")
@pytest.mark.api
@pytest.mark.search
@pytest.mark.filter
@pytest.mark.question
def test_combined_search_and_filter(admin_client):
    """Тест комбинированного поиска с фильтрацией."""
    
    with allure.step("Комбинированный поиск: текст + статус"):
        search_text = "вопрос"
        status = QuestionStatus.PUBLISHED
        
        questions = admin_client.search_questions(
            query=search_text,
            status=status
        )
        
        assert questions is not None, "Поиск вернул None"
        
        # Проверяем что все найденные вопросы соответствуют критериям
        for question in questions[:3]:  # Проверяем первые 3 вопроса
            assert search_text.lower() in question["text"].lower(), \
                f"Вопрос не содержит искомый текст: {question['text']}"
            assert question["status"] == status.value, (
                f"Вопрос имеет статус {question['status']}, "
                f"ожидался {status.value}"
            )


@allure.title("Пагинация результатов поиска")
@allure.description("Проверка пагинации при поиске вопросов")
@pytest.mark.api
@pytest.mark.search
@pytest.mark.pagination
@pytest.mark.question
def test_search_pagination(admin_client):
    """Тест пагинации результатов поиска."""
    
    with allure.step("Поиск с ограничением количества результатов"):
        limit = 10
        questions = admin_client.search_questions(query="", limit=limit)
        
        assert questions is not None, "Поиск вернул None"
        assert len(questions) <= limit, (
            f"Получено больше результатов чем запрошено: "
            f"{len(questions)} > {limit}"
        )
    
    with allure.step("Поиск с пропуском результатов"):
        skip = 5
        questions_page1 = admin_client.search_questions(query="", limit=10, skip=0)
        questions_page2 = admin_client.search_questions(query="", limit=10, skip=skip)
        
        assert questions_page1 is not None, "Первая страница поиска вернула None"
        assert questions_page2 is not None, "Вторая страница поиска вернула None"
        
        # Проверяем что результаты разные (если есть достаточно данных)
        if len(questions_page1) > skip and len(questions_page2) > 0:
            # Сравниваем первые элементы после пропуска
            if skip < len(questions_page1):
                first_item_page1 = questions_page1[skip]
                first_item_page2 = questions_page2[0]
                # Они могут быть разными (проверяем что это не один и тот же вопрос)
                assert first_item_page1.get("id") != first_item_page2.get("id") or \
                       first_item_page1.get("text") != first_item_page2.get("text"), \
                       "Результаты пагинации идентичны"


@allure.title("Поиск по категориям вопросов")
@allure.description("Проверка поиска вопросов по категориям")
@pytest.mark.api
@pytest.mark.search
@pytest.mark.question
def test_search_questions_by_category(admin_client):
    """Тест поиска вопросов по категориям."""
    
    with allure.step("Получение доступных категорий"):
        categories = admin_client.get_question_categories()
        assert categories is not None, "Получение категорий вернуло None"
        assert len(categories) > 0, "Нет доступных категорий"
    
    with allure.step("Поиск вопросов по первой категории"):
        first_category = categories[0]
        questions = admin_client.search_questions(category=first_category)
        
        assert questions is not None, "Поиск по категории вернул None"
        
        # Проверяем что вопросы принадлежат указанной категории
        if questions:
            for question in questions[:3]:  # Проверяем первые 3 вопроса
                question_category = question.get("category")
                assert question_category == first_category, (
                    f"Вопрос имеет категорию '{question_category}', "
                    f"ожидалась '{first_category}'"
                )


@allure.title("Валидация параметров поиска")
@allure.description("Проверка валидации параметров поиска вопросов")
@pytest.mark.api
@pytest.mark.search
@pytest.mark.validation
@pytest.mark.question
@pytest.mark.parametrize("invalid_limit", [
    -1,  # Отрицательное значение
    0,   # Нулевое значение
    10000,  # Слишком большое значение
], ids=["negative", "zero", "too_large"])
def test_search_validation_invalid_limit(admin_client, invalid_limit):
    """Тест валидации некорректных значений limit."""
    
    with allure.step(f"Поиск с некорректным значением limit: {invalid_limit}"):
        # Ожидаем что система корректно обработает некорректные значения
        questions = admin_client.search_questions(query="", limit=invalid_limit)
        assert questions is not None, "Поиск вернул None"
        # Система должна использовать значение по умолчанию или ограничить диапазон


@allure.title("Поиск с пустыми параметрами")
@allure.description("Проверка поиска с пустыми или None параметрами")
@pytest.mark.api
@pytest.mark.search
@pytest.mark.validation
@pytest.mark.question
def test_search_with_empty_parameters(admin_client):
    """Тест поиска с пустыми параметрами."""
    
    with allure.step("Поиск с пустым текстом запроса"):
        questions = admin_client.search_questions(query="")
        assert questions is not None, (
            "Поиск с пустым запросом вернул None"
        )
    
    with allure.step("Поиск с None в параметрах"):
        questions = admin_client.search_questions(query=None)
        assert questions is not None, (
            "Поиск с None вернул None"
        )


if __name__ == "__main__":
    # Этот блок позволяет запускать тесты напрямую
    # python tests/integration/test_question_search_filter.py
    pytest.main([__file__, "-v", "-s"])
