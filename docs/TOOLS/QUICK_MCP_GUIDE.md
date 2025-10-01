# Быстрый старт с Playwright MCP

## Что такое Playwright MCP?

Playwright MCP - это инструмент для автоматизации браузерных тестов через Model Context Protocol. Он позволяет управлять браузером и выполнять тестовые сценарии без прямого программирования браузера.

## Основные команды

### Навигация
```python
# Переход на страницу
use_mcp_tool(
    server_name="playwright-mcp",
    tool_name="browser_navigate",
    arguments={"url": "https://example.com"}
)

# Получение снимка страницы
snapshot = use_mcp_tool(
    server_name="playwright-mcp",
    tool_name="browser_snapshot",
    arguments={}
)

# Создание скриншота
use_mcp_tool(
    server_name="playwright-mcp",
    tool_name="browser_take_screenshot",
    arguments={"filename": "page.jpg", "fullPage": True}
)
```

### Взаимодействие с элементами
```python
# Клик по элементу
use_mcp_tool(
    server_name="playwright-mcp",
    tool_name="browser_click",
    arguments={
        "element": "Описание элемента",
        "ref": "элемент-референс"
    }
)

# Ввод текста
use_mcp_tool(
    server_name="playwright-mcp",
    tool_name="browser_type",
    arguments={
        "element": "Поле ввода",
        "ref": "input-ref",
        "text": "тестовый текст"
    }
)

# Ожидание
use_mcp_tool(
    server_name="playwright-mcp",
    tool_name="browser_wait_for",
    arguments={"time": 3}
)
```

## Запуск тестов

### Python скрипты
```bash
python test_bll_navigation.py
python examples/mcp_browser_test_example.py
```

### Pytest тесты
```bash
# Все MCP тесты
pytest -m mcp

# Тесты интеграции с MCP
pytest tests/integration/ -m mcp

# Конкретный тест
pytest tests/integration/test_burger_menu_links_mcp.py
```

## Полезные ресурсы

- **Полное руководство**: `docs/guides/PLAYWRIGHT_MCP_TESTING_GUIDE.md`
- **Список всех инструментов**: `docs/guides/MCP_SERVERS_GUIDE.md`
- **Примеры тестов**: `examples/` и `tests/integration/`
- **Шаблон теста**: `examples/mcp_test_template.py`

## Распространенные задачи

### 1. Тест навигации
```python
use_mcp_tool("playwright-mcp", "browser_navigate", {"url": "https://bll.by"})
snapshot = use_mcp_tool("playwright-mcp", "browser_snapshot", {})
assert "ожидаемый_текст" in str(snapshot)
```

### 2. Тест производительности
```python
use_mcp_tool("playwright-mcp", "browser_navigate", {"url": "https://bll.by"})
logs = use_mcp_tool("github.com/AgentDeskAI/browser-tools-mcp", "getConsoleLogs", {})
errors = use_mcp_tool("github.com/AgentDeskAI/browser-tools-mcp", "getConsoleErrors", {})
assert len(errors.get('errors', [])) == 0
```

### 3. Скриншот страницы
```python
use_mcp_tool("playwright-mcp", "browser_navigate", {"url": "https://bll.by"})
use_mcp_tool("playwright-mcp", "browser_take_screenshot", {
    "filename": "screenshot.jpg",
    "fullPage": True
})
```

## Устранение неполадок

1. **MCP не доступен**: Проверьте `cline_mcp_settings.json`
2. **Элемент не найден**: Используйте `browser_snapshot` для анализа
3. **Таймауты**: Увеличьте время ожидания
4. **Ошибки в консоли**: Проверьте `getConsoleErrors`

## Дополнительная информация

- Все MCP серверы запускаются автоматически
- Используйте `sequentialthinking` для сложной логики
- Комбинируйте несколько MCP серверов для расширенных тестов
- Смотрите примеры в существующих тестах
