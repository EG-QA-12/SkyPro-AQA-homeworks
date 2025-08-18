"""
Конфигурационный файл для новых фикстур фреймворка.

Этот файл автоматически импортирует все фикстуры из новых модулей,
обеспечивая их доступность в тестах.
"""

# Импортируем все фикстуры из модулей фреймворка
from .auth_fixtures import *
from .moderation_fixtures import *

# Дополнительная конфигурация pytest

import pytest
import logging
from typing import Any

# Настройка логирования для тестов
logger = logging.getLogger(__name__)


def pytest_configure(config):
    """Конфигурация pytest при запуске."""
    # Добавляем пользовательские маркеры
    config.addinivalue_line(
        "markers", "api: тесты API"
    )
    config.addinivalue_line(
        "markers", "moderation: тесты модерации"
    )
    config.addinivalue_line(
        "markers", "auth: тесты авторизации"
    )
    config.addinivalue_line(
        "markers", "smoke: smoke тесты"
    )
    config.addinivalue_line(
        "markers", "regression: регрессионные тесты"
    )
    
    logger.info("Новый фреймворк фикстур сконфигурирован")


def pytest_collection_modifyitems(config, items):
    """Модификация коллекции тестов."""
    for item in items:
        # Автоматически добавляем маркер api для тестов в новых модулях
        if "test_new_framework_example" in item.nodeid:
            item.add_marker("api")
            item.add_marker("regression")


# Хуки для отладки и диагностики

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для создания отчетов о выполнении тестов."""
    outcome = yield
    rep = outcome.get_result()
    
    # Добавляем информацию о статусе теста
    if rep.when == "call":
        if rep.passed:
            logger.debug(f"✅ Тест прошел: {item.nodeid}")
        elif rep.failed:
            logger.error(f"❌ Тест упал: {item.nodeid}")
            logger.error(f"   Ошибка: {call.excinfo}" if call.excinfo else "")
        elif rep.skipped:
            logger.warning(f"⚠️  Тест пропущен: {item.nodeid}")


# Параметризованные фикстуры для удобства

@pytest.fixture(params=["admin", "user", "moderator"])
def all_roles_client(request):
    """
    Параметризованная фикстура для тестирования всех ролей.
    
    Args:
        request: Объект запроса pytest
        
    Returns:
        AdminAPIClient: Клиент для соответствующей роли
    """
    from framework.api.admin_client import AdminAPIClient
    client = AdminAPIClient(role=request.param)
    yield client
    client.close()


@pytest.fixture
def test_data_generator():
    """
    Фикстура для генерации тестовых данных.
    
    Returns:
        callable: Функция для генерации тестовых данных
    """
    from framework.utils.question_factory import QuestionFactory
    
    def _generate_data(count: int = 5, category: str = None):
        factory = QuestionFactory()
        return factory.generate_multiple_questions(count=count, category=category)
    
    return _generate_data


# Утилиты для работы с тестами

class TestContextManager:
    """
    Менеджер контекста для тестов.
    
    Предоставляет удобные методы для управления контекстом тестов
    и сбора метрик выполнения.
    """
    
    def __init__(self):
        self.test_metrics = {}
    
    def start_test(self, test_name: str):
        """Начало выполнения теста."""
        import time
        self.test_metrics[test_name] = {
            'start_time': time.time(),
            'status': 'running'
        }
        logger.info(f"🚀 Начало теста: {test_name}")
    
    def end_test(self, test_name: str, success: bool = True, error: str = None):
        """Завершение выполнения теста."""
        import time
        if test_name in self.test_metrics:
            self.test_metrics[test_name].update({
                'end_time': time.time(),
                'duration': time.time() - self.test_metrics[test_name]['start_time'],
                'status': 'passed' if success else 'failed',
                'error': error
            })
        logger.info(f"{'✅' if success else '❌'} Завершение теста: {test_name}")


@pytest.fixture(scope="session")
def test_context_manager():
    """
    Фикстура для получения менеджера контекста тестов.
    
    Returns:
        TestContextManager: Менеджер контекста тестов
    """
    return TestContextManager()


# Конфигурация для Allure отчетов

import allure

@pytest.fixture(autouse=True)
def allure_test_setup(request):
    """
    Автоматическая настройка Allure для всех тестов.
    
    Args:
        request: Объект запроса pytest
    """
    # Добавляем информацию о тесте в Allure
    test_name = request.node.name
    test_class = request.cls.__name__ if request.cls else "Без класса"
    
    with allure.step("Информация о тесте"):
        allure.attach(test_name, name="Название теста", attachment_type=allure.attachment_type.TEXT)
        allure.attach(test_class, name="Класс теста", attachment_type=allure.attachment_type.TEXT)
        allure.attach(request.node.nodeid, name="Полный путь", attachment_type=allure.attachment_type.TEXT)


# Обработка ошибок и восстановление

@pytest.fixture(autouse=True)
def error_recovery():
    """
    Автоматическая обработка ошибок и восстановление.
    
    Этот фикстур гарантирует что тесты будут выполняться
    даже при возникновении ошибок в предыдущих тестах.
    """
    # Здесь можно добавить логику восстановления
    # Например, очистку временных данных, сброс состояния и т.д.
    pass


# Настройка таймаутов для тестов

@pytest.fixture
def test_timeout(request):
    """
    Фикстура для установки таймаута теста.
    
    Args:
        request: Объект запроса pytest
        
    Returns:
        int: Таймаут в секундах (по умолчанию 30)
    """
    return int(request.config.getoption("--test-timeout", 30))


def pytest_addoption(parser):
    """Добавление пользовательских опций командной строки."""
    parser.addoption(
        "--test-timeout",
        action="store",
        default=30,
        help="Таймаут для тестов в секундах"
    )


# Логирование и диагностика

@pytest.fixture
def test_logger(request):
    """
    Фикстура для получения логгера теста.
    
    Args:
        request: Объект запроса pytest
        
    Returns:
        logging.Logger: Логгер для текущего теста
    """
    test_name = request.node.name
    logger = logging.getLogger(f"test.{test_name}")
    
    # Настройка обработчика для текущего теста
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f'%(asctime)s - {test_name} - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    
    return logger
