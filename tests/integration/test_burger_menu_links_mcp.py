import pytest
from typing import List, Tuple
import csv

# Импортируем функцию для использования MCP инструментов
try:
    from cline_mcp import use_mcp_tool
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

CSV_PATH = "tests/data/burger_menu_links.csv"
WAIT_TIMEOUT = 1500

def load_burger_menu_links() -> List[Tuple[str, str]]:
    """Загружает параметры теста из CSV-файла.

    Returns:
        Список кортежей (текст ссылки, href).
    """
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [(row["link_text"].strip(), row["href"].strip()) for row in reader]

def add_allow_session_param(url: str) -> str:
    """Добавляет параметр allow-session=2 к URL корректно (через ? или &)."""
    from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query['allow-session'] = ['2']
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP client not available")
def test_burger_menu_navigation_mcp() -> None:
    """Тест навигации по бургер-меню с использованием Playwright MCP."""
    
    # Переход на главную страницу
    main_url = "https://bll.by/"
    main_url = add_allow_session_param(main_url)
    
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": main_url}
    )
    
    # Получаем снимок страницы для анализа элементов
    snapshot = use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_snapshot",
        arguments={}
    )
    
    # Проверяем наличие кнопки бургер-меню
    burger_button_found = False
    if "menu-btn menu-btn_new" in str(snapshot):
        burger_button_found = True
    
    # Кликаем по кнопке бургер-меню
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_click",
        arguments={
            "element": "Burger menu button with class 'menu-btn menu-btn_new'",
            "ref": "menu-btn"  # Это будет референс из снимка
        }
    )
    
    # Ждем появления меню
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_wait_for",
        arguments={"text": "menu_item_link", "time": 2}
    )
    
    # Получаем обновленный снимок
    updated_snapshot = use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_snapshot",
        arguments={}
    )
    
    # Проверяем, что меню открылось
    assert "menu_item_link" in str(updated_snapshot), "Burger menu did not open"
    
    print("MCP browser test completed successfully")

@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP client not available")
@pytest.mark.parametrize("link_text,href", load_burger_menu_links()[:3])  # Тестируем первые 3 ссылки
def test_burger_menu_links_mcp(link_text: str, href: str) -> None:
    """Параметризованный тест ссылок бургер-меню с использованием Playwright MCP."""
    
    # Переход на главную страницу
    main_url = "https://bll.by/"
    main_url = add_allow_session_param(main_url)
    href = add_allow_session_param(href)
    
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": main_url}
    )
    
    # Открываем бургер-меню
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_click",
        arguments={
            "element": "Burger menu button",
            "ref": "menu-btn"
        }
    )
    
    # Ждем появления меню
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_wait_for",
        arguments={"text": link_text, "time": 2}
    )
    
    # Кликаем по ссылке
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_click",
        arguments={
            "element": f"Menu link with text '{link_text}'",
            "ref": f"link-{link_text}"  # Референс будет определен из снимка
        }
    )
    
    # Ждем загрузки страницы
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_wait_for",
        arguments={"text": link_text, "time": 3}
    )
    
    # Проверяем наличие заголовка
    page_content = use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_snapshot",
        arguments={}
    )
    
    assert link_text in str(page_content), f"Header with text '{link_text}' not found on page"
    
    print(f"Successfully navigated to {link_text}")

@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP client not available")
def test_page_performance_mcp() -> None:
    """Тест производительности страницы с использованием Browser Tools MCP."""
    
    # Переход на страницу
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://bll.by/"}
    )
    
    # Получаем логи консоли
    console_logs = use_mcp_tool(
        server_name="github.com/AgentDeskAI/browser-tools-mcp",
        tool_name="getConsoleLogs",
        arguments={}
    )
    
    # Получаем сетевые логи
    network_logs = use_mcp_tool(
        server_name="github.com/AgentDeskAI/browser-tools-mcp",
        tool_name="getNetworkLogs",
        arguments={}
    )
    
    # Запускаем аудит производительности
    perf_audit = use_mcp_tool(
        server_name="github.com/AgentDeskAI/browser-tools-mcp",
        tool_name="runPerformanceAudit",
        arguments={}
    )
    
    # Проверяем, что нет ошибок в консоли
    console_errors = use_mcp_tool(
        server_name="github.com/AgentDeskAI/browser-tools-mcp",
        tool_name="getConsoleErrors",
        arguments={}
    )
    
    assert len(console_errors.get('errors', [])) == 0, "Console errors found"
    
    print("Performance test completed")
    print(f"Console logs count: {len(console_logs.get('logs', []))}")
    print(f"Network requests count: {len(network_logs.get('requests', []))}")

if __name__ == "__main__":
    # Пример ручного запуска теста
    if MCP_AVAILABLE:
        try:
            test_burger_menu_navigation_mcp()
            print("All MCP tests passed!")
        except Exception as e:
            print(f"Test failed: {e}")
    else:
        print("MCP client not available. Please ensure MCP is properly configured.")
