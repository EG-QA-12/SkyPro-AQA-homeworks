"""
Пакет Page Objects для фреймворка автоматизации.

Этот пакет содержит все Page Object Models (POM) для различных страниц приложения.
Page Objects помогают инкапсулировать логику работы с элементами страниц.

Modules:
    login_page: Page Object для страницы входа в систему
"""

from .login_page import LoginPage

__all__ = ['LoginPage']
