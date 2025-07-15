# 🚀 Framework автоматизации тестирования

Переиспользуемые компоненты для автотестов проекта BLL. Этот framework предоставляет единообразные инструменты для написания надежных и поддерживаемых автотестов.

## 📖 Описание

Framework разработан для упрощения создания автотестов и обеспечения консистентности между различными тестовыми проектами. Основные принципы:

- **Переиспользование** - общие компоненты для всех тестов
- **Надежность** - встроенные ожидания и обработка ошибок  
- **Простота** - понятный API для команды
- **Расширяемость** - легко добавлять новые модули

## 📦 Структура

```
framework/
├── app/                    # Page Objects и бизнес-логика
│   └── pages/             # Page Object модели для UI
├── fixtures/              # Pytest фикстуры
├── utils/                 # Утилиты и вспомогательные функции  
│   └── reporting/         # Allure интеграция
└── db_utils/              # Работа с базой данных
```

### 📄 Основные модули

#### `app/pages/` - Page Objects
- **`login_page.py`** - Страница авторизации
- **`profile_page.py`** - Страница профиля пользователя  
- **`base_page.py`** - Базовый класс для всех страниц

#### `utils/` - Утилиты
- **`auth_utils.py`** - Авторизация и работа с cookies
- **`url_utils.py`** - Работа с URL-адресами
- **`cookie_constants.py`** - Константы для cookies
- **`reporting/allure_utils.py`** - Allure отчеты

#### `fixtures/` - Pytest фикстуры
- **`auth_fixtures.py`** - Фикстуры для авторизации

#### `db_utils/` - База данных
- **`database_manager.py`** - Менеджер БД SQLite
- **`security.py`** - Безопасность и хеширование

## 🚀 Быстрый старт

### Установка зависимостей
```bash
pip install -r requirements.txt
python -m playwright install
```

### Базовый пример использования
```python
import pytest
from framework.app.pages.login_page import LoginPage
from framework.fixtures.auth_fixtures import authenticated_admin

def test_login_functionality(page):
    # Использование Page Object
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.fill_username("admin")
    login_page.fill_password("password")
    login_page.click_submit_button()
    
    # Проверка успешной авторизации
    assert login_page.is_logged_in()

def test_with_auth_fixture(authenticated_admin):
    # Использование готовой фикстуры авторизации
    page = authenticated_admin.new_page()
    page.goto("https://bll.by/admin")
    # Тест уже авторизованного пользователя
```

## 💼 Использование

### 🔐 Авторизация и Cookies

#### Простая авторизация
```python
from framework.utils.auth_utils import save_cookie, load_cookie

# Сохранение cookies после авторизации
save_cookie(context, "admin_cookies.json")

# Загрузка cookies для повторного использования
load_cookie(context, "admin_cookies.json")
```

#### Продвинутая авторизация
```python
from framework.utils.auth_utils import UnifiedAuthManager

auth_manager = UnifiedAuthManager()

# Сохранение с метаданными
auth_manager.save_auth_cookie(context, "admin", {
    "role": "administrator", 
    "expiry": "2025-12-31"
})

# Загрузка с проверкой валидности
if auth_manager.load_auth_cookie(context, "admin"):
    print("Cookies успешно загружены")
```

### 📄 Page Objects

#### Создание новой страницы
```python
from framework.app.pages.base_page import BasePage

class MyPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.URL = "https://example.com/my-page"
        
    def navigate(self):
        """Переход на страницу."""
        self.page.goto(self.URL)
        
    def get_title(self):
        """Получение заголовка страницы."""
        return self.page.title()
```

### 🎯 Фикстуры для тестов

#### Готовые фикстуры авторизации
```python
def test_admin_functionality(authenticated_admin):
    """Тест функций администратора."""
    page = authenticated_admin.new_page()
    # Уже авторизован как admin
    
def test_user_functionality(authenticated_user):
    """Тест функций обычного пользователя.""" 
    page = authenticated_user.new_page()
    # Уже авторизован как user
```

#### Быстрая авторизация
```python
def test_quick_access(quick_auth):
    """Тест с быстрой авторизацией любого пользователя."""
    context = quick_auth("moderator")
    page = context.new_page()
    # Авторизован как moderator
```

### 📊 Allure отчеты

#### Автоматические отчеты
```python
from framework.utils.reporting.allure_utils import ui_test, AllureReporter

@ui_test(title="Тест главной страницы", feature="Navigation")
def test_main_page(page):
    """Тест загрузки главной страницы."""
    page.goto("https://bll.by")
    
    # Автоматическое прикрепление скриншота при ошибке
    assert page.title() == "BLL"
```

#### Ручное управление отчетами
```python
import allure
from framework.utils.reporting.allure_utils import AllureReporter

def test_with_custom_attachments(page):
    with allure.step("Переход на страницу"):
        page.goto("https://bll.by")
        
    with allure.step("Проверка элементов"):
        # Добавление скриншота
        AllureReporter.attach_screenshot("screenshot.png")
        
        # Добавление логов браузера
        AllureReporter.attach_browser_logs(page)
```

### 🗄️ Работа с базой данных

```python
from framework.db_utils.database_manager import DatabaseManager

# Контекстный менеджер (рекомендуется)
with DatabaseManager() as db:
    user = db.get_user("admin")
    print(f"Пользователь: {user.login}, роль: {user.role}")
    
    # Добавление нового пользователя
    user_id = db.add_or_update_user(
        login="new_user",
        role="user", 
        subscription="basic"
    )
```

## 🔧 Конфигурация

### Переменные окружения
Создайте файл `secrets/.env`:
```bash
# Основные настройки
AUTH_USERNAME=admin
AUTH_PASSWORD=your_password
BASE_URL=https://bll.by

# Настройки браузера  
HEADLESS=true
BROWSER=chromium
SLOW_MO=0

# База данных
DB_PATH=secrets/users.db
```

### Настройки pytest
В `pytest.ini`:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --alluredir=allure-results
    --browser chromium
```

## 🧪 Примеры тестов

### E2E тест с полным сценарием
```python
import pytest
from framework.app.pages.login_page import LoginPage
from framework.utils.reporting.allure_utils import ui_test

@ui_test(title="Полный сценарий авторизации", feature="Authentication")
def test_full_auth_scenario(page):
    """Тест полного сценария авторизации пользователя."""
    # Переход на страницу логина
    login_page = LoginPage(page)
    login_page.navigate()
    
    # Авторизация
    login_page.login("admin", "password")
    
    # Проверка успешной авторизации
    assert "dashboard" in page.url
    assert page.locator("[data-testid='user-menu']").is_visible()
```

### Тест с фикстурами
```python
@pytest.mark.auth
def test_user_profile_access(authenticated_user):
    """Тест доступа к профилю пользователя."""
    page = authenticated_user.new_page()
    page.goto("https://bll.by/profile")
    
    # Проверяем элементы профиля
    assert page.locator(".profile-header").is_visible()
    assert page.locator(".user-settings").is_visible()
```

## 🎯 Лучшие практики

### ✅ Рекомендации
1. **Используйте Page Objects** для UI взаимодействий
2. **Применяйте фикстуры** для настройки тестовых данных  
3. **Добавляйте ожидания** для стабильности тестов
4. **Группируйте тесты** марками (`@pytest.mark.auth`)
5. **Используйте Allure** для подробных отчетов

### ❌ Чего избегать
1. Прямые вызовы Playwright в тестах
2. Хардкод URL и селекторов
3. Тесты без ожиданий и таймаутов
4. Дублирование кода авторизации
5. Тесты без понятных сообщений об ошибках

## 🔍 Отладка

### Запуск с отладкой
```bash
# Видимый браузер для отладки
pytest tests/test_example.py --headed --slow-mo 1000

# Только сбор тестов без выполнения
pytest --collect-only

# Запуск с подробным выводом
pytest -v -s tests/test_example.py
```

### Логирование
```python
import logging
from framework.utils.auth_utils import logger

# В тестах доступно подробное логирование
logger.info("Начинаем тест авторизации")
```

## 📈 Мониторинг и отчеты

### Allure отчеты
```bash
# Генерация отчета
allure generate allure-results --clean -o allure-report

# Просмотр отчета
allure open allure-report
```

### Анализ качества кода
```bash
# Анализ документации
python scripts/maintenance/analyze_documentation.py

# Анализ импортов
python scripts/maintenance/analyze_imports.py
```

## 🆘 Поддержка

### Частые проблемы

**Проблема**: Тест падает с TimeoutError  
**Решение**: Увеличьте таймауты или добавьте явные ожидания

**Проблема**: Cookies не загружаются  
**Решение**: Проверьте путь к файлу и формат JSON

**Проблема**: Page Object не находит элемент  
**Решение**: Проверьте селекторы и добавьте ожидания

### Контакты
- **Документация**: `docs/` директория
- **Примеры**: `tests/` директория  
- **Архитектура**: `ARCHITECTURE.md`

---

**Версия framework**: 1.0.0  
**Последнее обновление**: 2025-01-27