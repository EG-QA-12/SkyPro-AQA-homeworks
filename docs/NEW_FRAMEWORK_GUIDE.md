# Новый фреймворк для автоматизации тестирования

## Обзор

Новый фреймворк представляет собой современное решение для автоматизации тестирования, построенное на принципах SOLID и обеспечивающее высокую читаемость, поддерживаемость и расширяемость тестов.

## Основные преимущества

### 1. Централизованная авторизация
- Автоматическая авторизация для всех тестов
- Поддержка различных ролей пользователей
- Безопасное хранение учетных данных
- Автоматическое обновление сессий

### 2. Типизированные API клиенты
- Строгая типизация для предотвращения ошибок
- Автодополнение в IDE
- Четко определенные интерфейсы
- Встроенная обработка ошибок

### 3. Управляемые фикстуры
- Автоматическое управление жизненным циклом
- Изоляция тестов
- Повторное использование ресурсов
- Централизованная конфигурация

### 4. Интеграция с Allure
- Богатые отчеты с шагами тестов
- Прикрепление артефактов
- Структурированное логирование
- Автоматическая генерация документации

## Архитектура

### Базовый класс тестов
```python
from framework.test_bases.api_test_base import APITestBase

class TestExample(APITestBase):
    def test_something(self):
        # Доступны готовые клиенты:
        # self.admin_client - клиент администратора
        # self.moder_client - клиент модератора
        # self.user_client - клиент обычного пользователя
        # self.question_factory - фабрика вопросов
        # self.logger - логгер
        pass
```

### API клиенты
```python
# Создание вопроса
result = self.admin_client.create_test_question("Текст вопроса")

# Поиск вопросов
questions = self.moder_client.search_questions(query="поиск")

# Ответ на вопрос
success = self.moder_client.answer_question(question_id, "Ответ")
```

### Фикстуры
```python
# Автоматически доступны в базовом классе:
# - admin_client: API клиент администратора
# - moder_client: API клиент модератора
# - user_client: API клиент пользователя
# - question_factory: Фабрика тестовых вопросов
# - logger: Логгер для тестов
```

## Примеры использования

### Базовый тест
```python
import pytest
import allure
from framework.test_bases.api_test_base import APITestBase

class TestQuestionManagement(APITestBase):
    @allure.title("Создание вопроса через API")
    @pytest.mark.api
    @pytest.mark.question
    def test_create_question_via_api(self):
        with allure.step("Подготовка тестовых данных"):
            test_question = self.question_factory.generate_question()
        
        with allure.step("Создание вопроса через API"):
            result = self.admin_client.create_test_question(test_question)
            assert result is True
```

### Тесты публикации вопросов
```python
# tests/integration/test_publish_question_new.py
class TestQuestionPublication(APITestBase):
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.question
    def test_publish_question_via_admin_api(self):
        # Создание и публикация вопроса
        test_question = self.question_factory.generate_question()
        success = self.admin_client.create_test_question(test_question)
        success = self.moder_client.publish_question(question_id)
```

### Тесты публикации ответов
```python
# tests/integration/test_publish_answer_new.py
class TestAnswerPublication(APITestBase):
    @pytest.mark.api
    @pytest.mark.moderation
    @pytest.mark.answer
    def test_publish_answer_to_question(self):
        # Создание вопроса и ответа на него
        test_question = self.question_factory.generate_question()
        success = self.admin_client.create_test_question(test_question)
        success = self.moder_client.answer_question(question_id, "Ответ")
```

### Тест с параметризацией
```python
import pytest
from framework.utils.enums import UserRole

@pytest.mark.parametrize("role", [
    UserRole.ADMIN,
    UserRole.MODERATOR,
    UserRole.USER
], ids=["admin", "moderator", "user"])
def test_role_based_access(self, role):
    if role == UserRole.ADMIN:
        client = self.admin_client
    # ... логика теста
```

## Рекомендации по использованию

### 1. Структура тестов
- Используйте базовый класс `APITestBase`
- Разделяйте тесты по функциональности на классы
- Используйте Allure аннотации для документирования
- Следуйте паттерну AAA (Arrange-Act-Assert)

### 2. Работа с данными
- Используйте `question_factory` для генерации тестовых данных
- Не хардкодьте учетные данные
- Используйте enums для статусов и ролей
- Очищайте тестовые данные при необходимости

### 3. Логирование и отчетность
- Используйте `self.logger` для логирования
- Добавляйте шаги через `allure.step()`
- Прикрепляйте артефакты через Allure
- Используйте содержательные названия тестов

## Маркеры тестов

### Стандартные маркеры
- `@pytest.mark.api` - API тесты
- `@pytest.mark.ui` - UI тесты
- `@pytest.mark.smoke` - Smoke тесты
- `@pytest.mark.regression` - Регрессионные тесты
- `@pytest.mark.question` - Тесты вопросов
- `@pytest.mark.moderation` - Тесты модерации
- `@pytest.mark.security` - Тесты безопасности

### Запуск тестов
```bash
# Smoke тесты
pytest -m smoke

# API тесты
pytest -m api

# Тесты с определенной ролью
pytest -m "api and question"
```

## Обработка ошибок

Фреймворк автоматически обрабатывает:
- Ошибки авторизации
- Таймауты запросов
- Некорректные ответы API
- Проблемы с сетью

```python
# Ошибки автоматически логируются и прикрепляются к отчету
with allure.step("Операция которая может упасть"):
    try:
        result = client.some_operation()
        assert result is True
    except APIError as e:
        # Ошибка будет автоматически прикреплена к отчету
        raise
```

## Расширение фреймворка

### Добавление новых API клиентов
```python
# framework/api/new_client.py
from framework.api.base_client import BaseAPIClient

class NewAPIClient(BaseAPIClient):
    def __init__(self, base_url: str, session_cookie: str):
        super().__init__(base_url, session_cookie)
    
    def new_method(self) -> bool:
        # Реализация нового метода
        pass
```

### Добавление новых фикстур
```python
# framework/new_fixtures/custom_fixtures.py
import pytest
from framework.api.new_client import NewAPIClient

@pytest.fixture
def new_client(admin_session_cookie):
    return NewAPIClient("https://api.example.com", admin_session_cookie)
```

## Лучшие практики

### 1. Названия тестов
```python
# Хорошо
def test_create_question_via_api_returns_success():
    pass

# Плохо
def test_1():
    pass
```

### 2. Структура шагов
```python
def test_example(self):
    with allure.step("Подготовка данных"):
        # Подготовка
        pass
    
    with allure.step("Выполнение действия"):
        # Действие
        pass
    
    with allure.step("Проверка результата"):
        # Проверка
        pass
```

### 3. Работа с assertions
```python
# Хорошо - содержательные сообщения об ошибках
assert result is True, "Не удалось создать вопрос"

# Плохо - нет сообщения
assert result

# Плохо - слишком общее сообщение
assert result, "Ошибка"
```

## Миграция со старого фреймворка

### Основные изменения
1. **Базовый класс**: Вместо самостоятельной настройки используйте `APITestBase`
2. **Клиенты**: Вместо ручной работы с requests используйте типизированные клиенты
3. **Фикстуры**: Большинство фикстур теперь доступны автоматически
4. **Логирование**: Используйте `self.logger` вместо print

### Пример миграции
```python
# Старый подход
def test_old_way():
    session = get_session()
    response = session.post("/api/questions", data={"text": "вопрос"})
    assert response.status_code == 200

# Новый подход
def test_new_way(self):
    result = self.admin_client.create_test_question("вопрос")
    assert result is True
```

## Поддержка и развитие

Фреймворк активно развивается и поддерживается командой QA.
Новые функции добавляются регулярно, обратная совместимость сохраняется.

### Обратная связь
- Создавайте issues в репозитории
- Предлагайте улучшения через pull requests
- Участвуйте в code review

### Документация
- Эта документация обновляется вместе с фреймворком
- Примеры кода всегда актуальны
- API документация генерируется автоматически