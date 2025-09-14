# Полное руководство по MCP серверам

## Обзор

MCP (Model Context Protocol) серверы предоставляют дополнительные инструменты и ресурсы для расширения возможностей системы. Все серверы запускаются автоматически при первом обращении к их инструментам.

## Доступные MCP серверы

### 1. Server Sequential Thinking

**Назначение:** Инструмент для последовательного и рефлексивного решения проблем через мышление.

**Команда запуска:** `cmd /c npx -y @smithery/cli@latest run @smithery-ai/server-sequential-thinking --key far-angelfish-LeI7K9`

**Инструменты:**
- `sequentialthinking` - детальный инструмент для динамического и рефлексивного решения проблем

**Особенности:**
- Подходит для разбиения сложных проблем на шаги
- Планирование и дизайн с возможностью корректировки
- Анализ, который может потребовать корректировки курса
- Задачи, где полный объем может быть неясен изначально
- Многошаговые решения
- Поддерживает контекст на нескольких шагах
- Фильтрация нерелевантной информации

**Пример использования:**
```python
result = use_mcp_tool(
    server_name="server-sequential-thinking",
    tool_name="sequentialthinking",
    arguments={
        "thought": "Анализ проблемы...",
        "nextThoughtNeeded": True,
        "thoughtNumber": 1,
        "totalThoughts": 5
    }
)
```

### 2. Playwright MCP

**Назначение:** Инструменты для автоматизации браузера через Playwright.

**Команда запуска:** `npx @playwright/mcp@latest`

**Основные инструменты:**
- `browser_navigate` - переход по URL
- `browser_click` - клик по элементу
- `browser_type` - ввод текста в поле
- `browser_snapshot` - получение снимка страницы
- `browser_take_screenshot` - создание скриншота
- `browser_select_option` - выбор опции в выпадающем списке
- `browser_hover` - наведение курсора
- `browser_drag` - перетаскивание элементов
- `browser_press_key` - нажатие клавиши
- `browser_wait_for` - ожидание элемента или текста
- `browser_close` - закрытие страницы
- `browser_console_messages` - получение сообщений консоли
- `browser_network_requests` - получение сетевых запросов

**Пример использования:**
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
```

### 3. File System MCP

**Назначение:** Доступ к локальной файловой системе.

**Команда запуска:** `npx -y @modelcontextprotocol/server-filesystem d:\Bll_tests\`

**Инструменты:**
- `read_file` - чтение содержимого файла
- `write_file` - создание/перезапись файла
- `list_directory` - список файлов и директорий
- `create_directory` - создание директории
- `move_file` - перемещение/переименование файлов
- `search_files` - поиск файлов по шаблону

**Пример использования:**
```python
# Чтение файла
content = use_mcp_tool(
    server_name="github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
    tool_name="read_file",
    arguments={"path": "config/settings.json"}
)

# Список директорий
files = use_mcp_tool(
    server_name="github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
    tool_name="list_directory",
    arguments={"path": "docs/"}
)
```

### 4. Firecrawl MCP

**Назначение:** Инструменты для веб-скрапинга и поиска.

**Команда запуска:** `npx -y firecrawl-mcp`

**Инструменты:**
- `firecrawl_scrape` - скрапинг содержимого с одной страницы
- `firecrawl_map` - карта сайта для обнаружения URL
- `firecrawl_crawl` - асинхронный краулинг сайта
- `firecrawl_search` - поиск в интернете
- `firecrawl_extract` - извлечение структурированной информации
- `firecrawl_deep_research` - глубокое веб-исследование

**Пример использования:**
```python
# Скрапинг страницы
result = use_mcp_tool(
    server_name="firecrawl-mcp",
    tool_name="firecrawl_scrape",
    arguments={"url": "https://example.com"}
)

# Поиск в интернете
search_results = use_mcp_tool(
    server_name="firecrawl-mcp",
    tool_name="firecrawl_search",
    arguments={"query": "последние новости AI"}
)
```

### 5. Browser Tools MCP

**Назначение:** Инструменты для анализа и отладки браузера.

**Команда запуска:** `node C:\Users\LENOVO\Documents\Cline\MCP\browser-tools-mcp\node_modules\@agentdeskai\browser-tools-mcp\dist\mcp-server.js`

**Инструменты:**
- `getConsoleLogs` - получение логов консоли
- `getConsoleErrors` - получение ошибок консоли
- `getNetworkErrors` - получение сетевых ошибок
- `getNetworkLogs` - получение всех сетевых логов
- `takeScreenshot` - создание скриншота
- `runAccessibilityAudit` - аудит доступности
- `runPerformanceAudit` - аудит производительности
- `runSEOAudit` - аудит SEO
- `runBestPracticesAudit` - аудит лучших практик

**Пример использования:**
```python
# Получение логов консоли
logs = use_mcp_tool(
    server_name="github.com/AgentDeskAI/browser-tools-mcp",
    tool_name="getConsoleLogs",
    arguments={}
)

# Аудит производительности
perf_audit = use_mcp_tool(
    server_name="github.com/AgentDeskAI/browser-tools-mcp",
    tool_name="runPerformanceAudit",
    arguments={}
)
```

### 6. Context7 MCP

**Назначение:** Сервер для работы с контекстом и документацией библиотек.

**Команда запуска:** `cmd /c npx -y @upstash/context7-mcp@latest`

**Инструменты:**
- `resolve-library-id` - разрешение имени библиотеки в ID
- `get-library-docs` - получение документации библиотеки

**Пример использования:**
```python
# Поиск библиотеки
library_info = use_mcp_tool(
    server_name="github.com/upstash/context7-mcp",
    tool_name="resolve-library-id",
    arguments={"libraryName": "react"}
)

# Получение документации
docs = use_mcp_tool(
    server_name="github.com/upstash/context7-mcp",
    tool_name="get-library-docs",
    arguments={"context7CompatibleLibraryID": "/facebook/react"}
)
```

## Общие принципы работы

### Автоматический запуск
Все MCP серверы запускаются автоматически при первом обращении к их инструментам. Не нужно запускать их вручную.

### Обработка ошибок
Если инструмент недоступен:
1. Проверьте конфигурацию в `cline_mcp_settings.json`
2. Убедитесь, что MCP клиент подключен
3. Проверьте логи сервера на наличие ошибок

### Комбинирование инструментов
Можно комбинировать инструменты разных серверов для решения сложных задач:
```python
# Пример комплексного использования
# 1. Поиск информации через Firecrawl
search_results = use_mcp_tool("firecrawl-mcp", "firecrawl_search", {"query": "..."})

# 2. Анализ через Sequential Thinking
analysis = use_mcp_tool("server-sequential-thinking", "sequentialthinking", {...})

# 3. Проверка в браузере через Playwright
use_mcp_tool("playwright-mcp", "browser_navigate", {"url": "..."})
```

## Рекомендации по использованию

1. **Начинайте с простых задач** - используйте один инструмент за раз
2. **Следите за логами** - серверы выводят информацию в консоль
3. **Используйте Sequential Thinking** для сложных задач планирования
4. **Комбинируйте инструменты** для максимальной эффективности
5. **Обрабатывайте ошибки** - проверяйте возвращаемые значения

## Устранение неполадок

### Сервер не запускается
- Проверьте конфигурацию в `cline_mcp_settings.json`
- Убедитесь, что все зависимости установлены
- Проверьте права доступа к файлам

### Инструмент недоступен
- Убедитесь, что сервер запущен
- Проверьте правильность имени инструмента
- Проверьте параметры вызова

### Проблемы с производительностью
- Используйте `sequentialthinking` для оптимизации сложных задач
- Ограничьте количество одновременных вызовов
- Используйте кэширование где возможно
