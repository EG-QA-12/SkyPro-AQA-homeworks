"""
Глобальные фикстуры для End-to-End тестов.

Этот модуль содержит:
- Настройки браузеров для E2E тестирования.
- Заглушки для авторизационных фикстур.
- Маркеры для категоризации тестов.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

# Добавляем корневую директорию проекта в sys.path для импорта `framework`
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """
    Фикстура для передачи кастомных аргументов в контекст браузера.
    Добавляет User-Agent для headless режима.
    """
    force_headed = os.getenv("FORCE_HEADED") == "1"
    is_headless = False if force_headed else (os.getenv("HEADLESS", "1").lower() in ("1", "true", "yes", "on"))

    args = {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "ru-RU",
        "timezone_id": "Europe/Minsk",
        "permissions": ["geolocation"],
        "record_video_dir": "test-results/videos/",
        "record_har_path": "test-results/network.har",
    }

    if is_headless:
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
        args["user_agent"] = user_agent
        print(f"\n🚀 Запуск в headless-режиме с User-Agent: {user_agent}")

    return args


@pytest.fixture(scope="function")
def authenticated_context_admin(
    browser: Browser,
) -> Generator[BrowserContext, None, None]:
    """Браузерный контекст с авторизацией под администратором (заглушка)."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080}, locale="ru-RU"
    )
    # TODO: Реализовать загрузку сохраненных куки администратора
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def authenticated_context_moderator(
    browser: Browser,
) -> Generator[BrowserContext, None, None]:
    """Браузерный контекст с авторизацией под модератором (заглушка)."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080}, locale="ru-RU"
    )
    # TODO: Реализовать загрузку сохраненных куки модератора
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def authenticated_page_admin(
    authenticated_context_admin: BrowserContext,
) -> Generator[Page, None, None]:
    """Страница с авторизацией под администратором (заглушка)."""
    page = authenticated_context_admin.new_page()
    try:
        yield page
    finally:
        page.close()


@pytest.fixture(scope="function")
def authenticated_page_moderator(
    authenticated_context_moderator: BrowserContext,
) -> Generator[Page, None, None]:
    """Страница с авторизацией под модератором (заглушка)."""
    page = authenticated_context_moderator.new_page()
    try:
        yield page
    finally:
        page.close()


# Маркеры для категоризации тестов
pytest.mark.smoke = pytest.mark.smoke
pytest.mark.regression = pytest.mark.regression
pytest.mark.user_journey = pytest.mark.user_journey
pytest.mark.admin_workflow = pytest.mark.admin_workflow
pytest.mark.cross_browser = pytest.mark.cross_browser
pytest.mark.mobile = pytest.mark.mobile
pytest.mark.slow = pytest.mark.slow
pytest.mark.critical = pytest.mark.critical

# ---------------------------------------------------------------------------
# Патчинг URL для `allow-session=1` теперь в корневом tests/conftest.py
# и применяется глобально. Удалено из этого файла во избежание дублирования.
# ---------------------------------------------------------------------------
