#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Интеграционный тест для отправки ответа на вопрос с последующей проверкой.
"""

import pytest
from framework.utils.answer_utils import (
    select_question,
    submit_answer,
    verify_answer_in_admin_panel,
)
from framework.utils.smart_auth_manager import SmartAuthManager

# Определяем سن나рии для параметризации теста
# Каждый кортеж: (ID для теста, Описание)
SELECTION_MODES = [
    ("latest", "Ответить на самый свежий вопрос"),
    ("zero_answers", "Ответить на вопрос без ответов"),
    ("by_author", "Ответить на вопрос пользователя 'Admin'"),
]


@pytest.mark.parametrize(
    "selection_mode, description",
    SELECTION_MODES,
    ids=[mode[0] for mode in SELECTION_MODES],
)
def test_submit_answer_and_verify(selection_mode: str, description: str):
    """
    Выполняет полный цикл: выбор вопроса, ответ и проверка в админ-панели.

    Args:
        selection_mode: Критерий выбора вопроса (latest, zero_answers, by_author).
        description: Человекочитаемое описание тестового случая.
    """
    print(f"\n--- Начало теста: {description} ---")
    auth_manager = SmartAuthManager()

    # --- Arrange (Подготовка) ---

    # 1. Получаем куку эксперта для отправки ответа
    # Примечание: для локального запуска этого теста требуется настроить учетные данные
    # для роли 'expert' (через ENV переменные или в auth_config.json)
    expert_cookie = auth_manager.get_valid_session_cookie(role="expert")
    assert expert_cookie, "Не удалось получить валидную сессионную куку Эксперта"

    # 2. Выбираем вопрос по заданному критерию
    question_data = select_question(selection_mode, expert_cookie)
    assert (
        question_data and "id" in question_data
    ), f"Не удалось найти вопрос по критерию '{selection_mode}'"
    question_id = question_data["id"]
    print(f"Выбран вопрос ID: {question_id} ('{question_data['text'][:50]}...')")

    # --- Act (Действие) ---

    # 3. Отправляем ответ, авторизовавшись под экспертом
    answer_id, submitted_text = submit_answer(
        question_id=question_data["id"], session_cookie=expert_cookie
    )
    assert answer_id is not None, "Не удалось отправить ответ (submit_answer провалился)"

    # --- Assert (Проверка) ---

    # 4. Проверяем наличие ответа в админ-панели под админом
    admin_cookie = auth_manager.get_valid_session_cookie(role="admin")
    assert admin_cookie, "Не удалось получить валидную сессионную куку Администратора для проверки"

    verified = verify_answer_in_admin_panel(
        answer_text=submitted_text, admin_cookie=admin_cookie
    )
    assert verified, "Отправленный ответ не найден в панели модерации или не имеет нужной маркировки"
    print("✅ Проверка в админ-панели прошла успешно.")
    print(f"--- Тест '{description}' завершен успешно ---")

