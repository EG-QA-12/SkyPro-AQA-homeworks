# Руководство по использованию Playwright MCP для автотестов

## Обзор

Playwright MCP предоставляет мощные инструменты для автоматизации браузерных тестов без необходимости напрямую управлять браузером. Это особенно полезно для интеграции с существующими тестовыми фреймворками.

## Основные инструменты Playwright MCP

### Навигация и управление браузером
- `browser_navigate` - переход по URL
- `browser_close` - закрытие страницы
- `browser_resize` - изменение размера окна
- `browser_take_screenshot` - создание скриншота
- `browser_snapshot` - получение снимка страницы (лучше чем скриншот для анализа)

### Взаимодействие с элементами
- `browser_click` - клик по элементу
- `browser_type` - ввод текста
- `browser_select_option` - выбор опции в выпадающем списке
- `browser_hover` - наведение курсора
- `browser_drag` - перетаскивание элементов
- `browser_press_key` - наведение клавиши

### Ожидание и синхронизация
- `browser_wait_for` - ожидание текста, исчезновения текста или времени
- `browser_console_messages` - получение сообщений консоли
- `browser_network_requests` - получение сетевых запросов

## Базовое использование

### Импорт и настройка

```python
from cline_mcp import use_mcp_tool

# Проверка доступности MCP
try:
    from cline_mcp import use_mcp_tool
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
```

### Простой тест навигации

```python
def test_basic_navigation():
    """Базовый тест навигации."""
    
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
    
    # Проверка содержимого
    assert "expected_text" in str(snapshot)
```

## Интеграция с pytest

### Базовый тест с pytest

```python
import pytest
from cline_mcp import use_mcp_tool

@pytest.mark.mcp
def test_page_load():
    """Тест загрузки страницы."""
    
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://bll.by"}
    )
    
    snapshot = use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_snapshot",
        arguments={}
    )
    
    assert "bll" in str(snapshot).lower()

@pytest.mark.mcp
def test_page_screenshot():
    """Тест создания скриншота."""
    
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://bll.by"}
    )
    
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_take_screenshot",
        arguments={
            "filename": "test_page.jpg",
            "fullPage": True
        }
    )
```

### Параметризованные тесты

```python
import pytest
import csv

def load_test_data():
    """Загрузка тестовых данных из CSV."""
    with open("tests/data/test_links.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [(row["text"], row["url"]) for row in reader]

@pytest.mark.mcp
@pytest.mark.parametrize("expected_text,url", load_test_data())
def test_multiple_pages(expected_text, url):
    """Параметризованный тест нескольких страниц."""
    
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": url}
    )
    
    snapshot = use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_snapshot",
        arguments={}
    )
    
    assert expected_text in str(snapshot)
```

## Работа с элементами интерфейса

### Клик по элементам

```python
def test_menu_navigation():
    """Тест навигации через меню."""
    
    # Переход на страницу
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://bll.by"}
    )
    
    # Клик по кнопке меню
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_click",
        arguments={
            "element": "Menu button with class 'menu-btn'",
            "ref": "menu-button-ref"  # Получается из browser_snapshot
        }
    )
    
    # Ожидание появления меню
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_wait_for",
        arguments={"text": "menu-item", "time": 2}
    )
```

### Ввод текста

```python
def test_form_submission():
    """Тест заполнения формы."""
    
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://example.com/form"}
    )
    
    # Ввод текста в поле
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_type",
        arguments={
            "element": "Input field with name 'username'",
            "ref": "username-input",
            "text": "testuser"
        }
    )
    
    # Клик по кнопке отправки
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_click",
        arguments={
            "element": "Submit button",
            "ref": "submit-button"
        }
    )
```

## Мониторинг и отладка

### Получение логов

```python
def test_console_logs():
    """Тест проверки логов консоли."""
    
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://bll.by"}
    )
    
    # Получение логов консоли
    console_logs = use_mcp_tool(
        server_name="github.com/AgentDeskAI/browser-tools-mcp",
        tool_name="getConsoleLogs",
        arguments={}
    )
    
    # Проверка отсутствия ошибок
    console_errors = use_mcp_tool(
        server_name="github.com/AgentDeskAI/browser-tools-mcp",
        tool_name="getConsoleErrors",
        arguments={}
    )
    
    assert len(console_errors.get('errors', [])) == 0
```

### Аудит производительности

```python
def test_page_performance():
    """Тест производительности страницы."""
    
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://bll.by"}
    )
    
    # Аудит производительности
    perf_audit = use_mcp_tool(
        server_name="github.com/AgentDeskAI/browser-tools-mcp",
        tool_name="runPerformanceAudit",
        arguments={}
    )
    
    # Получение сетевых запросов
    network_logs = use_mcp_tool(
        server_name="github.com/AgentDeskAI/browser-tools-mcp",
        tool_name="getNetworkLogs",
        arguments={}
    )
    
    print(f"Network requests: {len(network_logs.get('requests', []))}")
```

## Лучшие практики

### 1. Обработка ошибок

```python
import pytest
from cline_mcp import use_mcp_tool

@pytest.mark.mcp
def test_with_error_handling():
    """Тест с обработкой ошибок."""
    
    try:
        use_mcp_tool(
            server_name="playwright-mcp",
            tool_name="browser_navigate",
            arguments={"url": "https://bll.by"}
        )
        
        snapshot = use_mcp_tool(
            server_name="playwright-mcp",
            tool_name="browser_snapshot",
            arguments={}
        )
        
        assert "expected_content" in str(snapshot)
        
    except Exception as e:
        # Логирование ошибки
        print(f"Test failed: {e}")
        raise
```

### 2. Использование фикстур

```python
import pytest
from cline_mcp import use_mcp_tool

@pytest.fixture(scope="session")
def mcp_browser():
    """Фикстура для инициализации браузера."""
    # Браузер автоматически запускается при первом обращении
    yield "playwright-mcp"
    # Очистка (если нужна)

@pytest.mark.mcp
def test_with_fixture(mcp_browser):
    """Тест с использованием фикстуры."""
    
    use_mcp_tool(
        server_name=mcp_browser,
        tool_name="browser_navigate",
        arguments={"url": "https://bll.by"}
    )
    
    # Тестовая логика...
```

### 3. Параметризация и конфигурация

```python
import pytest
from cline_mcp import use_mcp_tool

# Конфигурация тестов
TEST_CONFIG = {
    "base_url": "https://bll.by",
    "timeout": 5,
    "headless": True
}

@pytest.mark.mcp
@pytest.mark.parametrize("page_path,expected_title", [
    ("/", "Главная"),
    ("/about", "О нас"),
    ("/contact", "Контакты")
])
def test_page_titles(page_path, expected_title):
    """Параметризованный тест заголовков страниц."""
    
    full_url = f"{TEST_CONFIG['base_url']}{page_path}"
    
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": full_url}
    )
    
    snapshot = use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_snapshot",
        arguments={}
    )
    
    assert expected_title in str(snapshot)
```

## Расширенные возможности

### Комбинирование с другими MCP серверами

```python
def test_with_multiple_mcp_servers():
    """Тест с использованием нескольких MCP серверов."""
    
    # Навигация через Playwright
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://bll.by"}
    )
    
    # Получение документации через Context7
    docs = use_mcp_tool(
        server_name="github.com/upstash/context7-mcp",
        tool_name="get-library-docs",
        arguments={"context7CompatibleLibraryID": "/some/library"}
    )
    
    # Анализ через Sequential Thinking
    analysis = use_mcp_tool(
        server_name="server-sequential-thinking",
        tool_name="sequentialthinking",
        arguments={
            "thought": f"Analyze page content with docs: {docs}",
            "nextThoughtNeeded": False,
            "thoughtNumber": 1,
            "totalThoughts": 1
        }
    )
```

### Работа с cookies и сессиями

```python
def test_with_auth_cookies():
    """Тест с использованием cookies авторизации."""
    
    # Переход на страницу
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://bll.by/dashboard"}
    )
    
    # Проверка доступа к защищенному контенту
    snapshot = use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_snapshot",
        arguments={}
    )
    
    assert "dashboard" in str(snapshot).lower()
```

## Запуск тестов

### Запуск отдельных тестов

```bash
# Запуск тестов с MCP маркером
pytest -m mcp tests/integration/

# Запуск конкретного теста
pytest tests/integration/test_mcp_example.py::test_page_load

# Запуск с подробным выводом
pytest -v -s -m mcp
```

### Конфигурация в pytest.ini

```ini
[tool:pytest]
markers =
    mcp: Tests using Playwright MCP
    integration: Integration tests
    e2e: End-to-end tests

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Устранение неполадок

### Распространенные ошибки

1. **MCP клиент не доступен**
   - Проверьте конфигурацию в `cline_mcp_settings.json`
   - Убедитесь, что MCP серверы запущены

2. **Элемент не найден**
   - Используйте `browser_snapshot` для анализа структуры страницы
   - Проверьте правильность описания элемента

3. **Таймауты**
   - Увеличьте время ожидания в `browser_wait_for`
   - Используйте более точные селекторы

### Отладка тестов

```python
def debug_test():
    """Пример отладки теста."""
    
    # Переход на страницу
    use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_navigate",
        arguments={"url": "https://bll.by"}
    )
    
    # Получение подробного снимка
    snapshot = use_mcp_tool(
        server_name="playwright-mcp",
        tool_name="browser_snapshot",
        arguments={}
    )
    
    # Сохранение снимка для анализа
    import json
    with open("debug_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    print("Snapshot saved for debugging")
```

## Примеры из реальных тестов

Смотрите примеры в:
- `tests/integration/test_burger_menu_links_mcp.py`
- `examples/mcp_browser_test_example.py`
- `examples/mcp_test_template.py`

## Дополнительные ресурсы

- [MCP_SERVERS_GUIDE.md](MCP_SERVERS_GUIDE.md) - полное руководство по MCP серверам
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - общее руководство по тестированию
- [REFERENCE.md](REFERENCE.md) - справочник по инструментам
