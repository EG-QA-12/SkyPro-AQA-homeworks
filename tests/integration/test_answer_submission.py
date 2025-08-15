#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Интеграционный тест для отправки ответа на вопрос.

Сценарий E2E:
1. Авторизация под ролью 'expert'.
2. Выбор вопроса для ответа по одному из критериев:
   - 'latest': самый свежий вопрос.
   - 'zero_answers': самый свежий вопрос без ответов.
   - 'by_author': самый свежий вопрос от указанного автора.
3. Отправка POST-запроса с текстом ответа.
4. Авторизация под ролью 'admin'.
5. Проверка появления отправленного ответа в панели модерации со статусом 'П'.

Особенности:
- **Отказоустойчивость:** Встроен механизм повторной отправки ответа с
  автоматической реавторизацией при получении статуса 401/419.
- **Параметризация:** Тест параметризован как по критериям выбора,
  так и по количеству отправок.

## Использование параметризации для массовой отправки

Этот тест можно запускать для отправки нескольких ответов, используя
переменную окружения `NUM_ANSWERS_TO_SUBMIT`.

**Примеры запуска:**

*   **Отправить по 1 ответу для каждого из 3-х сценариев (всего 3 тест-кейса):**
    ```bash
    python -m pytest tests/integration/test_answer_submission.py
    ```

*   **Отправить по 5 ответов для каждого сценария (всего 15 тест-кейсов):**
    ```bash
    NUM_ANSWERS_TO_SUBMIT=5 python -m pytest tests/integration/test_answer_submission.py
    ```
"""

import pytest
import os
import allure
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


def _get_num_answers_env() -> int:
    """Возвращает количество ответов для отправки из ENV NUM_ANSWERS_TO_SUBMIT."""
    try:
        value = int(os.getenv("NUM_ANSWERS_TO_SUBMIT", "1").strip())
        return value if value > 0 else 1
    except (ValueError, TypeError):
        return 1

@allure.title("Отправка ответа на вопрос и его проверка")
@allure.description(
    "Тест выполняет полный E2E сценарий: авторизация, выбор вопроса по критерию, "
    "отправка ответа и проверка его появления в панели модерации с корректным статусом."
)
@allure.feature("API Тестирование")
@pytest.mark.api
@pytest.mark.parametrize("run_index", range(_get_num_answers_env()))
@pytest.mark.parametrize(
    "selection_mode, description",
    SELECTION_MODES,
    ids=[mode[0] for mode in SELECTION_MODES],
)
def test_submit_answer_and_verify(selection_mode: str, description: str, run_index: int):
    """
    Выполняет полный цикл: выбор вопроса, ответ и проверка в админ-панели.

    Args:
        selection_mode: Критерий выбора вопроса (latest, zero_answers, by_author).
        description: Человекочитаемое описание тестового случая.
        run_index: Индекс итерации для массового запуска.
    """
    # Динамически изменяем title в Allure для наглядности
    allure.dynamic.title(f"{description} (Запуск #{run_index + 1})")

    print(f"\n--- Начало теста: {description} (Запуск #{run_index + 1}) ---")
    auth_manager = SmartAuthManager()

    # --- Arrange (Подготовка) ---

    # 1. Получаем куку эксперта для отправки ответа
    # Примечание: для локального запуска этого теста требуется настроить учетные данные
    # для роли 'expert' (через ENV переменные или в auth_config.json)
    # ВРЕМЕННОЕ РЕШЕНИЕ: Используем 'admin', чтобы проверить логику теста.
    # TODO: Вернуть 'expert' после настройки локальных учетных данных.
    current_role = "admin"
    expert_cookie = auth_manager.get_valid_session_cookie(role=current_role)
    assert expert_cookie, f"Не удалось получить валидную сессионную куку для роли '{current_role}'"

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
        question_id=question_data["id"], session_cookie=expert_cookie, role=current_role
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

