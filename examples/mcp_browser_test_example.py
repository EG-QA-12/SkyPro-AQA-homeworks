#!/usr/bin/env python3
"""
Пример использования Playwright MCP для написания автотестов.

Этот файл демонстрирует основные паттерны использования Playwright MCP
для автоматизации браузерных тестов.
"""

import sys
from typing import Dict, Any

# Попытка импортировать MCP клиент
try:
    # Предполагаем, что функция доступна через cline_mcp
    from cline_mcp import use_mcp_tool
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("ВНИМАНИЕ: MCP клиент не доступен. Убедитесь, что он properly configured.")
    use_mcp_tool = None

def basic_navigation_test():
    """Базовый тест навигации с использованием Playwright MCP."""
    
    if not MCP_AVAILABLE or use_mcp_tool is None:
        print("MCP недоступен")
        return False
    
    try:
        print("=== Тест базовой навигации ===")
        
        # 1. Переход на страницу
        print("1. Переход на https://bll.by...")
        use_mcp_tool(
            server_name="playwright-mcp",
            tool_name="browser_navigate",
            arguments={"url": "https://bll.by"}
        )
        print("   ✓ Успешный переход")
        
        # 2. Получение снимка страницы
        print("2. Получение снимка страницы...")
        snapshot = use_mcp_tool(
            server_name="playwright-mcp",
            tool_name="browser_snapshot",
            arguments={}
        )
        
        # 3. Проверка наличия ключевых элементов
        print("3. Проверка элементов страницы...")
        if "bll" in str(snapshot).lower():
            print("   ✓ Найдено упоминание 'bll' в содержимом страницы")
        else:
            print("   ⚠ Не найдено упоминание 'bll' в содержимом страницы")
        
        # 4. Создание скриншота
        print("4. Создание скриншота...")
        use_mcp_tool(
            server_name="playwright-mcp",
            tool_name="browser_take_screenshot",
            arguments={
                "filename": "test_screenshot.jpg",
                "fullPage": True
            }
        )
        print("   ✓ Скриншот сохранен как test_screenshot.jpg")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def interactive_element_test():
    """Тест взаимодействия с элементами страницы."""
    
    if not MCP_AVAILABLE or use_mcp_tool is None:
        print("MCP недоступен")
        return False
    
    try:
        print("\n=== Тест взаимодействия с элементами ===")
        
        # Переход на тестовую страницу (или главную)
        use_mcp_tool(
            server_name="playwright-mcp",
            tool_name="browser_navigate",
            arguments={"url": "https://bll.by"}
        )
        
        # Получаем снимок для анализа структуры
        snapshot = use_mcp_tool(
            server_name="playwright-mcp",
            tool_name="browser_snapshot",
            arguments={}
        )
        print("1. Страница загружена и проанализирована")
        
        # Пример ожидания элемента (в реальном тесте нужно знать точные селекторы)
        print("2. Ожидание загрузки страницы...")
        use_mcp_tool(
            server_name="playwright-mcp",
            tool_name="browser_wait_for",
            arguments={"time": 2}
        )
        print("   ✓ Страница загружена")
        
        # Получаем логи консоли
        console_logs = use_mcp_tool(
            server_name="github.com/AgentDeskAI/browser-tools-mcp",
            tool_name="getConsoleLogs",
            arguments={}
        )
        print(f"3. Логи консоли получены: {len(console_logs.get('logs', []))} записей")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def performance_monitoring_test():
    """Тест мониторинга производительности."""
    
    if not MCP_AVAILABLE or use_mcp_tool is None:
        print("MCP недоступен")
        return False
    
    try:
        print("\n=== Тест производительности ===")
        
        # Переход на страницу
        use_mcp_tool(
            server_name="playwright-mcp",
            tool_name="browser_navigate",
            arguments={"url": "https://bll.by"}
        )
        
        # Получаем сетевые запросы
        network_requests = use_mcp_tool(
            server_name="github.com/AgentDeskAI/browser-tools-mcp",
            tool_name="getNetworkLogs",
            arguments={}
        )
        
        # Получаем логи консоли
        console_logs = use_mcp_tool(
            server_name="github.com/AgentDeskAI/browser-tools-mcp",
            tool_name="getConsoleLogs",
            arguments={}
        )
        
        # Получаем ошибки консоли
        console_errors = use_mcp_tool(
            server_name="github.com/AgentDeskAI/browser-tools-mcp",
            tool_name="getConsoleErrors",
            arguments={}
        )
        
        print(f"1. Сетевые запросы: {len(network_requests.get('requests', []))}")
        print(f"2. Логи консоли: {len(console_logs.get('logs', []))}")
        print(f"3. Ошибки консоли: {len(console_errors.get('errors', []))}")
        
        # Запуск аудита производительности
        perf_audit = use_mcp_tool(
            server_name="github.com/AgentDeskAI/browser-tools-mcp",
            tool_name="runPerformanceAudit",
            arguments={}
        )
        print("4. Аудит производительности выполнен")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Ошибка: {e}")
        return False

def create_test_template():
    """Создание шаблона для нового теста."""
    
    template = '''
import pytest
from cline_mcp import use_mcp_tool

@pytest.mark.mcp
def test_example_mcp():
    """Пример теста с использованием Playwright MCP."""
    
    # Переход на страницу
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={{"url": "https://your-test-url.com"}}
    )
    
    # Взаимодействие с элементами
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_click",
        arguments={{
            "element": "Описание элемента",
            "ref": "референс_элемента"
        }}
    )
    
    # Проверки
    snapshot = use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_snapshot",
        arguments={{}}
    )
    
    # Добавьте ваши проверки здесь
    assert "ожидаемый_текст" in str(snapshot)
'''
    
    return template

def main():
    """Основная функция для демонстрации возможностей."""
    
    if not MCP_AVAILABLE:
        print("MCP клиент не доступен. Проверьте конфигурацию.")
        print("См. docs/guides/MCP_SERVERS_GUIDE.md для подробной информации.")
        return 1
    
    print("Демонстрация использования Playwright MCP для автотестов")
    print("=" * 50)
    
    # Запуск тестов
    tests = [
        basic_navigation_test,
        interactive_element_test,
        performance_monitoring_test
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\nРезультаты: {passed}/{total} тестов пройдено")
    
    # Создание шаблона
    print("\nСоздание шаблона теста...")
    template = create_test_template()
    print("Шаблон сохранен в examples/mcp_test_template.py")
    
    # Сохраняем шаблон
    with open("examples/mcp_test_template.py", "w", encoding="utf-8") as f:
        f.write(template)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
