# 🏆 ЛУЧШИЕ ПРАКТИКИ ТЕСТИРОВАНИЯ

## 📋 ОБЗОР

Сборник лучших практик и рекомендаций по написанию эффективных, поддерживаемых и надежных тестов.

## 🎯 ОСНОВНЫЕ ПРИНЦИПЫ

### 1. Независимость тестов (Independence)
Каждый тест должен быть независимым и не зависеть от результатов других тестов.

```python
# ✅ Хорошо - независимые тесты
class TestQuestions(APITestBase):
    def test_create_question(self):
        """Создание вопроса."""
        question = self.question_factory.generate_question()
        result = self.admin_client.create_test_question(question)
        assert result is True
    
    def test_search_question(self):
        """Поиск вопроса."""
        # Каждый тест начинает с чистого состояния
        question = self.question_factory.generate_question()
        self.admin_client.create_test_question(question)
        
        questions = self.moder_client.search_questions(query=question)
        assert len(questions) > 0

# ❌ Плохо - зависимые тесты
class TestBadQuestions:
    question_id = None
    
    def test_create_question(self):
        """Создание вопроса."""
        # Сохраняем состояние в классе
        result = create_question("Тестовый вопрос")
        self.question_id = result["id"]
    
    def test_answer_question(self):
        """Ответ на вопрос - зависит от предыдущего теста."""
        # ПЛОХО: этот тест не может работать отдельно
        assert self.question_id is not None
        answer_question(self.question_id, "Ответ")
```

### 2. Повторяемость (Repeatability)
Тесты должны давать одинаковый результат при каждом запуске.

```python
# ✅ Хорошо - повторяемые тесты
def test_question_creation(self):
    """Создание вопроса с уникальными данными."""
    # Генерируем уникальные данные для каждого запуска
    question = self.question_factory.generate_question()
    result = self.admin_client.create_test_question(question)
    assert result is True

# ❌ Плохо - неповторяемые тесты
def test_specific_question(self):
    """Создание вопроса с жестко заданным текстом."""
    # ПЛОХО: если вопрос уже существует, тест упадет
    question = "Конкретный вопрос который уже может существовать"
    result = self.admin_client.create_test_question(question)
    assert result is True
```

### 3. Ясность и читаемость (Clarity)
Тесты должны быть понятными и легко читаемыми.

```python
# ✅ Хорошо - понятные имена
def test_admin_can_create_question(self):
    """Администратор может создать вопрос."""
    # Arrange
    test_question = self.question_factory.generate_question()
    
    # Act
    result = self.admin_client.create_test_question(test_question)
    
    # Assert
    assert result is True

# ❌ Плохо - непонятные имена
def test_1(self):
    question = "вопрос"
    result = create_question(question)
    assert result
```

## 🏗️ СТРУКТУРА ТЕСТОВ

### 1. Паттерн AAA (Arrange-Act-Assert)
Структурируйте тесты по трем четким секциям.

```python
def test_question_workflow(self):
    """Полный workflow вопроса."""
    
    # Arrange - Подготовка
    test_question = self.question_factory.generate_question()
    expected_answer = "Тестовый ответ"
    
    # Act - Действие
    create_result = self.admin_client.create_test_question(test_question)
    questions = self.moder_client.search_questions(query=test_question)
    question_id = questions[0]["id"] if questions else None
    answer_result = self.moder_client.answer_question(question_id, expected_answer)
    
    # Assert - Проверка
    assert create_result is True, "Не удалось создать вопрос"
    assert questions is not None, "Поиск вернул None"
    assert len(questions) > 0, "Вопрос не найден"
    assert answer_result is True, "Не удалось ответить на вопрос"
```

### 2. Использование шагов Allure
Добавляйте шаги для лучшей диагностики.

```python
import allure

def test_complex_workflow(self):
    """Комплексный workflow с шагами."""
    
    with allure.step("1. Создание тестового вопроса"):
        question = self.question_factory.generate_question()
        result = self.admin_client.create_test_question(question)
        assert result is True
    
    with allure.step("2. Поиск и проверка вопроса"):
        questions = self.moder_client.search_questions(query=question)
        assert questions is not None
        assert len(questions) > 0
    
    with allure.step("3. Ответ на вопрос"):
        question_id = questions[0]["id"]
        answer_result = self.moder_client.answer_question(question_id, "Ответ")
        assert answer_result is True
```

### 3. Организация тестовых данных
Используйте фабрики для генерации тестовых данных.

```python
# ✅ Хорошо - использование фабрик
def test_multiple_questions(self):
    """Тест с несколькими вопросами."""
    
    # Генерируем уникальные данные
    questions = [
        self.question_factory.generate_question(category="техника"),
        self.question_factory.generate_question(category="наука"),
        self.question_factory.generate_question(category="искусство")
    ]
    
    # Проверяем каждый вопрос
    for question in questions:
        result = self.admin_client.create_test_question(question)
        assert result is True

# ❌ Плохо - жестко заданные данные
def test_hardcoded_questions(self):
    """Тест с жестко заданными данными."""
    
    # ПЛОХО: данные не уникальны и могут конфликтовать
    questions = [
        "Вопрос о технике",
        "Вопрос о науке", 
        "Вопрос об искусстве"
    ]
    
    for question in questions:
        result = self.admin_client.create_test_question(question)
        # Может упасть если вопросы уже существуют
```

## 🔧 УПРАВЛЕНИЕ СОСТОЯНИЕМ

### 1. Очистка данных (Teardown)
Всегда очищайте созданные данные.

```python
import pytest

class TestQuestionManagement(APITestBase):
    """Тесты с правильной очисткой данных."""
    
    @pytest.fixture
    def cleanup_questions(self):
        """Фикстура для очистки вопросов."""
        created_questions = []
        
        yield created_questions
        
        # Очистка после теста
        for question_id in created_questions:
            try:
                self.admin_client.delete_question(question_id)
            except:
                pass  # Игнорируем ошибки при очистке
    
    def test_create_and_cleanup(self, cleanup_questions):
        """Тест с очисткой данных."""
        
        # Создаем вопрос
        question = self.question_factory.generate_question()
        result = self.admin_client.create_test_question(question)
        assert result is True
        
        # Сохраняем ID для очистки
        questions = self.moder_client.search_questions(query=question)
        if questions:
            cleanup_questions.append(questions[0]["id"])
```

### 2. Использование уникальных идентификаторов
Создавайте уникальные данные для каждого теста.

```python
import uuid
from datetime import datetime

class QuestionFactory:
    """Фабрика вопросов с уникальными данными."""
    
    @staticmethod
    def generate_question(prefix="Тестовый вопрос"):
        """Генерация уникального вопроса."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix} {timestamp} {unique_id}"
    
    @staticmethod
    def generate_answer():
        """Генерация уникального ответа."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"Тестовый ответ {timestamp}"

# Использование в тестах
def test_unique_questions(self):
    """Тест с уникальными вопросами."""
    
    question1 = self.question_factory.generate_question("Вопрос 1")
    question2 = self.question_factory.generate_question("Вопрос 2")
    
    # Эти вопросы гарантированно уникальны
    result1 = self.admin_client.create_test_question(question1)
    result2 = self.admin_client.create_test_question(question2)
    
    assert result1 is True
    assert result2 is True
```

## 🚀 ПРОИЗВОДИТЕЛЬНОСТЬ

### 1. Параллельное выполнение
Пишите тесты, которые могут выполняться параллельно.

```python
import pytest

class TestParallelizable(APITestBase):
    """Тесты, поддерживающие параллельное выполнение."""
    
    @pytest.mark.parallel
    def test_independent_operation_1(self):
        """Независимая операция 1."""
        question = self.question_factory.generate_question("Вопрос 1")
        result = self.admin_client.create_test_question(question)
        assert result is True
    
    @pytest.mark.parallel
    def test_independent_operation_2(self):
        """Независимая операция 2."""
        question = self.question_factory.generate_question("Вопрос 2")
        result = self.admin_client.create_test_question(question)
        assert result is True
    
    @pytest.mark.parallel
    def test_independent_operation_3(self):
        """Независимая операция 3."""
        question = self.question_factory.generate_question("Вопрос 3")
        result = self.admin_client.create_test_question(question)
        assert result is True
```

### 2. Оптимизация сетевых запросов
Минимизируйте количество сетевых запросов.

```python
# ✅ Хорошо - минимизация запросов
def test_efficient_search(self):
    """Эффективный поиск с минимальными запросами."""
    
    # Создаем несколько вопросов одним запросом (если возможно)
    questions = []
    for i in range(5):
        question = self.question_factory.generate_question()
        self.admin_client.create_test_question(question)
        questions.append(question)
    
    # Один поиск для всех вопросов
    all_questions = self.moder_client.search_questions(query="Тестовый")
    assert len(all_questions) >= 5

# ❌ Плохо - избыточные запросы
def test_inefficient_search(self):
    """Неэффективный поиск с множеством запросов."""
    
    # ПЛОХО: отдельный поиск для каждого вопроса
    for i in range(5):
        question = self.question_factory.generate_question()
        self.admin_client.create_test_question(question)
        questions = self.moder_client.search_questions(query=question)  # Отдельный запрос
        assert len(questions) > 0
```

### 3. Кэширование и переиспользование
Используйте кэширование для повторяющихся операций.

```python
import pytest

class TestWithCaching(APITestBase):
    """Тесты с использованием кэширования."""
    
    @pytest.fixture(scope="class")
    def cached_questions(self):
        """Кэширование тестовых данных на уровень класса."""
        questions = []
        
        # Создаем данные один раз для всего класса тестов
        for i in range(10):
            question = self.question_factory.generate_question()
            self.admin_client.create_test_question(question)
            questions.append(question)
        
        return questions
    
    def test_search_performance(self, cached_questions):
        """Тест производительности поиска."""
        # Используем кэшированные данные
        for question in cached_questions:
            results = self.moder_client.search_questions(query=question)
            assert len(results) > 0
```

## 🔍 ДИАГНОСТИКА И ОТЛАДКА

### 1. Подробное логирование
Добавляйте информативные логи для диагностики.

```python
import logging
import allure

def test_with_detailed_logging(self):
    """Тест с подробным логированием."""
    
    # Используем встроенный логгер
    self.logger.info("Начало теста создания вопроса")
    
    with allure.step("Генерация тестового вопроса"):
        question = self.question_factory.generate_question()
        self.logger.debug(f"Сгенерирован вопрос: {question[:50]}...")
    
    with allure.step("Создание вопроса через API"):
        self.logger.info("Отправка запроса на создание вопроса")
        result = self.admin_client.create_test_question(question)
        self.logger.info(f"Результат создания: {result}")
        assert result is True
    
    with allure.step("Проверка создания вопроса"):
        self.logger.info("Поиск созданного вопроса")
        questions = self.moder_client.search_questions(query=question)
        self.logger.info(f"Найдено вопросов: {len(questions)}")
        assert len(questions) > 0
```

### 2. Скриншоты и артефакты
Сохраняйте скриншоты и артефакты при ошибках.

```python
import allure

def test_with_artifacts(self, page):
    """Тест с автоматическим сохранением артефактов."""
    
    try:
        with allure.step("Навигация на страницу"):
            page.goto("https://bll.by")
            assert page.title() == "BLL - Главная страница"
        
        with allure.step("Открытие бургер-меню"):
            burger_button = page.locator("a.menu-btn.menu-btn_new")
            burger_button.click()
            
            menu = page.locator(".burger-menu-content")
            assert menu.is_visible()
            
    except AssertionError as e:
        # Автоматически сохраняем скриншот при ошибке
        allure.attach(
            page.screenshot(),
            name="Ошибка_навигации",
            attachment_type=allure.attachment_type.PNG
        )
        
        # Сохраняем HTML страницы для анализа
        allure.attach(
            page.content(),
            name="HTML_страницы",
            attachment_type=allure.attachment_type.HTML
        )
        
        raise
```

### 3. Стек вызовов и контекст
Сохраняйте контекст для лучшей диагностики.

```python
import traceback
import allure

def test_with_context(self):
    """Тест с сохранением контекста ошибок."""
    
    try:
        question = self.question_factory.generate_question()
        result = self.admin_client.create_test_question(question)
        assert result is True
        
    except Exception as e:
        # Сохраняем стек вызовов
        stack_trace = traceback.format_exc()
        allure.attach(
            stack_trace,
            name="Стек_вызовов",
            attachment_type=allure.attachment_type.TEXT
        )
        
        # Сохраняем контекст теста
        test_context = {
            "question": question,
            "timestamp": str(datetime.now()),
            "user_role": "admin",
            "test_method": "test_with_context"
        }
        
        allure.attach(
            str(test_context),
            name="Контекст_теста",
            attachment_type=allure.attachment_type.JSON
        )
        
        raise
```

## 🛡️ БЕЗОПАСНОСТЬ

### 1. Управление секретами
Никогда не храните секреты в коде.

```python
# ✅ Хорошо - использование переменных окружения
import os

class TestSecure(APITestBase):
    def test_secure_auth(self):
        """Безопасная авторизация."""
        # Куки берутся из переменных окружения
        # SESSION_COOKIE_ADMIN=...
        # SESSION_COOKIE_MODERATOR=...
        # SESSION_COOKIE_USER=...
        
        admin_cookie = os.getenv("SESSION_COOKIE_ADMIN")
        assert admin_cookie is not None, "Кука администратора не найдена"
        
        # Используем встроенный клиент с автоматической авторизацией
        result = self.admin_client.create_test_question("Тест")
        assert result is True

# ❌ Плохо - жестко заданные секреты
class TestInsecure:
    def test_hardcoded_secrets(self):
        """НЕПРАВИЛЬНО: жестко заданные секреты."""
        # ПЛОХО: секреты в коде
        ADMIN_COOKIE = "жестко_заданная_кука_в_коде"
        # Это может попасть в репозиторий!
```

### 2. Валидация входных данных
Всегда валидируйте входные данные.

```python
def test_input_validation(self):
    """Тест с валидацией входных данных."""
    
    # Тестируем различные граничные случаи
    invalid_inputs = [
        "",                    # Пустая строка
        " ",                   # Только пробелы
        "a" * 1000,           # Слишком длинная строка
        "<script>alert(1)</script>",  # XSS попытка
        "тест\0null",         # Null байты
    ]
    
    for invalid_input in invalid_inputs:
        with allure.step(f"Проверка недопустимого ввода: {invalid_input[:20]}..."):
            result = self.admin_client.create_test_question(invalid_input)
            # Система должна отклонить недопустимый ввод
            assert result is False, f"Система приняла недопустимый ввод: {invalid_input}"
```

### 3. Обработка ошибок
Правильно обрабатывайте ошибки и исключения.

```python
import pytest
import requests

def test_error_handling(self):
    """Тест с правильной обработкой ошибок."""
    
    # Тестируем различные сценарии ошибок
    
    with allure.step("Проверка обработки 404 ошибки"):
        try:
            response = self.admin_client.get_nonexistent_resource()
            # Если метод не бросает исключение, проверяем статус
            assert response.status_code == 404
        except requests.exceptions.HTTPError as e:
            # Ожидаем 404 ошибку
            assert "404" in str(e)
    
    with allure.step("Проверка обработки невалидных данных"):
        result = self.admin_client.create_test_question("")  # Пустой текст
        assert result is False, "Система должна отклонить пустой вопрос"
    
    with allure.step("Проверка обработки недостаточных прав"):
        with pytest.raises(PermissionError):
            self.user_client.access_admin_panel()
```

## 📊 ТЕСТИРОВАНИЕ РАЗНЫХ СЦЕНАРИЕВ

### 1. Позитивные сценарии
Тесты успешных сценариев.

```python
def test_positive_scenarios(self):
    """Тесты позитивных сценариев."""
    
    with allure.step("Создание валидного вопроса"):
        question = self.question_factory.generate_question()
        result = self.admin_client.create_test_question(question)
        assert result is True
    
    with allure.step("Поиск существующего вопроса"):
        questions = self.moder_client.search_questions(query=question)
        assert questions is not None
        assert len(questions) > 0
    
    with allure.step("Ответ на вопрос"):
        question_id = questions[0]["id"]
        answer_result = self.moder_client.answer_question(question_id, "Ответ")
        assert answer_result is True
```

### 2. Негативные сценарии
Тесты обработки ошибок.

```python
def test_negative_scenarios(self):
    """Тесты негативных сценариев."""
    
    with allure.step("Создание вопроса с пустым текстом"):
        result = self.admin_client.create_test_question("")
        assert result is False, "Система должна отклонить пустой вопрос"
    
    with allure.step("Поиск несуществующего вопроса"):
        questions = self.moder_client.search_questions(query="несуществующий вопрос")
        assert questions is not None
        assert len(questions) == 0
    
    with allure.step("Ответ на несуществующий вопрос"):
        result = self.moder_client.answer_question("999999", "Ответ")
        assert result is False, "Система должна отклонить ответ на несуществующий вопрос"
```

### 3. Граничные условия
Тесты граничных значений.

```python
def test_boundary_conditions(self):
    """Тесты граничных условий."""
    
    # Минимальная длина вопроса
    min_length_question = "a" * 8  # Минимальная допустимая длина
    result = self.admin_client.create_test_question(min_length_question)
    assert result is True
    
    # Максимальная длина вопроса
    max_length_question = "a" * 1000  # Максимальная длина
    result = self.admin_client.create_test_question(max_length_question)
    assert result is True  # Или False если система отклоняет
    
    # Вопрос ровно на границе
    boundary_question = "a" * 500
    result = self.admin_client.create_test_question(boundary_question)
    assert result is True
```

## 🎯 СПЕЦИФИЧЕСКИЕ РЕКОМЕНДАЦИИ

### 1. Для API тестов
```python
class APITestBestPractices(APITestBase):
    """Лучшие практики для API тестов."""
    
    def test_api_response_structure(self):
        """Проверка структуры ответа API."""
        
        with allure.step("Получение данных модерации"):
            response = self.admin_client.get_moderation_panel()
            
            # Проверяем структуру ответа
            assert "data" in response.json()
            assert "pagination" in response.json()
            assert "meta" in response.json()
            
            # Проверяем типы данных
            data = response.json()["data"]
            assert isinstance(data, list)
            
            if data:
                first_item = data[0]
                assert "id" in first_item
                assert "text" in first_item
                assert "created_at" in first_item
    
    def test_api_error_responses(self):
        """Проверка обработки ошибок API."""
        
        with allure.step("Проверка 404 ошибки"):
            response = self.admin_client.get_nonexistent_resource()
            assert response.status_code == 404
            
            # Проверяем структуру ошибки
            error_data = response.json()
            assert "error" in error_data
            assert "message" in error_data
            assert "code" in error_data
    
    def test_api_rate_limiting(self):
        """Проверка лимитов API."""
        
        with allure.step("Проверка обработки большого количества запросов"):
            # Выполняем серию запросов
            results = []
            for i in range(10):
                try:
                    result = self.admin_client.create_test_question(f"Вопрос {i}")
                    results.append(result)
                except Exception as e:
                    # Ловим ошибки rate limiting
                    assert "rate limit" in str(e).lower() or "429" in str(e)
                    break
            
            # Проверяем, что система обрабатывает нагрузку
            assert len(results) > 0
```

### 2. Для UI тестов
```python
class UITestBestPractices(UITestBase):
    """Лучшие практики для UI тестов."""
    
    def test_ui_element_interactions(self, page):
        """Тест взаимодействия с UI элементами."""
        
        with allure.step("Переход на страницу"):
            page.goto("https://bll.by")
            
            # Явные ожидания вместо time.sleep()
            page.wait_for_load_state("networkidle")
            
            # Проверка видимости элементов
            burger_button = page.locator("a.menu-btn.menu-btn_new")
            expect(burger_button).to_be_visible()
            expect(burger_button).to_be_enabled()
    
    def test_ui_responsive_design(self, page):
        """Тест адаптивного дизайна."""
        
        with allure.step("Проверка разных размеров экрана"):
            # Десктоп
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto("https://bll.by")
            desktop_menu = page.locator(".desktop-menu")
            expect(desktop_menu).to_be_visible()
            
            # Мобильный
            page.set_viewport_size({"width": 375, "height": 667})
            page.goto("https://bll.by")
            mobile_menu = page.locator(".mobile-menu")
            expect(mobile_menu).to_be_visible()
    
    def test_ui_accessibility(self, page):
        """Тест доступности."""
        
        with allure.step("Проверка доступности элементов"):
            page.goto("https://bll.by")
            
            # Проверка наличия alt текстов
            images = page.locator("img").all()
            for img in images:
                alt_text = img.get_attribute("alt")
                assert alt_text is not None, "Изображение без alt текста"
            
            # Проверка заголовков
            headings = page.locator("h1, h2, h3, h4, h5, h6").all()
            assert len(headings) > 0, "Нет заголовков на странице"
```

## 📈 МЕТРИКИ И МОНИТОРИНГ

### 1. Покрытие тестами
Отслеживайте покрытие кода тестами.

```python
# Запуск с покрытием кода
# pytest --cov=framework --cov-report=html --cov-report=term

def test_coverage_tracking(self):
    """Тест для отслеживания покрытия."""
    
    # Убедитесь что тестируете все основные пути
    with allure.step("Проверка основного пути"):
        question = self.question_factory.generate_question()
        result = self.admin_client.create_test_question(question)
        assert result is True
    
    with allure.step("Проверка альтернативного пути"):
        # Тестируем альтернативные сценарии
        result = self.admin_client.create_test_question("")  # Пустой текст
        assert result is False
```

### 2. Производительность тестов
Мониторьте время выполнения тестов.

```python
import time
import pytest

class TestPerformance(APITestBase):
    """Тесты производительности."""
    
    @pytest.mark.performance
    def test_api_response_time(self):
        """Проверка времени ответа API."""
        
        with allure.step("Измерение времени ответа"):
            start_time = time.time()
            response = self.admin_client.get_moderation_panel()
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # в миллисекундах
            allure.attach(
                str(response_time),
                name="Время_ответа_мс",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # API должен отвечать быстро
            assert response_time < 2000, f"API отвечает слишком медленно: {response_time}мс"
```

## 🤝 ПОДДЕРЖКА И СОПРОВОЖДЕНИЕ

### 1. Документирование тестов
Добавляйте понятные описания.

```python
@allure.title("Создание вопроса администратором")
@allure.description("""
    Проверяет возможность администратора создавать вопросы через API.
    Тест включает:
    1. Генерацию уникального вопроса
    2. Отправку запроса на создание
    3. Проверку успешного результата
""")
@pytest.mark.api
@pytest.mark.question
@pytest.mark.regression
def test_admin_can_create_question(self):
    """Администратор может создать вопрос."""
    # Реализация теста
    pass
```

### 2. Обратная связь и улучшения
Регулярно пересматривайте и улучшайте тесты.

```python
# Периодически анализируйте:
# - Время выполнения тестов
# - Частоту падений (flaky тесты)
# - Покрытие кода
# - Дублирование функциональности

def test_review_metrics(self):
    """Тест для анализа метрик."""
    
    # Этот тест может быть запущен отдельно для анализа
    # pytest tests/performance/test_metrics_analysis.py
    
    pass
```

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

### Связанные документы
- [Написание тестов](WRITING_TESTS.md) - основы написания тестов
- [Архитектура фреймворка](../ARCHITECTURE.md) - понимание структуры
- [Система авторизации](../COMPONENTS/AUTH_SYSTEM.md) - работа с авторизацией
- [Примеры тестов](../REFERENCES/EXAMPLES.md) - практические примеры

### Полезные ссылки
- [Pytest документация](https://docs.pytest.org/)
- [Allure документация](https://docs.qameta.io/allure/)
- [Playwright документация](https://playwright.dev/python/docs/intro)

При возникновении вопросов по лучшим практикам:
1. Изучите [примеры](../REFERENCES/EXAMPLES.md)
2. Создайте issue в репозитории
3. Обратитесь к Lead SDET Architect
