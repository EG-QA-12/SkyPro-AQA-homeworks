# Автоматизация тестирования UI BLL.BY

## Описание проекта

Этот проект содержит инструменты и тесты для автоматизации UI тестирования сайта [BLL.BY](https://bll.by) с использованием Codegen MCP и Playwright.

## ⚠️ ВАЖНО: Для полного функционала требуется авторизация

Некоторые элементы интерфейса доступны только для авторизованных пользователей. Для сбора полного набора локаторов необходимо использовать авторизацию.

## Структура проекта

```
.
├── ui_locators_bll_by.json          # Собранные UI локаторы в формате JSON
├── ui_locators_analysis_report.md    # Отчет по анализу UI локаторов
├── examples/
│   └── bll_by_navigation_test.py     # Примеры тестов навигации
└── README_BLL_UI_TESTING.md         # Этот файл
```

## Собранные UI локаторы

### Основные элементы навигации

1. **Бургер-меню**
   - Селектор: `.menu-btn.menu-btn_new`
   - Иконка: `.burger-icon`

2. **Основное меню**
   - Контейнер: `.new-menu.new-menu_main`
   - Мобильная версия: `.menu-gumb_new.menu-mobile`

3. **Рубрики**
   - Заголовок: `.menu_bl_ttl`
   - Новости: `.menu_item_link.link-rubric_1`
   - Справочная информация: `.menu_item_link.link-rubric_2`
   - Кодексы: `.menu_item_link.link-rubric_3`

## Установка зависимостей

```bash
# Установка Playwright
pip install playwright
playwright install

# Установка дополнительных зависимостей (если нужно)
pip install pytest asyncio
```

## Запуск тестов

### Запуск примера теста

```bash
# Запуск теста в режиме с GUI (видимый браузер)
python examples/bll_by_navigation_test.py

# Запуск теста в headless режиме
python examples/bll_by_navigation_test.py --headless
```

### Запуск с pytest

```bash
# Установка pytest-playwright
pip install pytest-playwright

# Запуск тестов
pytest examples/bll_by_navigation_test.py -v
```

## Использование UI локаторов

### В Playwright тестах

```python
from playwright.sync_api import sync_playwright

def test_bll_navigation():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Открытие сайта
        page.goto("https://bll.by")
        
        # Клик по бургер-меню
        page.click(".menu-btn.menu-btn_new")
        
        # Переход в раздел Новости
        page.click(".menu_item_link.link-rubric_1")
        
        # Проверка URL
        assert page.url == "https://bll.by/news"
        
        browser.close()
```

### В Selenium тестах

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_bll_navigation():
    driver = webdriver.Chrome()
    
    try:
        # Открытие сайта
        driver.get("https://bll.by")
        
        # Клик по бургер-меню
        burger_menu = driver.find_element(
            By.CSS_SELECTOR, 
            ".menu-btn.menu-btn_new"
        )
        burger_menu.click()
        
        # Переход в раздел Новости
        news_link = driver.find_element(
            By.CSS_SELECTOR, 
            ".menu_item_link.link-rubric_1"
        )
        news_link.click()
        
        # Проверка URL
        assert driver.current_url == "https://bll.by/news"
        
    finally:
        driver.quit()
```

## Интеграция с Codegen MCP

### Использование через Playwright MCP

```python
# Пример использования Codegen MCP для анализа страницы
from mcp import use_tool

# Анализ главной страницы
result = use_tool("playwright-mcp", "browser_navigate", {
    "url": "https://bll.by"
})

# Сбор локаторов
locators = use_tool("playwright-mcp", "browser_evaluate", {
    "function": "() => { /* функция сбора локаторов */ }"
})
```

## Рекомендации по стабильности локаторов

1. **Приоритет селекторов**:
   - `data-testid` (если доступны)
   - Уникальные классы (`.menu_item_link.link-rubric_1`)
   - Структурные селекторы (`.menu-item:nth-child(1)`)

2. **Обработка изменений**:
   - Регулярно проверять актуальность локаторов
   - Использовать относительные пути вместо абсолютных
   - Избегать селекторов, зависящих от позиционирования

## Примеры тестовых сценариев

### 1. Тест открытия бургер-меню

```python
async def test_burger_menu_opens(page):
    await page.goto("https://bll.by")
    
    # Клик по бургеру
    await page.click(".menu-btn.menu-btn_new")
    
    # Проверка видимости меню
    menu = page.locator(".menu-gumb_new.menu-mobile")
    await expect(menu).to_be_visible()
```

### 2. Тест навигации по рубрикам

```python
async def test_rubric_navigation(page):
    await page.goto("https://bll.by")
    
    # Открыть меню
    await page.click(".menu-btn.menu-btn_new")
    
    # Перейти в Новости
    await page.click(".menu_item_link.link-rubric_1")
    
    # Проверить URL
    await expect(page).to_have_url("https://bll.by/news")
```

## Поддержка и обновления

- **Дата последнего обновления**: 23.09.2025
- **Анализируемый сайт**: https://bll.by
- **Формат локаторов**: CSS селекторы
- **Совместимость**: Playwright, Selenium

## Лицензия

Этот проект предназначен для образовательных и тестовых целей. Используйте в соответствии с условиями использования сайта BLL.BY.
