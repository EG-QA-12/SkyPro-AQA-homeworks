#!/usr/bin/env python3
"""
Оптимизированный тест отправки вопросов

Демонстрирует:
- Умную авторизацию с проверкой куки
- Разнообразные тестовые вопросы
- Таргетированную авторизацию
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
        "--------------------------------------------------------------------------------------------",
    ]
    for e in head:
        lines.append(
            f"{e.get('user',''):<15}  {e.get('date',''):<16}  {e.get('type',' '):^3}  "
            f"{(e.get('text','') or '')[:40]:<40}  {e.get('id') or ''}"
        )
    return "\n".join(lines)


def verify_question_in_panel(
    panel_parser: ModerationPanelParser,
    session_cookie: str,
    fragment: str,
    *,
    limit: int = 100,
    delays: Tuple[float, ...] = (0.0, 0.7, 1.5, 3.0),
    freshness_minutes: int = 3,
) -> Dict[str, Any]:
    """Проверяет наличие записи с указанным фрагментом текста в панели модерации."""
    from datetime import datetime, timedelta, timezone

    last_entries: List[Dict[str, Any]] = []
    for attempt, delay in enumerate(delays, start=1):
        if delay > 0:
            time.sleep(delay)

        entries = panel_parser.get_moderation_panel_data(session_cookie, limit=limit)
        last_entries = entries
        print(
            f"Попытка {attempt}/{len(delays)}: Найдено {len(entries)} записей (limit={limit}, задержка {delay:.1f}с)"
        )

        for e in entries:
            text_value = (e.get("text", "") or "").lower()
            if fragment in text_value:
                if e.get("type") != "?":
                    continue  # Ищем только неопубликованные вопросы

                ts = e.get("timestamp")
                if not ts:
                    continue

                entry_dt_utc = datetime.fromtimestamp(float(ts), tz=timezone.utc)
                if datetime.now(timezone.utc) - entry_dt_utc > timedelta(minutes=freshness_minutes):
                    continue  # Запись слишком старая

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

    allure.attach(
        _format_table(last_entries, limit=10),
        name="Панель: последние 10 записей (финальная диагностика)",
        attachment_type=allure.attachment_type.TEXT,
    )
    pytest.fail(f"Отправленный вопрос с маркером '{fragment}' не найден в панели модерации.")


@allure.title("Отправка вопроса с умной авторизацией")
@allure.description("Проверка отправки вопроса с оптимизированной авторизацией")
@allure.feature("API тестирование")
@pytest.mark.api
@pytest.mark.parametrize(
    "case_index",
    range(_get_num_questions_env()),
    ids=lambda i: f"question_{i+1}"
)
def test_send_question_with_smart_auth(
    fx_auth_manager: SmartAuthManager,
    fx_panel_parser: ModerationPanelParser,
    fx_question_factory: QuestionFactory,
    case_index: int,
) -> None:
    """
    Тест отправки вопроса с умной авторизацией.
    """
    marker = f"MARKER_{int(time.time())}_{case_index}"
    base_question = fx_question_factory.generate_question(category="регистрация")
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
        delays = _parse_env_delays(os.getenv("PANEL_DELAYS", "0,1,3,5")) # Увеличенные задержки
        verify_question_in_panel(
            fx_panel_parser,
            session_cookie,
            fragment,
            delays=delays,
        )

if __name__ == "__main__":
    pytest.main([__file__, '-s', '-v'])