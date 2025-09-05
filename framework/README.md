# Новый унифицированный фреймворк для автоматизированных тестов

## Обзор

Новый унифицированный фреймворк предоставляет современный, типизированный и удобный подход к написанию автоматизированных тестов. Фреймворк включает в себя:

- **API клиенты** с автоматической авторизацией и обработкой ошибок
- **Централизованные фикстуры** для повторного использования компонентов
- **Базовые классы тестов** для упрощения написания тестов
- **Вспомогательные утилиты** для типичных операций

## Структура фреймворка

```
framework/
├── api/                    # Современные API клиенты
│   ├── base_client.py     # Базовый API клиент с retry логикой
│   └── admin_client.py    # Административный клиент
├── new_fixtures/          # Централизованные фикстуры
│   ├── auth_fixtures.py   # Фикстуры авторизации
│   ├── moderation_fixtures.py # Фикстуры модерации
│   └── conftest.py        # Конфигурация фикстур
├── test_bases/            # Базовые классы тестов
│   └── api_test_base.py   # Базовые классы для API тестов
├── utils/                 # Существующие утилиты
└── README.md             # Этот файл
```

## Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск примеров тестов

```bash
# Запуск примеров нового фреймворка
pytest tests/integration/test_new_framework_example.py -v

# Запуск с Allure отчетами
pytest tests/integration/test_new_framework_example.py -v --alluredir=./allure-results
allure serve ./allure-results
```

## Основные компоненты

### 1. API Клиенты

#### BaseAPIClient
Базовый клиент для работы с API, предоставляющий:
- Автоматическую авторизацию и обновление кук
- Обработку CSRF токенов
- Retry логику для 401/419 ошибок
- Типизированные ответы

##### Система авторизации
BaseAPIClient интегрирован с системой авторизации, которая поддерживает несколько источников получения кук:
1. **Переменные окружения**: `SESSION_COOKIE_{ROLE}` или `SESSION_COOKIE`
2. **Локальные файлы**: `cookies/{role}_session.txt` или `cookies/{role}_cookies.json`
3. **API-логин**: автоматический логин через `APIAuthManager`

При инициализации клиент автоматически получает валидную сессионную куку через `SmartAuthManager`,
который реализует интеллектуальное кэширование и обновление сессий.

```python
from framework.api.base_client import BaseAPIClient

# Клиент автоматически авторизуется при создании
client = BaseAPIClient(base_url="https://expert.bll.by", role="admin")
response = client.get("/admin/posts")
```

```python
from framework.api.base_client import BaseAPIClient

client = BaseAPIClient(base_url="https://expert.bll.by", role="admin")
response = client.get("/admin/posts")
```

#### AdminAPIClient
Специализированный клиент для административных операций:
- Работа с панелью модерации
- Публикация вопросов и ответов
- Взятие записей в работу

```python
from framework.api.admin_client import AdminAPIClient

client = AdminAPIClient(role="admin")
question = client.find_question(mode="latest")
response = client.publish_question(question['id'])
```

### 2. Централизованные фикстуры

#### Фикстуры авторизации
```python
def test_with_admin_client(admin_client):
    # admin_client уже авторизован и готов к использованию
    response = admin_client.get_moderation_panel_data()
    assert len(response) > 0

def test_with_session_cookie(session_cookie):
    # session_cookie содержит валидную сессионную куку
    pass
```

#### Фикстуры модерации
```python
def test_with_moderation_helper(moderation_helper):
    question = moderation_helper.get_latest_question()
    assert question is not None
    
    success = moderation_helper.publish_question(question['id'])
    assert success
```

### 3. Базовые классы тестов

#### APITestBase
Базовый класс для всех API тестов:
```python
from framework.test_bases.api_test_base import APITestBase

class TestMyAPI(APITestBase):
    def test_something(self):
        response = self.client.get("/api/endpoint")
        self.assert_api_success(response)
```

#### Специализированные базовые классы
```python
from framework.test_bases.api_test_base import AdminAPITestBase, UserAPITestBase

class TestAdminFunctionality(AdminAPITestBase):
    def test_publish_question(self):
        question = self.get_latest_question()
        success = self.publish_question(question['id'])
        assert success

class TestUserFunctionality(UserAPITestBase):
    def test_submit_question(self):
        question_text = self.generate_test_question()
        success = self.submit_question(question_text)
        assert success
```

## Примеры использования

### Простой тест с фикстурами
```python
import pytest
import allure

@allure.title("Публикация вопроса")
@pytest.mark.api
def test_publish_question_with_fixtures(admin_client, fresh_question):
    """Публикация вопроса с использованием фикстур."""
    
    with allure.step("Публикация вопроса"):
        response = admin_client.publish_question(fresh_question['id'])
        assert response.success
```

### Параметризованный тест
```python
from framework.utils.enums import AnswerPublicationType

@pytest.mark.api
@pytest.mark.parametrize("publication_type", [
    AnswerPublicationType.PUBLISHED,
    AnswerPublicationType.DRAFT,
    AnswerPublicationType.REJECTED
])
class TestAnswerPublication(AdminAPITestBase):
    def test_answer_publication(self, publication_type):
        answer = self.get_latest_answer()
        response = self.client.publish_answer(
            answer_id=answer['id'],
            publication_type=publication_type
        )
        self.assert_api_success(response)
```

## Миграция с существующих тестов

### Старый подход (до фреймворка)
```python
def test_old_approach():
    # Много кода для авторизации
    auth_manager = SmartAuthManager()
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")
    
    # Много кода для получения данных
    parser = ModerationPanelParser()
    entries = parser.get_moderation_panel_data(session_cookie, limit=100)
    question = next((e for e in entries if e.get('type') == '?'), None)
    
    # Много кода для CSRF токенов
    tokens = fetch_csrf_tokens_from_panel(parser.session, "https://expert.bll.by")
    # ... и много другого кода
```

### Новый подход (с фреймворком)
```python
def test_new_approach(admin_client):
    # Все автоматически
    question = admin_client.find_question(mode="latest")
    response = admin_client.publish_question(question['id'])
    assert response.success
```

## Преимущества нового фреймворка

### 1. Упрощение кода
- Меньше boilerplate кода
- Автоматическая обработка авторизации
- Встроенные вспомогательные методы

### 2. Повышение надежности
- Автоматический retry при ошибках авторизации
- Централизованная обработка ошибок
- Типизированные ответы API

### 3. Улучшение читаемости
- Четкая структура и именование
- Интуитивно понятные методы
- Хорошая документация и примеры

### 4. Повторное использование
- Централизованные фикстуры
- Переиспользуемые базовые классы
- Общие утилиты и помощники

## Документация

- [Руководство по новому фреймворку](../docs/NEW_FRAMEWORK_GUIDE.md)
- [Примеры тестов](../tests/integration/test_new_framework_example.py)
- [API документация](../docs/API_REFERENCE.md)

## Рекомендации по использованию

1. **Используйте фикстуры** вместо ручного создания клиентов
2. **Наследуйтесь от базовых классов** для упрощения тестов
3. **Используйте встроенные методы проверки** (`assert_api_success`, `assert_json_response`)
4. **Добавляйте Allure шаги** для лучшей читаемости отчетов
5. **Используйте параметризацию** для тестирования разных сценариев

## Поддержка и развитие

Фреймворк активно развивается и поддерживается. Для вопросов и предложений:
- Создавайте issues в репозитории
- Обращайтесь к Lead SDET Architect
- Участвуйте в code review новых функций

## Лицензия

Этот фреймворк разработан специально для проекта BLL и не предназначен для внешнего использования.
