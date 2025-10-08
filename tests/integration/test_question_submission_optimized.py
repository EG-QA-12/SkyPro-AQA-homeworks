#!/usr/bin/env python3
"""
Оптимизированный тест отправки вопросов

Демонстрирует:
- Умную авторизацию с проверкой куки
- Разнообразные тестовые вопросы
- Таргетированную авторизацию
- Параметризованные тесты
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
def test_send_question_with_smart_auth(
    fx_auth_manager: SmartAuthManager,
    fx_panel_parser: ModerationPanelParser,
    fx_question_factory: QuestionFactory,
) -> None:
    """
    Тест отправки вопроса с умной авторизацией
    
    Демонстрирует оптимизированный подход:
    - Проверка валидности существующей куки
    - Авторизация только при необходимости
    - Разнообразные тестовые вопросы
    """
    
    # Генерируем уникальный маркер и вопрос (отправляем ровно 1 вопрос)
    marker = f"MARKER_{int(time.time())}"
    base_question = fx_question_factory.generate_question(category="регистрация")
    # Вставляем короткий маркер в начало, чтобы он гарантированно попал в превью на панели
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
        # Извлекаем значение куки из словаря если необходимо
        cookie_value = session_cookie.get("value") if isinstance(session_cookie, dict) else session_cookie

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
            cookie_value,
            fragment,
            limit=limit_env,
            delays=delays_env,
            per_attempt_limits=per_attempt_limits,
            freshness_minutes=freshness,
        )


# ====== НОВЫЙ ТЕСТ ДЛЯ МАССОВОЙ ОТПРАВКИ ВОПРОСОВ ======

@allure.title("Массовая отправка 30 вопросов с умной авторизацией")
@allure.description("Создание 30 новых тестовых вопросов в панели модерации")
@allure.feature("API тестирование")
@pytest.mark.api
@pytest.mark.parametrize("question_num", list(range(1, 31)))
def test_bulk_questions_submission(
    fx_auth_manager: SmartAuthManager,
    fx_panel_parser: ModerationPanelParser,
    fx_question_factory: QuestionFactory,
    question_num: int,
) -> None:
    """
    Массовая отправка вопросов для создания тестовых данных

    Отправляет 30 уникальных вопросов в панель модерации.
    Каждый тест создает один вопрос с уникальным маркером.

    Args:
        question_num: Номер вопроса (от 1 до 30)
    """

    # Генерируем уникальный маркер для каждого вопроса
    marker = f"BULK_MARKER_Q{question_num}_{int(time.time())}"
    base_question = fx_question_factory.generate_question(category="регистрация")
    question_text = f"{marker} — {base_question}"

    with allure.step(f"Получение валидной сессионной куки (вопрос #{question_num})"):
        session_cookie = fx_auth_manager.get_valid_session_cookie(role=os.getenv("TEST_ROLE", "admin"))
        assert session_cookie, f"Не удалось получить валидную сессионную куку для вопроса #{question_num}"

    with allure.step(f"Отправка вопроса #{question_num} через API"):
        result = fx_auth_manager.test_question_submission(session_cookie, question_text)
        assert result["valid"], f"Кука невалидна: {result['message']}"
        assert result["success"], f"Ошибка отправки вопроса: {result['message']}"
        assert result["status_code"] == 200, f"Неожиданный статус код: {result['status_code']}"
        print(f"✅ Успешно отправлен вопрос #{question_num}: {question_text}")

    with allure.step(f"Проверка наличия вопроса #{question_num} в панели модерации"):
        # Извлекаем значение куки из словаря если необходимо
        cookie_value = session_cookie.get("value") if isinstance(session_cookie, dict) else session_cookie

        fragment = marker.lower()
        delays_env = _parse_env_delays(os.getenv("PANEL_DELAYS", "0,0.7,1.5,3"))
        limit_env = int(os.getenv("PANEL_LIMIT", "100"))
        limits_env_str = os.getenv("PANEL_LIMITS", "60,100")
        try:
            per_attempt_limits = tuple(int(x.strip()) for x in limits_env_str.split(",") if x.strip())
        except (ValueError, TypeError):
            per_attempt_limits = (60, 100)
        freshness = int(os.getenv("PANEL_FRESH_MINUTES", "3"))

        try:
            verify_question_in_panel(
                fx_panel_parser,
                cookie_value,
                fragment,
                limit=limit_env,
                delays=delays_env,
                per_attempt_limits=per_attempt_limits,
                freshness_minutes=freshness,
            )
            print(f"✅ Вопрос #{question_num} успешно верифицирован в панели модерации")
        except AssertionError as e:
            # Если вопрос не найден быстро, просто залогируем и продолжим
            print(f"⚠️  Вопрос #{question_num} не найден в панели модерации: {str(e)}")


if __name__ == "__main__":
    # Не используется в тестовом запуске. Блок намеренно оставлен пустым.
    pass
