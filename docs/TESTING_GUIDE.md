# Полное руководство по автоматизированному тестированию

## Оглавление
1. [Введение](#ведение)
2. [Архитектура тестового фреймворка](#архитектура-тестового-фреймворка)
3. [Новый унифицированный фреймворк](#новый-унифицированный-фреймворк)
4. [Типы тестов](#типы-тестов)
5. [Авторизация и безопасность](#авторизация-и-безопасность)
6. [API тестирование](#api-тестирование)
7. [UI тестирование](#ui-тестирование)
8. [Best Practices](#best-practices)
9. [Запуск тестов](#запуск-тестов)
10. [Отладка и диагностика](#отладка-и-диагностика)

## Введение

Добро пожаловать в комплексный фреймворк автоматизированного тестирования проектов BLL! Этот фреймворк предоставляет мощные инструменты для тестирования веб-приложений с учетом современных требований к качеству и надежности.

### Основные цели:
- **Надежность**: Стабильные и воспроизводимые тесты
- **Производительность**: Быстрое выполнение тестов
- **Читаемость**: Понятный и документированный код
- **Масштабируемость**: Легкое расширение функциональности

### Новшества:
- **Новый унифицированный фреймворк** - упрощенное API для тестирования
- **Автоматическая обработка авторизации** - больше не нужно писать boilerplate код
- **Централизованные фикстуры** - повторное использование компонентов
- **Типизированные клиенты** - автодополнение и проверка типов

## Архитектура тестового фреймворка

### Структура проекта:
```
Bll_tests/
├── framework/                          # Основной фреймворк
│   ├── api/                           # Современные API клиенты
│   │   ├── base_client.py            # Базовый клиент с retry логикой
│   │   └── admin_client.py           # Административный клиент
│   ├── new_fixtures/                  # Централизованные фикстуры
│   │   ├── auth_fixtures.py          # Фикстуры авторизации
│   │   └── moderation_fixtures.py    # Фикстуры модерации
│   ├── test_bases/                    # Базовые классы тестов
│   │   └── api_test_base.py          # Базовые классы для API тестов
│   └── utils/                         # Вспомогательные утилиты
├── tests/                             # Тестовые сценарии
│   └── integration/                   # Интеграционные тесты
│       └── test_new_framework_example.py # Примеры нового фреймворка
├── docs/                              # Документация
└── scripts/                           # Вспомогательные скрипты
```

### Ключевые компоненты:

#### 1. API Клиенты
- **BaseAPIClient**: Базовый клиент с автоматической авторизацией
- **AdminAPIClient**: Специализированный клиент для админ панели
- **Автоматический retry**: Обработка 401/419 ошибок
- **CSRF токены**: Автоматическое обновление

#### 2. Фикстуры
- **auth_fixtures**: Фикстуры для авторизации
- **moderation_fixtures**: Фикстуры для модерации
- **Централизованная конфигурация**: Все фикстуры в одном месте

#### 3. Базовые классы тестов
- **APITestBase**: Базовый класс для API тестов
- **AdminAPITestBase**: Для административных тестов
- **UserAPITestBase**: Для пользовательских тестов

## Новый унифицированный фреймворк

### Преимущества нового подхода:

#### 1. Упрощение кода
**Было:**
```python
def test_old_approach():
    auth_manager = SmartAuthManager()
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")
    parser = ModerationPanelParser()
    entries = parser.get_moderation_panel_data(session_cookie, limit=100)
    question = next((e for e in entries if e.get('type') == '?'), None)
    tokens = fetch_csrf_tokens_from_panel(parser.session, "https://expert.bll.by")
    # ... много кода для обработки ошибок
```

**Стало:**
```python
def test_new_approach(admin_client):
    question = admin_client.find_question(mode="latest")
    response = admin_client.publish_question(question['id'])
    assert response.success
```

#### 2. Автоматическая обработка ошибок
- **Retry логика**: Автоматический повтор при 401/419 ошибках
- **Обновление авторизации**: Автоматическое обновление кук
- **CSRF токены**: Автоматическое обновление токенов

#### 3. Типизированные ответы
- **Структурированные данные**: Четкие структуры ответов
- **Встроенные проверки**: Методы для проверки успешности
- **Автодополнение**: IDE помогает писать код быстрее

### Быстрый старт с новым фреймворком:

#### 1. Использование фикстур:
```python
import pytest
import allure

@allure.title("Публикация вопроса через новый фреймворк")
@pytest.mark.api
def test_publish_question_with_new_framework(admin_client):
    """Пример использования нового API клиента."""
    
    with allure.step("Получение последнего вопроса"):
        question = admin_client.find_question(mode="latest", limit=50)
        if not question:
            pytest.skip("Нет вопросов для публикации")
    
    with allure.step("Публикация вопроса"):
        response = admin_client.publish_question(question['id'])
        assert response.success
```

#### 2. Наследование от базовых классов:
```python
from framework.test_bases.api_test_base import AdminAPITestBase

class TestModerationFlow(AdminAPITestBase):
    """Тест комплексного сценария модерации."""
    
    @allure.title("Полный цикл модерации вопроса")
    def test_full_moderation_cycle(self):
        with allure.step("Получение вопроса для модерации"):
            question = self.get_latest_question()
            if not question:
                pytest.skip("Нет вопросов для модерации")
        
        with allure.step("Взятие вопроса в работу"):
            response = self.client.assign_entry(question['id'])
            self.assert_api_success(response)
        
        with allure.step("Публикация вопроса"):
            success = self.publish_question(question['id'])
            assert success
```

#### 3. Параметризованные тесты:
```python
from framework.utils.enums import AnswerPublicationType

@pytest.mark.api
@pytest.mark.parametrize("publication_type", [
    AnswerPublicationType.PUBLISHED,
    AnswerPublicationType.DRAFT,
    AnswerPublicationType.REJECTED
], ids=["published", "draft", "rejected"])
class TestAnswerPublication(AdminAPITestBase):
    """Параметризованный тест публикации ответов."""
    
    @allure.title("Публикация ответа с типом {publication_type}")
    def test_answer_publication(self, publication_type):
        answer = self.get_latest_answer()
        response = self.client.publish_answer(
            answer_id=answer['id'],
            publication_type=publication_type
        )
        self.assert_api_success(response)
```

## Типы тестов

### 1. API Тесты
Тестирование REST API эндпоинтов без использования браузера.

**Преимущества:**
- Высокая скорость выполнения
- Стабильность и надежность
- Простота отладки
- Полное покрытие API

**Пример:**
```python
def test_get_moderation_panel_data(admin_client):
    """Тест получения данных панели модерации."""
    data = admin_client.get_moderation_panel_data(limit=100)
    assert isinstance(data, list)
    assert len(data) > 0
```

### 2. UI Тесты
Тестирование пользовательского интерфейса с помощью Playwright.

**Преимущества:**
- Проверка пользовательского опыта
- Тестирование сквозных сценариев
- Визуальная проверка элементов
- Работа с реальным браузером

**Пример:**
```python
def test_login_ui(page: Page):
    """Тест авторизации через UI."""
    page.goto("https://bll.by/login")
    page.fill("input[name='username']", "test_user")
    page.fill("input[name='password']", "test_password")
    page.click("button[type='submit']")
    assert page.is_visible("text=Добро пожаловать")
```

### 3. Интеграционные Тесты
Комплексное тестирование взаимодействия компонентов системы.

**Преимущества:**
- Проверка сквозных сценариев
- Интеграция с внешними системами
- Реалистичные условия тестирования
- Высокая ценность для бизнеса

**Пример:**
```python
def test_question_submission_flow(user_client, admin_client):
    """Тест полного цикла отправки и публикации вопроса."""
    # Пользователь отправляет вопрос
    question_text = "Тестовый вопрос"
    success = user_client.submit_question(question_text)
    assert success
    
    # Админ публикует вопрос
    question = admin_client.find_question(text=question_text)
    response = admin_client.publish_question(question['id'])
    assert response.success
```

### 4. E2E Тесты
End-to-End тестирование полных пользовательских сценариев.

**Преимущества:**
- Проверка всей системы целиком
- Реалистичные пользовательские сценарии
- Высокая уверенность в качестве
- Бизнес-ориентированные проверки

## Авторизация и безопасность

### Современная система авторизации

#### 1. Автоматическая авторизация
```python
# Новый подход - автоматически
def test_with_auto_auth(admin_client):
    # Клиент уже авторизован
    data = admin_client.get("/admin/data")
    assert data is not None

# Старый подход - вручную
def test_with_manual_auth():
    auth_manager = SmartAuthManager()
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")
    # ... много кода для авторизации
```

#### 2. Поддержка разных ролей
```python
@pytest.mark.parametrize("role", ["admin", "user", "moderator"])
def test_different_roles(role, get_client_by_role):
    """Тест с разными ролями пользователей."""
    client = get_client_by_role(role)
    response = client.get("/api/data")
    assert response.status_code in [200, 403]  # Разные права доступа
```

#### 3. Безопасная работа с секретами
```python
# Использование secrets manager
from config.secrets_manager import secrets_manager

config = secrets_manager.get_test_config()
username = config.auth.username  # Безопасное получение данных
```

### Антибот защита

#### 1. Stealth режим браузера
```python
# Автоматическая настройка антибот защиты
def create_stealth_browser(playwright_instance, headless: bool = True):
    """Создает браузер с настройками для обхода антибот защиты."""
    args = [
        "--disable-blink-features=AutomationControlled",
        "--disable-automation",
        "--no-sandbox",
        # ... другие флаги
    ]
    return playwright_instance.chromium.launch(headless=headless, args=args)
```

#### 2. Параметр allow-session для headless режима
```python
from framework.utils.url_utils import add_allow_session_param, is_headless

def test_with_allow_session(page: Page):
    """Тест с параметром allow-session для headless режима."""
    url = add_allow_session_param("https://bll.by/page", is_headless())
    page.goto(url)
    # ... тест продолжается
```

## API Тестирование

### Рекомендации по API тестированию

#### 1. Использование новых API клиентов
```python
from framework.api.admin_client import AdminAPIClient

def test_admin_api_functionality():
    """Тест функциональности админ API."""
    client = AdminAPIClient(role="admin")
    
    # Получение данных панели модерации
    data = client.get_moderation_panel_data(limit=50)
    assert len(data) > 0
    
    # Поиск конкретного вопроса
    question = client.find_question(mode="latest")
    assert question is not None
    
    # Публикация вопроса
    response = client.publish_question(question['id'])
    assert response.success
```

#### 2. Обработка ошибок и retry логика
```python
def test_api_with_retry_logic(admin_client):
    """Тест с автоматической retry логикой."""
    # Клиент автоматически обрабатывает 401/419 ошибки
    try:
        data = admin_client.get("/api/protected-endpoint")
        assert data is not None
    except Exception as e:
        # Логирование ошибки
        admin_client.logger.error(f"API ошибка: {e}")
        raise
```

#### 3. Типизированные ответы
```python
def test_typed_responses(admin_client):
    """Тест с типизированными ответами."""
    response = admin_client.publish_question(123)
    
    # Структурированный ответ
    assert response.success is True
    assert response.status_code == 200
    assert response.data is not None
    assert hasattr(response, 'message')  # Автодополнение работает
```

### Мониторинг и метрики API тестов

#### 1. Производительность
```python
import time

def test_api_performance(admin_client):
    """Тест производительности API."""
    start_time = time.time()
    
    response = admin_client.get_moderation_panel_data(limit=100)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    assert execution_time < 5.0  # Должно выполняться менее 5 секунд
    assert len(response) == 100
```

#### 2. Стабильность
```python
@pytest.mark.flaky(reruns=3)
def test_api_stability(admin_client):
    """Тест стабильности API с повторными попытками."""
    response = admin_client.get("/api/unstable-endpoint")
    assert response.success
```

## UI Тестирование

### Best Practices для UI тестов

#### 1. Использование data-testid локаторов
```python
def test_with_data_testid(page: Page):
    """Тест с использованием data-testid локаторов."""
    page.goto("https://bll.by")
    
    # Приоритет: data-testid
    menu_button = page.locator("[data-testid='menu-button']")
    menu_button.click()
    
    # Второй приоритет: ARIA атрибуты
    login_link = page.locator("[aria-label='Войти']")
    login_link.click()
```

#### 2. Явные ожидания вместо time.sleep
```python
def test_with_explicit_waits(page: Page):
    """Тест с явными ожиданиями."""
    page.goto("https://bll.by")
    
    # Правильно: явное ожидание
    login_button = page.locator("button.login")
    login_button.wait_for(state="visible", timeout=10000)
    login_button.click()
    
    # Неправильно: time.sleep
    # time.sleep(5)  # ❌ Не используйте это
```

#### 3. Скриншоты для диагностики
```python
def test_with_screenshots(page: Page):
    """Тест со скриншотами для диагностики."""
    page.goto("https://bll.by")
    
    # Скриншот перед действием
    page.screenshot(path="before_login.png")
    
    page.fill("input[name='username']", "test_user")
    page.fill("input[name='password']", "test_password")
    page.click("button[type='submit']")
    
    # Скриншот после действия
    page.screenshot(path="after_login.png")
    
    assert page.is_visible("text=Добро пожаловать")
```

### Рекомендации по UI тестированию

#### 1. Антибот настройки
```python
# Использование антибот настроек из conftest.py
def test_with_anti_bot_settings(page: Page, anti_bot_browser_context_args):
    """Тест с антибот настройками."""
    # Настройки уже применены через фикстуру
    page.goto("https://bll.by")
    # ... тест продолжается
```

#### 2. Headless режим с allow-session
```python
def test_headless_with_allow_session(page: Page):
    """Тест в headless режиме с allow-session параметром."""
    from framework.utils.url_utils import add_allow_session_param
    
    url = add_allow_session_param("https://bll.by", True)  # headless=True
    page.goto(url)
    # ... тест продолжается
```

## Best Practices

### Общие рекомендации

#### 1. Структура тестов
```python
import pytest
import allure
from typing import Any

@allure.title("Описательное название теста")
@allure.description("Подробное описание теста и его целей")
@pytest.mark.api
@pytest.mark.regression
def test_example(admin_client):
    """Docstring с описанием теста."""
    
    # Arrange - Подготовка данных
    test_data = {
        "title": "Тестовый заголовок",
        "content": "Тестовое содержание"
    }
    
    # Act - Выполнение действий
    with allure.step("Создание тестовых данных"):
        result = admin_client.create_item(test_data)
    
    # Assert - Проверка результатов
    with allure.step("Проверка результата"):
        assert result.success
        assert result.data["title"] == test_data["title"]
```

#### 2. Использование Allure шагов
```python
def test_with_allure_steps(admin_client):
    """Тест с Allure шагами для лучшей читаемости."""
    
    with allure.step("Подготовка тестовых данных"):
        question_text = "Тестовый вопрос для публикации"
        expected_status = "published"
    
    with allure.step("Отправка вопроса"):
        success = admin_client.submit_question(question_text)
        assert success
    
    with allure.step("Проверка статуса вопроса"):
        question = admin_client.find_question(text=question_text)
        assert question is not None
        assert question["status"] == expected_status
```

#### 3. Параметризация тестов
```python
@pytest.mark.parametrize("user_role,expected_access", [
    ("admin", True),
    ("user", False),
    ("moderator", True),
], ids=["admin_access", "user_no_access", "moderator_access"])
def test_role_based_access(get_client_by_role, user_role, expected_access):
    """Параметризованный тест доступа по ролям."""
    client = get_client_by_role(user_role)
    response = client.get("/admin/panel")
    
    if expected_access:
        assert response.status_code == 200
    else:
        assert response.status_code == 403
```

### Технические рекомендации

#### 1. Обработка ошибок
```python
def test_with_proper_error_handling(admin_client):
    """Тест с правильной обработкой ошибок."""
    
    try:
        response = admin_client.get("/api/non-existent-endpoint")
        assert response.status_code == 404
    except Exception as e:
        # Логирование ошибки для диагностики
        admin_client.logger.error(f"Неожиданная ошибка: {e}")
        raise  # Перебрасываем исключение для правильной обработки pytest
```

#### 2. Работа с тестовыми данными
```python
from framework.utils.question_factory import QuestionFactory

@pytest.fixture
def test_question_data():
    """Фикстура для генерации тестовых данных."""
    factory = QuestionFactory()
    return factory.generate_question(category="регистрация")

def test_with_test_data(admin_client, test_question_data):
    """Тест с использованием сгенерированных данных."""
    success = admin_client.submit_question(test_question_data)
    assert success
```

#### 3. Изоляция тестов
```python
@pytest.mark.isolated
def test_isolated_context(admin_client):
    """Тест с изолированным контекстом."""
    # Каждый тест получает чистый клиент
    # Нет влияния от предыдущих тестов
    response = admin_client.get("/api/data")
    assert response.success
```

## Запуск тестов

### Быстрый старт

#### 1. Самые быстрые команды:
```bash
# Быстрый запуск (15 секунд)
scripts/run_tests_quick.bat

# Параллельный запуск (20 секунд)
scripts/run_tests_parallel.bat

# Запуск примеров нового фреймворка
pytest tests/integration/test_new_framework_example.py -v
```

#### 2. Запуск с Allure отчетами:
```bash
# Запуск с генерацией Allure отчетов
pytest tests/ -v --alluredir=./allure-results

# Просмотр отчета
allure serve ./allure-results
```

### Рекомендованные режимы запуска

#### 1. Для CI/CD:
```bash
# Только API тесты для быстрой проверки
pytest tests/ -m "api and not slow" -v --tb=short

# Параллельный запуск для скорости
pytest tests/ -n 10 -m "api" -v
```

#### 2. Для локальной разработки:
```bash
# Запуск конкретного теста с подробным выводом
pytest tests/integration/test_new_framework_example.py::test_publish_question_with_new_framework -v -s

# Запуск с GUI для отладки
pytest tests/ --headed -v -s

# Запуск с Allure отчетами
pytest tests/ -v --alluredir=./allure-results
allure serve ./allure-results
```

#### 3. Для регрессионного тестирования:
```bash
# Полный регрессионный набор
pytest tests/ -m "regression" -v

# Специфические маркеры
pytest tests/ -m "api or auth" -v
```

### Мониторинг производительности

#### 1. Замер времени выполнения:
```bash
# Запуск с замером времени
time pytest tests/integration/test_new_framework_example.py -v

# Использование pytest-benchmark
pytest tests/ --benchmark-only -v
```

#### 2. Проверка стабильности:
```bash
# Запуск с повторными попытками
pytest tests/ --reruns 3 --reruns-delay 1 -v

# Проверка flaky тестов
pytest tests/ --flake-finder --flake-runs=5 -v
```

## Отладка и диагностика

### Инструменты отладки

#### 1. Логирование:
```python
import logging

def test_with_logging(admin_client):
    """Тест с подробным логированием."""
    # Включение DEBUG логов
    admin_client.logger.setLevel(logging.DEBUG)
    
    response = admin_client.get("/api/data")
    admin_client.logger.debug(f"Получен ответ: {response}")
    
    assert response.success
```

#### 2. Allure аттачменты:
```python
import allure
import json

def test_with_attachments(admin_client):
    """Тест с Allure аттачментами."""
    
    response = admin_client.get("/api/data")
    
    # Аттачмент JSON данных
    allure.attach(
        json.dumps(response.data, indent=2, ensure_ascii=False),
        name="API Response Data",
        attachment_type=allure.attachment_type.JSON
    )
    
    # Аттачмент текстовой информации
    allure.attach(
        f"Status Code: {response.status_code}\nSuccess: {response.success}",
        name="Response Summary",
        attachment_type=allure.attachment_type.TEXT
    )
```

#### 3. Скриншоты для UI тестов:
```python
def test_with_screenshots(page: Page):
    """UI тест со скриншотами."""
    
    page.goto("https://bll.by")
    page.screenshot(path="screenshots/homepage.png")
    
    with allure.step("Авторизация"):
        page.fill("input[name='username']", "test_user")
        page.screenshot(path="screenshots/login_filled.png")
        page.click("button[type='submit']")
    
    # Скриншот после авторизации
    page.screenshot(path="screenshots/after_login.png")
```

### Устранение распространенных проблем

#### 1. Проблемы с авторизацией:
```bash
# Проверка кук
python scripts/maintenance/cookie_tester.py

# Обновление кук через API
python scripts/run_auth_tests.py api
```

#### 2. Проблемы с антибот защитой:
```bash
# Запуск в GUI режиме
pytest tests/ --headed -v

# Использование stealth настроек
pytest tests/ --test-browser=chromium -v
```

#### 3. Проблемы с производительностью:
```bash
# Запуск с профилированием
pytest tests/ --profile -v

# Проверка времени выполнения
pytest tests/ --durations=10 -v
```

### Метрики и мониторинг

#### 1. Статистика выполнения:
```python
def test_with_metrics_collection(admin_client):
    """Тест со сбором метрик."""
    import time
    
    start_time = time.time()
    start_memory = get_memory_usage()  # Псевдокод
    
    response = admin_client.get("/api/data")
    
    end_time = time.time()
    end_memory = get_memory_usage()  # Псевдокод
    
    execution_time = end_time - start_time
    memory_used = end_memory - start_memory
    
    # Логирование метрик
    admin_client.logger.info(f"Время выполнения: {execution_time:.2f} сек")
    admin_client.logger.info(f"Использовано памяти: {memory_used} MB")
    
    assert response.success
```

#### 2. Сравнение производительности:
```python
def test_performance_comparison(old_approach, new_approach):
    """Сравнение производительности старого и нового подходов."""
    import time
    
    # Старый подход
    start_time = time.time()
    old_result = old_approach()
    old_time = time.time() - start_time
    
    # Новый подход
    start_time = time.time()
    new_result = new_approach()
    new_time = time.time() - start_time
    
    # Новый подход должен быть быстрее
    assert new_time < old_time
    assert old_result == new_result  # Результаты должны совпадать
```

## Заключение

Новый унифицированный фреймворк предоставляет мощные инструменты для упрощения и ускорения написания автоматизированных тестов. Следуя рекомендациям из этого руководства, вы сможете:

- **Писать более читаемый и поддерживаемый код**
- **Сократить время на написание тестов в 2-3 раза**
- **Повысить стабильность и надежность тестов**
- **Упростить отладку и диагностику проблем**
- **Использовать современные подходы к тестированию**

### Следующие шаги:
1. **Изучите примеры** в `tests/integration/test_new_framework_example.py`
2. **Попробуйте написать свой первый тест** с новым фреймворком
3. **Ознакомьтесь с документацией** в `docs/NEW_FRAMEWORK_GUIDE.md`
4. **Присоединяйтесь к миграции** существующих тестов

### Поддержка:
- **Lead SDET Architect** - для архитектурных вопросов
- **Code review** - для проверки новых тестов
- **Team meetings** - для обсуждения проблем и улучшений

---
*Документация регулярно обновляется. Последнее обновление: 2025*