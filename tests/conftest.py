"""Root-level Pytest configuration.

Добавляет параметр ``allow-session=1`` ко всем HTTP/Playwright запросам
в без-GUI (headless) сборках, чтобы бэкенд не считал нас ботом.  Логика
вынесена на корневой уровень, чтобы применяться ко *всем* подпапкам
(`tests/e2e`, `tests/integration`, etc.).
"""
from __future__ import annotations

import os
from typing import Generator

import pytest
import requests
from playwright.sync_api import Page

from framework.utils.url_utils import ensure_allow_session_param
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из secrets/
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / "secrets" / ".env", override=False)
load_dotenv(project_root / "secrets" / "creds.env", override=True)


def _is_headless_run() -> bool:
    """
    Определяет, должен ли браузер работать в headless-режиме.

    Алгоритм:
    1. Если выставлена переменная ``FORCE_HEADED=1`` — всегда GUI.
    2. Иначе учитываем переменную ``HEADLESS`` (по умолчанию «1»/True).
    3. Для обратной совместимости поддерживаем устаревшую ``NOTGUI``.
    """
    if os.getenv("FORCE_HEADED") == "1":
        return False
    if os.getenv("NOTGUI") == "1":
        return True
    return os.getenv("HEADLESS", "1").lower() in ("1", "true", "yes", "on")


@pytest.fixture(autouse=True, scope="session")
def _patch_urls_for_allow_session() -> Generator[None, None, None]:
    """Патчит `Page.goto` и `requests.Session.request` один раз за сессию."""
    if not _is_headless_run():
        yield  # ничего не делаем, пропускаем
        return

    from pytest import MonkeyPatch
    mp = MonkeyPatch()

    # --- Patch Playwright Page.goto ---------------------------------------
    original_goto = Page.goto  # type: ignore[attr-defined]
    def patched_goto(self: Page, url: str, *args, **kwargs):  # type: ignore[override]
        return original_goto(self, ensure_allow_session_param(url), *args, **kwargs)
    mp.setattr(Page, "goto", patched_goto, raising=True)

    # --- Patch requests ----------------------------------------------------
    original_request = requests.Session.request  # type: ignore[assignment]
    def patched_request(self: requests.Session, method: str, url: str, *args, **kwargs):  # type: ignore[override]
        return original_request(self, method, ensure_allow_session_param(url), *args, **kwargs)
    mp.setattr(requests.Session, "request", patched_request, raising=True)

    print(
        "🛡️  allow-session=1 параметр будет автоматически подставляться во все URL "
        "(headless run)."
    )
    try:
        yield
    finally:
        mp.undo()

