#!/usr/bin/env python3
"""
Утилиты и fixtures для интеграции Allure в тестовые проекты.

Этот модуль предоставляет:
- Декораторы для автоматического добавления Allure метаданных
- Fixtures для тестовых данных и отчетности
- Функции для создания подробных отчетов
- Интеграцию с pytest для улучшенного опыта
"""

import allure
import pytest
import json
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from functools import wraps


class AllureReporter:
    """Класс для создания подробных Allure отчетов."""
    
    @staticmethod
    def add_environment_info(test_environment: Dict[str, str]) -> None:
        """
        Добавляет информацию о среде выполнения тестов.
        
        Args:
            test_environment: Словарь с информацией о среде
        """
        for key, value in test_environment.items():
            allure.environment(**{key: value})
    
    @staticmethod
    def attach_screenshot(screenshot_path: Union[str, Path], name: str = "Screenshot") -> None:
        """
        Прикрепляет скриншот к отчету Allure.
        
        Args:
            screenshot_path: Путь к файлу скриншота
            name: Название вложения
        """
        if isinstance(screenshot_path, str):
            screenshot_path = Path(screenshot_path)
        
        if screenshot_path.exists():
            with open(screenshot_path, 'rb') as f:
                allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)
    
    @staticmethod
    def attach_logs(log_content: str, name: str = "Test Logs") -> None:
        """
        Прикрепляет логи к отчету Allure.
        
        Args:
            log_content: Содержимое логов
            name: Название вложения
        """
        allure.attach(log_content, name=name, attachment_type=allure.attachment_type.TEXT)
    
    @staticmethod
    def attach_html(html_content: str, name: str = "HTML Output") -> None:
        """
        Прикрепляет HTML содержимое к отчету Allure.
        
        Args:
            html_content: HTML содержимое
            name: Название вложения
        """
        allure.attach(html_content, name=name, attachment_type=allure.attachment_type.HTML)
    
    @staticmethod
    def attach_json(data: Any, name: str = "JSON Data") -> None:
        """
        Прикрепляет JSON данные к отчету Allure.
        
        Args:
            data: Данные для сериализации в JSON
            name: Название вложения
        """
        json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        allure.attach(json_str, name=name, attachment_type=allure.attachment_type.JSON)
    
    @staticmethod
    def step(step_name: str) -> Callable:
        """
        Декоратор для создания шагов в отчете Allure.
        
        Args:
            step_name: Название шага
            
        Returns:
            Декоратор функции
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                with allure.step(step_name):
                    return func(*args, **kwargs)
            return wrapper
        return decorator


def allure_test_case(
    title: str = None,
    description: str = None,
    severity: str = "normal",
    epic: str = None,
    feature: str = None,
    story: str = None,
    tag: str = None,
    link_type: str = None,
    link_url: str = None,
    issue: str = None,
    testcase: str = None
) -> Callable:
    """
    Декоратор для автоматического добавления Allure метаданных к тестам.
    
    Args:
        title: Заголовок теста
        description: Описание теста
        severity: Критичность (blocker, critical, normal, minor, trivial)
        epic: Epic в Allure
        feature: Feature в Allure
        story: Story в Allure
        tag: Тег для категоризации
        link_type: Тип ссылки (issue, tms, custom)
        link_url: URL ссылки
        issue: ID проблемы
        testcase: ID тест-кейса
        
    Returns:
        Декоратор функции
    """
    def decorator(func: Callable) -> Callable:
        # Добавляем заголовок
        if title:
            func = allure.title(title)(func)
        
        # Добавляем описание
        if description:
            func = allure.description(description)(func)
        
        # Добавляем критичность
        func = allure.severity(getattr(allure.severity_level, severity.upper(), allure.severity_level.NORMAL))(func)
        
        # Добавляем epic, feature, story
        if epic:
            func = allure.epic(epic)(func)
        if feature:
            func = allure.feature(feature)(func)
        if story:
            func = allure.story(story)(func)
        
        # Добавляем тег
        if tag:
            func = allure.tag(tag)(func)
        
        # Добавляем ссылки
        if link_url and link_type:
            if link_type.lower() == "issue":
                func = allure.issue(link_url, issue or "Issue")(func)
            elif link_type.lower() == "tms":
                func = allure.testcase(link_url, testcase or "Test Case")(func)
            else:
                func = allure.link(link_url, name=link_type)(func)
        
        return func
    
    return decorator


# Fixtures для интеграции с pytest
@pytest.fixture(scope="session", autouse=True)
def allure_setup():
    """Автоматическая настройка Allure для всех тестов."""
    # Добавляем информацию о среде выполнения
    AllureReporter.add_environment_info({
        "Test Execution Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Python Version": pytest.__version__,
        "Platform": "Windows",
    })


@pytest.fixture
def allure_reporter():
    """Fixture для доступа к AllureReporter в тестах."""
    return AllureReporter


@pytest.fixture
def allure_step():
    """Fixture для создания шагов в тестах."""
    def step(step_name: str):
        return allure.step(step_name)
    return step


@pytest.fixture
def allure_attach():
    """Fixture для прикрепления файлов к отчету."""
    def attach(content: Any, name: str = "Attachment", attachment_type: str = "text"):
        """
        Прикрепляет содержимое к отчету Allure.
        
        Args:
            content: Содержимое для прикрепления
            name: Название вложения
            attachment_type: Тип вложения (text, json, html, png, etc.)
        """
        if attachment_type.lower() == "json":
            AllureReporter.attach_json(content, name)
        elif attachment_type.lower() == "html":
            AllureReporter.attach_html(str(content), name)
        elif attachment_type.lower() == "png":
            AllureReporter.attach_screenshot(content, name)
        else:
            AllureReporter.attach_logs(str(content), name)
    
    return attach


@pytest.fixture(autouse=True)
def auto_attach_on_failure(request, allure_attach):
    """Автоматически прикрепляет информацию при падении теста."""
    yield
    
    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        # Прикрепляем трассировку ошибки
        if request.node.rep_call.longrepr:
            allure_attach(
                str(request.node.rep_call.longrepr),
                "Error Traceback",
                "text"
            )
        
        # Прикрепляем информацию о тесте
        test_info = {
            "test_name": request.node.name,
            "test_file": str(request.node.fspath),
            "failure_time": datetime.now().isoformat(),
        }
        allure_attach(test_info, "Test Information", "json")


# Хук для автоматического прикрепления информации о тестах
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для создания отчетов и прикрепления дополнительной информации."""
    outcome = yield
    rep = outcome.get_result()
    
    # Сохраняем результат в узле теста для доступа в fixture
    setattr(item, f"rep_{rep.when}", rep)
    
    # Добавляем дополнительную информацию в Allure
    if rep.when == "call":
        if rep.passed:
            allure.dynamic.tag("passed")
        elif rep.failed:
            allure.dynamic.tag("failed")
            
            # Прикрепляем подробную информацию об ошибке
            if rep.longrepr:
                error_message = str(rep.longrepr)
                AllureReporter.attach_logs(error_message, "Detailed Error Information")
        elif rep.skipped:
            allure.dynamic.tag("skipped")


# Специальные декораторы для разных типов тестов
def smoke_test(title: str = None, description: str = None):
    """Декоратор для smoke тестов."""
    return allure_test_case(
        title=title,
        description=description,
        severity="critical",
        tag="smoke",
        epic="Smoke Testing"
    )


def regression_test(title: str = None, description: str = None):
    """Декоратор для регрессионных тестов."""
    return allure_test_case(
        title=title,
        description=description,
        severity="normal",
        tag="regression",
        epic="Regression Testing"
    )


def ui_test(title: str = None, description: str = None, feature: str = None):
    """Декоратор для UI тестов."""
    return allure_test_case(
        title=title,
        description=description,
        severity="normal",
        tag="ui",
        epic="User Interface",
        feature=feature or "UI Testing"
    )


def api_test(title: str = None, description: str = None, feature: str = None):
    """Декоратор для API тестов."""
    return allure_test_case(
        title=title,
        description=description,
        severity="normal",
        tag="api",
        epic="API Testing",
        feature=feature or "API Integration"
    )


def auth_test(title: str = None, description: str = None):
    """Декоратор для тестов авторизации."""
    return allure_test_case(
        title=title,
        description=description,
        severity="critical",
        tag="auth",
        epic="Authentication & Authorization",
        feature="User Authentication"
    )


def database_test(title: str = None, description: str = None):
    """Декоратор для тестов базы данных."""
    return allure_test_case(
        title=title,
        description=description,
        severity="normal",
        tag="database",
        epic="Database Integration",
        feature="Data Management"
    )


# Утилиты для работы с Allure в контексте Playwright
class PlaywrightAllureIntegration:
    """Интеграция Allure с Playwright для E2E тестов."""
    
    @staticmethod
    def attach_browser_logs(page, name: str = "Browser Console Logs"):
        """Прикрепляет логи браузера к отчету."""
        try:
            # Получаем логи консоли если они доступны
            logs = []
            # В Playwright логи можно получить через события page
            # Это базовая реализация, может потребоваться расширение
            AllureReporter.attach_logs(str(logs), name)
        except Exception as e:
            AllureReporter.attach_logs(f"Failed to get browser logs: {str(e)}", "Browser Logs Error")
    
    @staticmethod
    def attach_page_screenshot(page, name: str = "Page Screenshot"):
        """Делает скриншот страницы и прикрепляет к отчету."""
        try:
            screenshot = page.screenshot()
            allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            AllureReporter.attach_logs(f"Failed to take screenshot: {str(e)}", "Screenshot Error")
    
    @staticmethod
    def attach_page_source(page, name: str = "Page Source"):
        """Прикрепляет HTML источник страницы к отчету."""
        try:
            html_content = page.content()
            AllureReporter.attach_html(html_content, name)
        except Exception as e:
            AllureReporter.attach_logs(f"Failed to get page source: {str(e)}", "Page Source Error")


# Fixture для Playwright интеграции
@pytest.fixture
def playwright_allure(request):
    """Fixture для интеграции Playwright с Allure."""
    integration = PlaywrightAllureIntegration()
    
    # Автоматически прикрепляем скриншот при падении теста
    def finalizer():
        if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
            # Пытаемся получить page из fixture
            if 'page' in request.fixturenames:
                page = request.getfixturevalue('page')
                integration.attach_page_screenshot(page, "Failed Test Screenshot")
                integration.attach_page_source(page, "Failed Test Page Source")
                integration.attach_browser_logs(page, "Failed Test Browser Logs")
    
    request.addfinalizer(finalizer)
    return integration


# Экспорт основных компонентов
__all__ = [
    'AllureReporter',
    'allure_test_case',
    'smoke_test',
    'regression_test',
    'ui_test',
    'api_test',
    'auth_test',
    'database_test',
    'PlaywrightAllureIntegration',
    'allure_reporter',
    'allure_step',
    'allure_attach',
    'playwright_allure',
]
