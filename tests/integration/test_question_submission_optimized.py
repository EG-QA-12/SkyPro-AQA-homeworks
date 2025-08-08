#!/usr/bin/env python3
"""
Оптимизированный тест отправки вопросов

Демонстрирует:
- Умную авторизацию с проверкой куки
- Разнообразные тестовые вопросы
- Таргетированную авторизацию
- Параметризованные тесты
"""

import pytest
import allure
import time
from framework.utils.smart_auth_manager import SmartAuthManager
from framework.utils.question_factory import QuestionFactory
from framework.utils.html_parser import ModerationPanelParser


@allure.title("Отправка вопроса с умной авторизацией")
@allure.description("Проверка отправки вопроса с оптимизированной авторизацией")
@allure.feature("API тестирование")
@pytest.mark.api
def test_send_question_with_smart_auth():
    """
    Тест отправки вопроса с умной авторизацией
    
    Демонстрирует оптимизированный подход:
    - Проверка валидности существующей куки
    - Авторизация только при необходимости
    - Разнообразные тестовые вопросы
    """
    
    # Инициализация компонентов
    auth_manager = SmartAuthManager()
    question_factory = QuestionFactory()
    
    # Генерируем уникальный маркер и вопрос (отправляем ровно 1 вопрос)
    marker = f"MARKER_{int(time.time())}"
    base_question = question_factory.generate_question(category="регистрация")
    # Вставляем короткий маркер в начало, чтобы он гарантированно попал в превью на панели
    question_text = f"{marker} — {base_question}"
    
    # Получаем валидную сессионную куку (с умной авторизацией)
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")
    
    if not session_cookie:
        pytest.fail("Не удалось получить валидную сессионную куку")
    
    # Тестируем отправку вопроса
    result = auth_manager.test_question_submission(session_cookie, question_text)

    # Проверяем результат
    assert result["valid"], f"Кука невалидна: {result['message']}"
    assert result["success"], f"Ошибка отправки вопроса: {result['message']}"
    assert result["status_code"] == 200, f"Неожиданный статус код: {result['status_code']}"

    print(f"✅ Успешно отправлен вопрос: {question_text}")

    # Дополнительная проверка: убеждаемся, что отправленный вопрос появился в панели модерации
    print("\n🔍 Проверяем появление вопроса в панели модерации...")
    panel_parser = ModerationPanelParser()

    # Короткая пауза, чтобы запись появилась на странице
    time.sleep(2.0)

    # Ищем отправленный вопрос по уникальному маркеру (устойчиво к обрезанию текста на панели)
    fragment = marker.lower()

    max_attempts = 5
    attempt = 0
    found = False
    while attempt < max_attempts and not found:
        entries = panel_parser.get_moderation_panel_data(session_cookie, limit=100)
        print(f"Найдено {len(entries)} записей в панели модерации (попытка {attempt+1}/{max_attempts})")
        panel_parser.print_table(entries[:5])

        for e in entries:
            if fragment in e.get('text', '').lower():
                found = True
                print("\n✅ Найден отправленный вопрос в панели модерации")
                break

        if not found:
            time.sleep(2.0)
            attempt += 1

    assert found, "Отправленный вопрос не найден в панели модерации"


@allure.title("Параметризованный тест отправки вопросов")
@allure.description("Проверка отправки вопросов разных категорий")
@allure.feature("API тестирование")
@pytest.mark.skip(reason="Отключено: оставляем только один сценарий с маркировкой")
@pytest.mark.parametrize("category", [
    "регистрация",
    "договоры", 
    "процедуры",
    "налоги"
])
def test_send_questions_by_category(category):
    """
    Параметризованный тест отправки вопросов по категориям
    
    Args:
        category: Категория вопроса для тестирования
    """
    
    auth_manager = SmartAuthManager()
    question_factory = QuestionFactory()
    
    # Генерируем вопрос указанной категории
    question_text = question_factory.generate_question(category=category)
    
    # Получаем валидную куку
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")
    
    if not session_cookie:
        pytest.fail("Не удалось получить валидную сессионную куку")
    
    # Тестируем отправку
    result = auth_manager.test_question_submission(session_cookie, question_text)
    
    # Проверяем результат
    assert result["valid"], f"Кука невалидна для категории {category}: {result['message']}"
    assert result["success"], f"Ошибка отправки вопроса категории {category}: {result['message']}"
    
    print(f"✅ Успешно отправлен вопрос категории '{category}': {question_text[:50]}...")


@pytest.mark.skip(reason="Сценарий множественных отправок отключен: проектная политика — отправляем ровно один вопрос и валидируем его появление в панели модерации")
def test_multiple_questions_submission():
    pass


@allure.title("Тест валидности куки без авторизации")
@allure.description("Проверка работы с существующей валидной кукой")
@allure.feature("API тестирование")
@pytest.mark.skip(reason="Отключено: оставляем только один сценарий с маркировкой")
def test_cookie_reuse():
    """
    Тест переиспользования валидной куки
    
    Проверяет, что при наличии валидной куки
    авторизация не выполняется повторно.
    """
    
    auth_manager = SmartAuthManager()
    question_factory = QuestionFactory()
    
    # Первый вызов - может потребовать авторизацию
    print("🔄 Первый вызов get_valid_session_cookie...")
    session_cookie_1 = auth_manager.get_valid_session_cookie(role="admin")
    assert session_cookie_1, "Не удалось получить куку при первом вызове"

    # Отправляем вопрос с первой кукой
    question_text_1 = question_factory.generate_question()
    result_1 = auth_manager.test_question_submission(session_cookie_1, question_text_1)
    assert result_1["valid"], f"Кука 1 невалидна: {result_1['message']}"
    assert result_1["success"], f"Ошибка отправки с кукой 1: {result_1['message']}"

    # Второй вызов - должен возвращать рабочую куку (значение может отличаться)
    print("🔄 Второй вызов get_valid_session_cookie...")
    session_cookie_2 = auth_manager.get_valid_session_cookie(role="admin")
    assert session_cookie_2, "Не удалось получить куку при втором вызове"

    # Отправляем вопрос со второй кукой
    question_text_2 = question_factory.generate_question()
    result_2 = auth_manager.test_question_submission(session_cookie_2, question_text_2)
    assert result_2["valid"], f"Кука 2 невалидна: {result_2['message']}"
    assert result_2["success"], f"Ошибка отправки с кукой 2: {result_2['message']}"

    print("✅ Обе куки рабочие: отправка прошла успешно")


if __name__ == "__main__":
    # Демонстрация возможностей фабрики вопросов
    factory = QuestionFactory()
    
    print("📋 Доступные категории вопросов:")
    for category in factory.get_categories():
        print(f"  - {category}")
    
    print("\n🎲 Примеры уникальных вопросов:")
    for i in range(3):
        question = factory.generate_question()
        print(f"  {i+1}. {question}") 