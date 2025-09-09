# Руководство по работе с фреймворком автоматизации тестирования

## Введение

Это руководство поможет вам эффективно использовать фреймворк автоматизации тестирования
для написания надежных и поддерживаемых тестов.

## Основные изменения

### 1. Базовый класс тестов
**Старый подход:**
```python
import pytest
import requests
from framework.utils.auth_utils import get_session_cookie

def test_old_way():
    # Ручная настройка всего
    cookie = get_session_cookie("admin")
    session = requests.Session()
    session.cookies.set("test_joint_session", cookie)
    # ... остальная логика
```

**Новый подход:**
```python
import pytest
import allure
from framework.test_bases.api_test_base import APITestBase

class TestNewWay(APITestBase):
    @pytest.mark.api
    def test_new_way(self):
        # Все уже настроено автоматически
        result = self.admin_client.create_test_question("вопрос")
        assert result is True
```

### 2. Работа с API
**Старый подход:**
```python
def test_old_api():
    session = get_authorized_session("admin")
    response = session.post(
        "https://bll.by/api/questions",
        json={"text": "тестовый вопрос"}
    )
    assert response.status_code == 200
```

**Новый подход:**
```python
def test_new_api(self):
    result = self.admin_client.create_test_question("тестовый вопрос")
    assert result is True  # Метод возвращает bool, обработка ошибок внутри
```

### 3. Фикстуры
**Старый подход:**
```python
@pytest.fixture
def admin_session():
    return get_authorized_session("admin")

def test_with_fixture(admin_session):
    # Используем фикстуру
    pass
```

**Новый подход:**
```python
class TestWithFixtures(APITestBase):
    def test_with_automatic_fixtures(self):
        # self.admin_client доступен автоматически
        # self.moder_client доступен автоматически  
        # self.user_client доступен автоматически
        # self.question_factory доступен автоматически
        # self.logger доступен автоматически
        pass
```

## Пошаговая миграция

### Шаг 1: Создание нового класса теста
**Было:**
```python
# tests/integration/test_old_questions.py
import pytest

def test_create_question():
    # Старая реализация
    pass
```

**Стало:**
```python
# tests/integration/test_new_questions.py
import pytest
import allure
from framework.test_bases.api_test_base import APITestBase

class TestQuestionManagement(APITestBase):
    @allure.title("Создание вопроса")
    @pytest.mark.api
    @pytest.mark.question
    def test_create_question(self):
        # Новая реализация
        pass
```

### Шаг 2: Миграция логики создания вопросов
**Было:**
```python
def test_create_question_old():
    session = get_authorized_session("admin")
    question_text = "Тестовый вопрос"
    
    response = session.post(
        "https://bll.by/api/questions",
        json={"text": question_text, "category": "test"}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
```

**Стало:**
```python
def test_create_question_new(self):
    with allure.step("Генерация тестового вопроса"):
        test_question = self.question_factory.generate_question()
    
    with allure.step("Создание вопроса через API"):
        result = self.admin_client.create_test_question(test_question)
        assert result is True
```

### Шаг 3: Миграция поиска и проверки вопросов
**Было:**
```python
def test_search_question_old():
    session = get_authorized_session("moderator")
    
    response = session.get(
        "https://bll.by/api/questions",
        params={"query": "тестовый"}
    )
    
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) > 0
```

**Стало:**
```python
def test_search_question_new(self):
    with allure.step("Поиск вопросов"):
        questions = self.moder_client.search_questions(query="тестовый")
        assert questions is not None
        assert len(questions) > 0
```

### Шаг 4: Миграция ответов на вопросы
**Было:**
```python
def test_answer_question_old():
    session = get_authorized_session("moderator")
    
    response = session.post(
        "https://bll.by/api/questions/123/answer",
        json={"answer": "Тестовый ответ"}
    )
    
    assert response.status_code == 200
```

**Стало:**
```python
def test_answer_question_new(self):
    with allure.step("Ответ на вопрос"):
        success = self.moder_client.answer_question(
            question_id="123",
            answer_text="Тестовый ответ"
        )
        assert success is True
```

## Пример полной миграции теста

### Старый тест
```python
# tests/integration/test_old_workflow.py
import pytest
import requests
from framework.utils.auth_utils import get_authorized_session

def test_question_workflow_old():
    # 1. Создание вопроса
    admin_session = get_authorized_session("admin")
    question_text = "Тестовый вопрос для workflow"
    
    create_response = admin_session.post(
        "https://bll.by/api/questions",
        json={"text": question_text}
    )
    assert create_response.status_code == 200
    
    # 2. Поиск вопроса
    mod_session = get_authorized_session("moderator")
    search_response = mod_session.get(
        "https://bll.by/api/questions",
        params={"query": question_text}
    )
    assert search_response.status_code == 200
    questions = search_response.json()
    assert len(questions) > 0
    
    question_id = questions[0]["id"]
    
    # 3. Ответ на вопрос
    answer_response = mod_session.post(
        f"https://bll.by/api/questions/{question_id}/answer",
        json={"answer": "Ответ на тестовый вопрос"}
    )
    assert answer_response.status_code == 200
```

### Новый тест
```python
# tests/integration/test_new_workflow.py
import pytest
import allure
from framework.test_bases.api_test_base import APITestBase

class TestQuestionWorkflow(APITestBase):
    @allure.title("Полный workflow вопроса")
    @allure.description("Создание → поиск → ответ")
    @pytest.mark.api
    @pytest.mark.question
    @pytest.mark.regression
    def test_question_workflow_new(self):
        with allure.step("1. Создание вопроса"):
            test_question = self.question_factory.generate_question()
            result = self.admin_client.create_test_question(test_question)
            assert result is True
        
        with allure.step("2. Поиск вопроса"):
            questions = self.moder_client.search_questions(query=test_question)
            assert questions is not None
            assert len(questions) > 0
            question_id = questions[0]["id"]
        
        with allure.step("3. Ответ на вопрос"):
            success = self.moder_client.answer_question(
                question_id=question_id,
                answer_text="Ответ на тестовый вопрос"
            )
            assert success is True
```

## Миграция фикстур

### Старые фикстуры (удаляются)
```python
# Большинство старых фикстур больше не нужны
@pytest.fixture
def admin_session():
    pass

@pytest.fixture  
def moderator_session():
    pass
```

### Новые автоматические фикстуры
```python
# Все доступно в базовом классе:
class TestExample(APITestBase):
    def test_something(self):
        # self.admin_client - готовый клиент администратора
        # self.moder_client - готовый клиент модератора
        # self.user_client - готовый клиент пользователя
        # self.question_factory - фабрика вопросов
        # self.logger - логгер
        pass
```

## Миграция маркеров pytest

### Старые маркеры
```python
@pytest.mark.integration
@pytest.mark.api_test
@pytest.mark.question_test
```

### Новые маркеры
```python
@pytest.mark.api          # API тесты
@pytest.mark.question     # Тесты вопросов
@pytest.mark.moderation   # Тесты модерации
@pytest.mark.smoke        # Smoke тесты
@pytest.mark.regression   # Регрессионные тесты
@pytest.mark.security     # Тесты безопасности
```

## Миграция обработки ошибок

### Старый подход
```python
def test_with_error_handling_old():
    try:
        session = get_authorized_session("admin")
        response = session.post("/api/questions", json={"text": ""})
        if response.status_code != 200:
            raise AssertionError(f"Ошибка: {response.status_code}")
    except Exception as e:
        print(f"Ошибка: {e}")
        raise
```

### Новый подход
```python
def test_with_error_handling_new(self):
    with allure.step("Попытка создания вопроса с пустым текстом"):
        success = self.admin_client.create_test_question("")
        # Клиент автоматически обрабатывает ошибки и логирует их
        assert success is False, "Система должна отклонить пустой вопрос"
```

## Рекомендации по миграции

### 1. Постепенная миграция
- Не мигрируйте все тесты сразу
- Начните с новых тестов
- Постепенно переписывайте старые тесты
- Сохраняйте обратную совместимость

### 2. Тестирование после миграции
- Запустите мигрированные тесты
- Сравните результаты с оригинальными
- Убедитесь что логика не изменилась
- Проверьте отчеты Allure

### 3. Обновление документации
- Обновите README.md
- Добавьте ссылки на новую документацию
- Удалите устаревшие руководства
- Обновите примеры

### 4. Обучение команды
- Проведите демонстрацию нового фреймворка
- Объясните преимущества
- Покажите примеры миграции
- Ответьте на вопросы

## Частые проблемы и решения

### Проблема 1: "Атрибут не найден"
**Ошибка:**
```
AttributeError: 'TestExample' object has no attribute 'admin_client'
```

**Решение:** Убедитесь что класс наследуется от `APITestBase`:
```python
from framework.test_bases.api_test_base import APITestBase

class TestExample(APITestBase):  # ВАЖНО: наследование
    def test_something(self):
        # Теперь admin_client доступен
        pass
```

### Проблема 2: "Метод не найден"
**Ошибка:**
```
AttributeError: 'AdminAPIClient' object has no attribute 'some_method'
```

**Решение:** Проверьте доступные методы в клиенте или добавьте новый метод:
```python
# Проверьте framework/api/admin_client.py
# Или добавьте метод в клиент
```

### Проблема 3: "Фикстура не найдена"
**Ошибка:**
```
fixture 'some_old_fixture' not found
```

**Решение:** Замените старые фикстуры на автоматические:
```python
# Вместо: def test_old(some_old_fixture):
# Используйте: 
class TestNew(APITestBase):
    def test_new(self):
        # self.admin_client вместо some_old_fixture
        pass
```

## Обратная совместимость

Новый фреймворк спроектирован с учетом обратной совместимости:
- Старые тесты продолжают работать
- Старые фикстуры остаются доступны
- Можно постепенно мигрировать
- Нет необходимости в массовом рефакторинге

## Поддержка

При возникновении проблем с миграцией:
1. Обратитесь к новой документации
2. Изучите примеры тестов
3. Свяжитесь с командой QA
4. Создайте issue в репозитории

## Заключение

Миграция на новый фреймворк значительно упростит написание и поддержку тестов,
обеспечит лучшую читаемость кода и повысит надежность тестирования.
