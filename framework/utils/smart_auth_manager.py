#!/usr/bin/env python3
"""
SmartAuthManager - РАБОЧАЯ ВЕРСИЯ ПРОБНОГО ПОДХОДА

Теперь используется как РАБОЧИЙ ФАЙЛ с новой архитектурой!
smart_auth_api_approach.py - вспомогательный файл с реализациями.

ОБРАТНАЯ СОВМЕСТИМОСТЬ: Все существующие UI тесты продолжают работать
через этот файл, а он делегирует вызовы новому подходу.
"""

import time
import asyncio
import logging
from typing import Optional, Dict, List
from pathlib import Path

from framework.utils.smart_auth_api_approach import SmartAuthManager as SmartAuthAPIApproach

logger = logging.getLogger(__name__)

class SmartAuthManager(SmartAuthAPIApproach):
    """
    SmartAuthManager - РАБОЧАЯ ВЕРСИЯ для UI и API тестов

    Наследуется от SmartAuthAPIApproach и делегирует все вызовы ему.
    Этот файл остается основным для импортов в тестах.
    """

    def __init__(self):
        """Инициализация через наследование"""
        super().__init__()

# ПЕРЕНАПРАВИТЬ ВСЕ ВЫЗОВЫ НА НОВУЮ РЕАЛИЗАЦИЮ
# Этот класс просто наследуется, чтобы сохранить обратную совместимость
