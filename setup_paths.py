"""
Настройка путей для корректной работы импортов в проекте.

Этот файл должен быть импортирован в самом начале тестовых скриптов.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))
