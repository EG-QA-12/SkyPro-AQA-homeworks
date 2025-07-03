"""
Пакет utils содержит вспомогательные модули для работы с cookies, URL, авторизацией и вспомогательными функциями для тестов.

Используйте эти утилиты для повышения читаемости, повторного использования и стандартизации кода тестов.

Этот модуль содержит:
- auth_utils: Функции для работы с авторизацией и куками
- allure_utils: Интеграция с Allure для создания подробных отчетов  
- secure_auth_utils: Безопасная работа с авторизационными данными
- cookie_constants: Константы для работы с куками

Рекомендации по использованию:
Используйте эти утилиты вместо написания собственного кода для типовых задач.
Все функции содержат подробную документацию и примеры использования.
Модули организованы по принципу единой ответственности для удобства сопровождения.
"""

from .auth_utils import save_cookie, load_cookie
from .reporting.allure_utils import AllureReporter, allure_test_case, smoke_test, regression_test
from .secure_auth_utils import SecureAuthManager  # auth_manager исключен чтобы избежать проблем инициализации
from .cookie_constants import COOKIE_NAME, joint_cookie
from .cookie_helper import get_cookie_files, parse_auth_cookie

__all__ = [
    # Авторизация
    'save_cookie',
    'load_cookie',
    'SecureAuthManager',
    
    # Allure отчеты
    'AllureReporter',
    'allure_test_case',
    'smoke_test',
    'regression_test',
    
    # Константы
    'COOKIE_NAME',
    'joint_cookie',
    'get_cookie_files',
    'parse_auth_cookie'
]
