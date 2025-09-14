"""
Пакет fixtures для фреймворка автоматизации.

Этот пакет содержит готовые fixtures для pytest, которые упрощают
написание тестов и устраняют повторяющийся код.

Modules:
    auth_fixtures: Fixtures для авторизации и управления cookies
"""

from .auth_fixtures import (
    browser_context,
    clean_context, 
    authenticated_admin,
    authenticated_user,
    auth_page,
    quick_auth,
    isolated_context
)

__all__ = [
    'browser_context',
    'clean_context',
    'authenticated_admin', 
    'authenticated_user',
    'auth_page',
    'quick_auth',
    'isolated_context'
]
