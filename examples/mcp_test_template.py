import pytest
from cline_mcp import use_mcp_tool

@pytest.mark.mcp
def test_example_mcp():
    """Пример теста с использованием Playwright MCP."""
    
    # Переход на страницу
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://your-test-url.com"}
    )
    
    # Взаимодействие с элементами
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_click",
        arguments={
            "element": "Описание элемента",
            "ref": "референс_элемента"
        }
    )
    
    # Проверки
    snapshot = use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_snapshot",
        arguments={}
    )
    
    # Добавьте ваши проверки здесь
    assert "ожидаемый_текст" in str(snapshot)
