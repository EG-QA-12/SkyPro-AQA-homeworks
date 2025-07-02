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




