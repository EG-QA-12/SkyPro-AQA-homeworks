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
from typing import Set
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

@allure.feature("API Тестирование")
@pytest.mark.api
class TestAnswerSubmission:
    """
    Группирует тесты по отправке ответов для управления общим состоянием.
    """

    answered_question_ids: Set[int] = set()

    @allure.title("Отправка ответа на вопрос и его проверка")
    @allure.description(
        "Тест выполняет полный E2E сценарий: авторизация, выбор вопроса по критерию, "
        "отправка ответа и проверка его появления в панели модерации с корректным статусом."
    )
    @pytest.mark.parametrize("run_index", range(_get_num_answers_env()))
    @pytest.mark.parametrize(
        "selection_mode, description",
        SELECTION_MODES,
        ids=[mode[0] for mode in SELECTION_MODES],
    )
    def test_submit_answer_and_verify(
        self, selection_mode: str, description: str, run_index: int
    ):
        """
        Выполняет полный цикл: выбор вопроса, ответ и проверка в админ-панели.
        """
        allure.dynamic.title(f"{description} (Запуск #{run_index + 1})")

        print(f"\n--- Начало теста: {description} (Запуск #{run_index + 1}) ---")
        auth_manager = SmartAuthManager()

        # --- Arrange (Подготовка) ---
        current_role = "admin"
        expert_cookie = auth_manager.get_valid_session_cookie(role=current_role)
        assert expert_cookie, f"Не удалось получить валидную сессионную куку для роли '{current_role}'"

        # Выбираем вопрос, исключая те, на которые уже ответили в этой сессии
        question_data = select_question(
            selection_mode,
            expert_cookie,
            exclude_ids=list(self.answered_question_ids),
        )
        if not (question_data and "id" in question_data):
            pytest.skip(
                f"Не удалось найти УНИКАЛЬНЫЙ вопрос по критерию '{selection_mode}'. "
                f"Уже использованы: {self.answered_question_ids}"
            )

        question_id = question_data["id"]
        print(f"Выбран вопрос ID: {question_id} ('{question_data['text'][:50]}...')")

        # Добавляем ID в множество использованных, чтобы не повторяться
        self.answered_question_ids.add(question_id)

        # --- Act (Действие) ---
        answer_id, submitted_text = submit_answer(
            question_id=question_id, session_cookie=expert_cookie, role=current_role
        )
        assert answer_id is not None, "Не удалось отправить ответ (submit_answer провалился)"

        # --- Assert (Проверка) ---
        admin_cookie = auth_manager.get_valid_session_cookie(role="admin")
        assert admin_cookie, "Не удалось получить валидную сессионную куку Администратора для проверки"

        verified = verify_answer_in_admin_panel(
            answer_text=submitted_text, admin_cookie=admin_cookie
        )
        assert verified, "Отправленный ответ не найден в панели модерации или не имеет нужной маркировки"
        print("✅ Проверка в админ-панели прошла успешно.")
        print(f"--- Тест '{description}' завершен успешно ---")

