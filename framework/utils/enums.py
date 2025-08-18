#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Этот модуль содержит перечисления (Enums), используемые в тестах.

Использование Enum вместо "магических" строковых или числовых литералов
повышает читаемость кода, упрощает рефакторинг и предотвращает ошибки,
связанные с опечатками.
"""

from enum import Enum


class AnswerPublicationType(Enum):
    """
    Определяет типы ответов при публикации через панель администратора.
    Значения соответствуют `post_type_id` в POST-запросе.
    """
    ANSWER = 3
    SUPPORTIVE = 4
    OTHER = 5
    MAXIMUM = 6
    PUBLISHED = 3
    DRAFT = 4
    REJECTED = 5

    def __str__(self):
        """Возвращает имя члена Enum, например 'ANSWER'."""
        return self.name


class QuestionStatus(Enum):
    """
    Определяет статусы вопросов.
    """
    PENDING = 1
    APPROVED = 2
    PUBLISHED = 3
    REJECTED = 4
    ARCHIVED = 5

    def __str__(self):
        """Возвращает имя члена Enum."""
        return self.name


class UserRole(Enum):
    """
    Определяет роли пользователей в системе.
    """
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

    def __str__(self):
        """Возвращает имя члена Enum."""
        return self.name
