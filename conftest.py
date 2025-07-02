"""Корневой conftest для Pytest.

Добавляет корневую директорию проекта в `sys.path`, чтобы модули из `framework` и
других папок импортировались без дополнительных настроек.

Это решение упрощает импорты — не нужно запоминать, куда добавлять пути,
достаточно просто писать `from framework.utils ...`.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Абсолютный путь до корня репозитория (папка, где расположен этот conftest)
PROJECT_ROOT: Path = Path(__file__).resolve().parent

# Добавляем в sys.path, если ещё не добавлен
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
