# __init__.py
"""
Пакет тестов для проверки функциональности burger menu
"""

from test_utils import (
    Config,
    RequestHandler,
    Auth,
    setup_logging,
    generate_random_text,
    FolderUtils,
    ScreenshotManager
)

__version__ = '1.0.0'
__author__ = 'Evgeny Gusinets'

# Экспортируемые компоненты
__all__ = [
    'Config',
    'RequestHandler',
    'Auth',
    'setup_logging',
    'generate_random_text'
]

# Дополнительные константы или настройки пакета
DEFAULT_TIMEOUT = 10000  # миллисекунды
DEBUG_MODE = False