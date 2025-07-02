"""
Общий фреймворк автоматизации тестирования.

Этот пакет содержит переиспользуемые компоненты для всех тестовых проектов:
- utils: Общие утилиты (авторизация, отчеты, вспомогательные функции)
- fixtures: Переиспользуемые pytest фикстуры
- app: Специфичный код приложения и page objects

Преимущества использования:
Этот фреймворк позволяет писать тесты быстрее, используя готовые компоненты.
Не нужно каждый раз писать код авторизации или настройки браузера заново.
Все модули содержат подробную документацию и примеры использования.
"""

__version__ = "1.0.0"
__author__ = "Lead SDET Architect"

# Импорты для удобства использования (опциональны)
try:
    from .utils.auth_utils import save_cookie, load_cookie
    from .utils.reporting.allure_utils import AllureReporter, allure_test_case
except (ModuleNotFoundError, ValueError):
    # Не устанавливаем тяжёлые зависимости, если они не нужны (playwright и т.д.)
    # ValueError может возникнуть при отсутствии переменных окружения
    save_cookie = load_cookie = None  # type: ignore
    AllureReporter = allure_test_case = None  # type: ignore


__all__ = [
    'save_cookie',
    'load_cookie', 
    'AllureReporter',
    'allure_test_case'
]
