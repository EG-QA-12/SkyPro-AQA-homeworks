# Использование Playwright MCP и Browser Tools

## Как работают MCP серверы

MCP серверы работают через протокол Model Context Protocol и предоставляют инструменты, которые можно вызывать через MCP клиент. Они запускаются автоматически при первом обращении к их инструментам.

## Playwright MCP

Playwright MCP предоставляет инструменты для автоматизации браузера через Playwright.

### Доступные инструменты:

- `browser_navigate` - переход по URL
- `browser_click` - клик по элементу
- `browser_type` - ввод текста в поле
- `browser_snapshot` - получение снимка страницы (лучше чем скриншот)
- `browser_take_screenshot` - создание скриншота
- `browser_select_option` - выбор опции в выпадающем списке
- `browser_hover` - наведение курсора
- `browser_drag` - перетаскивание элементов
- `browser_press_key` - нажатие клавиши
- `browser_wait_for` - ожидание элемента или текста
- `browser_close` - закрытие страницы
- `browser_console_messages` - получение сообщений консоли
- `browser_network_requests` - получение сетевых запросов
- И другие...

### Пример использования Playwright MCP:

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

# Клик по элементу (нужно указать описание элемента из снимка)
use_mcp_tool(
    server_name="playwright-mcp",
    tool_name="browser_click",
    arguments={
        "element": "кнопка с текстом 'Submit'",
        "ref": "какой-то-идентификатор-элемента"
    }
)

# Ввод текста
use_mcp_tool(
    server_name="playwright-mcp",
    tool_name="browser_type",
    arguments={
        "element": "поле ввода email",
        "ref": "идентификатор-поля",
        "text": "user@example.com"
    }
)
```

## Browser Tools MCP

Browser Tools MCP предоставляет дополнительные инструменты для анализа и отладки браузера.

### Доступные инструменты:

- `getConsoleLogs` - получение логов консоли
- `getConsoleErrors` - получение ошибок консоли
- `getNetworkErrors` - получение сетевых ошибок
- `getNetworkLogs` - получение всех сетевых логов
- `takeScreenshot` - создание скриншота
- `runAccessibilityAudit` - аудит доступности
- `runPerformanceAudit` - аудит производительности
- `runSEOAudit` - аудит SEO
- `runBestPracticesAudit` - аудит лучших практик

### Пример использования Browser Tools MCP:

```python
# Получение логов консоли
logs = use_mcp_tool(
    server_name="github.com/AgentDeskAI/browser-tools-mcp",
    tool_name="getConsoleLogs",
    arguments={}
)

# Запуск аудита производительности
perf_audit = use_mcp_tool(
    server_name="github.com/AgentDeskAI/browser-tools-mcp",
    tool_name="runPerformanceAudit",
    arguments={}
)

# Создание скриншота
screenshot = use_mcp_tool(
    server_name="github.com/AgentDeskAI/browser-tools-mcp",
    tool_name="takeScreenshot",
    arguments={}
)
```

## Порядок работы:

1. **Убедитесь, что MCP клиент подключен** к серверам
2. **Используйте инструменты через `use_mcp_tool()`** - серверы запустятся автоматически
3. **Следите за выводом** - серверы могут выводить логи в консоль
4. **Обрабатывайте ошибки** - если инструмент недоступен, проверьте конфигурацию

## Полезные советы:

- Серверы запускаются автоматически при первом вызове
- Не нужно запускать их вручную
- Все инструменты работают через протокол MCP
- Можно комбинировать инструменты разных серверов
- Для сложных задач используйте `server-sequential-thinking` для планирования шагов

## Пример комплексного использования:

```python
# 1. Переход на страницу
use_mcp_tool("playwright-mcp", "browser_navigate", {"url": "https://example.com"})

# 2. Получение снимка страницы
snapshot = use_mcp_tool("playwright-mcp", "browser_snapshot", {})

# 3. Анализ страницы и выполнение действий
use_mcp_tool("playwright-mcp", "browser_click", {
    "element": "найденный элемент",
    "ref": "идентификатор"
})

# 4. Проверка результата
logs = use_mcp_tool("github.com/AgentDeskAI/browser-tools-mcp", "getConsoleLogs", {})
```

## Пример перехода на bll.by:

```python
# Переход на главную страницу bll.by
result = use_mcp_tool(
    server_name="playwright-mcp",
    tool_name="browser_navigate",
    arguments={"url": "https://bll.by"}
)

# Получение снимка страницы для анализа
snapshot = use_mcp_tool(
    server_name="playwright-mcp",
    tool_name="browser_snapshot",
    arguments={}
)

# Проверка консольных логов
console_logs = use_mcp_tool(
    server_name="github.com/AgentDeskAI/browser-tools-mcp",
    tool_name="getConsoleLogs",
    arguments={}
)

print("Navigation result:", result)
print("Page snapshot received")
print("Console logs:", console_logs)
