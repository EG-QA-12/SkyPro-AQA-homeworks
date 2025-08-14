#!/usr/bin/env python3
"""
Оптимизированный тест отправки вопросов

Демонстрирует:
- Умную авторизацию с проверкой куки
- Разнообразные тестовые вопросы
- Таргетированную авторизацию
- **Параметризованная отправка N вопросов**

## Использование параметризации

Этот тест можно запускать для отправки нескольких вопросов, используя параметризацию Pytest.
Количество отправляемых вопросов контролируется переменной окружения `NUM_QUESTIONS`.

**Примеры запуска:**

*   **Отправить 1 вопрос (по умолчанию):**
    ```bash
    python -m pytest tests/integration/test_question_submission_optimized.py -v -s
    ```

*   **Отправить 5 вопросов:**
    ```bash
    NUM_QUESTIONS=5 python -m pytest tests/integration/test_question_submission_optimized.py -v -s
    ```

*   **Отправить 10 вопросов:**
    ```bash
    NUM_QUESTIONS=10 python -m pytest tests/integration/test_question_submission_optimized.py -v -s
    ```

**Отчетность Allure:**
Каждый отправленный вопрос будет отображаться как отдельный тестовый кейс в отчете Allure, 
что обеспечивает высокую детализацию и упрощает отладку.
"""

import os
import time
from typing import Any, Dict, List, Tuple

import allure
import pytest

from framework.utils.html_parser import ModerationPanelParser
from framework.utils.question_factory import QuestionFactory
from framework.utils.smart_auth_manager import SmartAuthManager


@pytest.fixture
def fx_auth_manager() -> SmartAuthManager:
    """Инициализирует менеджер умной авторизации.

    Returns:
        SmartAuthManager: Экземпляр менеджера авторизации.
    """
    return SmartAuthManager()


@pytest.fixture
def fx_panel_parser() -> ModerationPanelParser:
    """Инициализирует парсер панели модерации.

    Returns:
        ModerationPanelParser: Экземпляр парсера панели модерации.
    """
    return ModerationPanelParser()


@pytest.fixture
def fx_question_factory() -> QuestionFactory:
    """Инициализирует фабрику генерации вопросов.

    Returns:
        QuestionFactory: Экземпляр фабрики вопросов.
    """
    return QuestionFactory()


def _parse_env_delays(value: str) -> Tuple[float, ...]:
    """Преобразует строку задержек из переменной окружения в кортеж чисел.

    Args:
        value: Строка вида "0,1,2,4".

    Returns:
        Tuple[float, ...]: Кортеж задержек в секундах.
    """
    try:
        parts = [p.strip() for p in value.split(",") if p.strip()]
        return tuple(float(p) for p in parts)
    except (ValueError, TypeError):
        return (0.0, 1.0, 2.0, 4.0)


def _get_num_questions_env() -> int:
    """Возвращает количество вопросов для отправки из ENV NUM_QUESTIONS.

    По умолчанию возвращает 1. Некорректные значения приводятся к 1.

    Returns:
        int: Количество вопросов для параметризации теста.
    """
    try:
        value = int(os.getenv("NUM_QUESTIONS", "1").strip())
        return value if value > 0 else 1
    except Exception:
        return 1


def _format_table(entries: List[Dict[str, Any]], limit: int = 5) -> str:
    """Формирует текстовую таблицу для отображения в логах/Allure.

    Args:
        entries: Список записей панели модерации.
        limit: Максимальное число строк для отображения.

    Returns:
        str: Текстовая таблица.
    """
    head = entries[: max(0, limit)]
    lines = [
        "Пользователь            Дата            Тип     Текст           ID",
        "-" * 92,
    ]
    for e in head:
        lines.append(
            f"{e.get('user',''):15}  {e.get('date',''):16}  {e.get('type',' '):^3}  "
            f"{(e.get('text','') or '')[:40]:40}  {e.get('id') or ''}"
        )
    return "\n".join(lines)


def verify_question_in_panel(
    panel_parser: ModerationPanelParser,
    session_cookie: str,
    fragment: str,
    *,
    limit: int = 100,
    delays: Tuple[float, ...] = (0.0, 0.7, 1.5, 3.0),
    per_attempt_limits: Tuple[int, ...] | None = None,
    freshness_minutes: int = 3,
) -> Dict[str, Any]:
    """Проверяет наличие записи с указанным фрагментом текста в панели модерации.

    В несколько попыток опрашивает панель, возвращает найденную запись или
    падает с диагностикой.

    Args:
        panel_parser: Парсер панели модерации.
        session_cookie: Значение куки сессии.
        fragment: Фрагмент текста для поиска (нижний регистр).
        limit: Количество записей, запрашиваемых у панели.
        delays: Задержки между попытками, первая попытка — сразу.
        freshness_minutes: Максимально допустимый возраст записи в минутах.

    Returns:
        Dict[str, Any]: Найденная запись панели модерации.
    """
    from datetime import datetime, timedelta, timezone

    max_attempts = len(delays)
    last_entries: List[Dict[str, Any]] = []

    for attempt, delay in enumerate(delays, start=1):
        if delay > 0:
            time.sleep(delay)

        # Динамический лимит: сперва меньше, затем больше
        effective_limit = limit
        if per_attempt_limits and len(per_attempt_limits) > 0:
            idx = min(attempt - 1, len(per_attempt_limits) - 1)
            effective_limit = per_attempt_limits[idx]

        entries = panel_parser.get_moderation_panel_data(session_cookie, limit=effective_limit)
        last_entries = entries
        print(
            f"Найдено {len(entries)} записей (limit={effective_limit}) (попытка {attempt}/{max_attempts}, задержка {delay:.1f}с)"
        )
        # Минимизируем оверхед: вложения только при успехе/провале

        for e in entries:
            text_value = (e.get("text", "") or "").lower()
            if fragment in text_value:
                # Проверка типа и свежести
                if e.get("type") != "?":
                    raise AssertionError("Неверный тип записи (ожидался '?')")

                ts = e.get("timestamp")
                if not ts:
                    raise AssertionError("У найденной записи отсутствует timestamp")

                entry_dt_utc = datetime.fromtimestamp(float(ts), tz=timezone.utc)
                if datetime.now(timezone.utc) - entry_dt_utc > timedelta(minutes=freshness_minutes):
                    raise AssertionError("Найдена не свежая запись — возможное ложное совпадение по маркеру")

                # Диагностика найденной записи
                details = (
                    f"Пользователь: {e.get('user')}\n"
                    f"Дата: {e.get('date')}\n"
                    f"Тип: {e.get('type')}\n"
                    f"Текст: {e.get('text')}\n"
                    f"ID: {e.get('id') or 'Н/Д'}\n"
                )
                allure.attach(details, name="Найденная запись", attachment_type=allure.attachment_type.TEXT)
                print("\n✅ Найден отправленный вопрос в панели модерации")
                print("\n🔍 Детали вопроса:\n" + details)
                return e

    # Не нашли — финальная диагностика
    allure.attach(
        _format_table(last_entries, limit=5),
        name="Панель: первые 5 записей (финальная диагностика)",
        attachment_type=allure.attachment_type.TEXT,
    )
    raise AssertionError("Отправленный вопрос не найден в панели модерации")


@allure.title("Отправка вопроса с умной авторизацией")
@allure.description("Проверка отправки вопроса с оптимизированной авторизацией")
@allure.feature("API тестирование")
@pytest.mark.api
@pytest.mark.parametrize(
    "case_index",
    tuple(range(_get_num_questions_env())),
    ids=lambda i: f"send_q_{int(i)+1}",
)
def test_send_question_with_smart_auth(
    fx_auth_manager: SmartAuthManager,
    fx_panel_parser: ModerationPanelParser,
    fx_question_factory: QuestionFactory,
    case_index: int,
) -> None:
    """
    Тест отправки вопроса с умной авторизацией
    
    Демонстрирует оптимизированный подход:
    - Проверка валидности существующей куки
    - Авторизация только при необходимости
    - Разнообразные тестовые вопросы
    """
    
    # Генерируем уникальный маркер и вопрос для данного кейса
    marker = f"MARKER_{int(time.time())}_{case_index}"
    base_question = fx_question_factory.generate_question(category="регистрация")
    # Вставляем маркер в начало, чтобы он гарантированно попал в превью на панели
    question_text = f"{marker} — {base_question}"
    
    with allure.step("Получение валидной сессионной куки (умная авторизация)"):
        session_cookie = fx_auth_manager.get_valid_session_cookie(role=os.getenv("TEST_ROLE", "admin"))
        assert session_cookie, "Не удалось получить валидную сессионную куку"

    with allure.step("Отправка вопроса через API"):
        result = fx_auth_manager.test_question_submission(session_cookie, question_text)
        assert result["valid"], f"Кука невалидна: {result['message']}"
        assert result["success"], f"Ошибка отправки вопроса: {result['message']}"
        assert result["status_code"] == 200, f"Неожиданный статус код: {result['status_code']}"
        print(f"✅ Успешно отправлен вопрос: {question_text}")

    with allure.step("Проверка наличия вопроса в панели модерации"):
        fragment = marker.lower()
        delays_env = _parse_env_delays(os.getenv("PANEL_DELAYS", "0,0.7,1.5,3"))
        limit_env = int(os.getenv("PANEL_LIMIT", "100"))
        limits_env_str = os.getenv("PANEL_LIMITS", "60,100")
        try:
            per_attempt_limits = tuple(int(x.strip()) for x in limits_env_str.split(",") if x.strip())
        except (ValueError, TypeError):
            per_attempt_limits = (60, 100)
        freshness = int(os.getenv("PANEL_FRESH_MINUTES", "3"))
        verify_question_in_panel(
            fx_panel_parser,
            session_cookie,
            fragment,
            limit=limit_env,
            delays=delays_env,
            per_attempt_limits=per_attempt_limits,
            freshness_minutes=freshness,
        )


# Удалены вспомогательные сценарии: оставляем один быстрый и показательный тест


if __name__ == "__main__":
    # Не используется в тестовом запуске. Блок намеренно оставлен пустым.
    pass