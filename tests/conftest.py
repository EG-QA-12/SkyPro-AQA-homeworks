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


def _is_headless_run() -> bool:
    """Определяем, запускаемся ли мы без UI.

    Проверяем env-переменные, которые обычно выставляют в CI или пользователи
    локально:
     • ``NOTGUI=1``
     • ``HEADLESS=1``
    """
    return os.getenv("NOTGUI") == "1" or os.getenv("HEADLESS") == "1"


@pytest.fixture(autouse=True, scope="session")
def _patch_urls_for_allow_session(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Патчит `Page.goto` и `requests.Session.request` один раз за сессию."""
    if not _is_headless_run():
        yield  # ничего не делаем, пропускаем
        return

    # --- Patch Playwright Page.goto ---------------------------------------
    original_goto = Page.goto  # type: ignore[attr-defined]

    def patched_goto(self: Page, url: str, *args, **kwargs):  # type: ignore[override]
        return original_goto(self, ensure_allow_session_param(url), *args, **kwargs)

    monkeypatch.setattr(Page, "goto", patched_goto, raising=True)

    # --- Patch requests ----------------------------------------------------
    original_request = requests.Session.request  # type: ignore[assignment]

    def patched_request(self: requests.Session, method: str, url: str, *args, **kwargs):  # type: ignore[override]
        return original_request(self, method, ensure_allow_session_param(url), *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", patched_request, raising=True)

    print("🛡️  allow-session=1 параметр будет автоматически подставляться во все URL (headless run).")

    try:
        yield
    finally:
        # При финализации возвращаем методы в исходное состояние
        monkeypatch.setattr(Page, "goto", original_goto, raising=True)
        monkeypatch.setattr(requests.Session, "request", original_request, raising=True)
