"""Конфигурация pytest для папки tests.

Содержит специфичные для тестовой папки фикстуры и утилиты.
Базовая конфигурация наследуется из корневого conftest.py.
"""
from __future__ import annotations

from framework.utils.url_utils import ensure_allow_session_param

# Все остальные настройки (sys.path, переменные окружения, http_session) 
# теперь наследуются из корневого conftest.py




