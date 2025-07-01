"""
Общий фреймворк автоматизации тестирования.

Этот пакет содержит переиспользуемые компоненты для всех тестовых проектов:
- utils: Общие утилиты (авторизация, отчеты, вспомогательные функции)
- fixtures: Переиспользуемые pytest фикстуры
- app: Специфичный код приложения и page objects

Для Junior QA-инженеров:
Этот фреймворк позволяет писать тесты быстрее, используя готовые компоненты.
Не нужно каждый раз писать код авторизации или настройки браузера заново.
"""

__version__ = "1.0.0"
__author__ = "Lead SDET Architect"

# Импорты для удобства использования
from .utils.auth_utils import save_cookie, load_cookie
from .utils.allure_utils import AllureReporter, allure_test_case

__all__ = [
    'save_cookie',
    'load_cookie', 
    'AllureReporter',
    'allure_test_case'
]
