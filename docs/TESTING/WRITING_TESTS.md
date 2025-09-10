# 🧪 НАПИСАНИЕ ТЕСТОВ

## 📋 ОБЗОР

Руководство по написанию эффективных и поддерживаемых тестов с использованием фреймворка автотестов.

## 🎯 ТИПЫ ТЕСТОВ

### 1. API Тесты
Тесты для проверки REST API эндпоинтов.

```python
import pytest
from framework.test_bases.api_test_base import APITestBase

class TestQuestionsAPI(APITestBase):
    """Тесты для API вопросов."""
    
    @pytest.mark.api
    @pytest.mark.question
    def test_create_question(self):
        """Создание вопроса через API."""
        # Используем встроенный клиент с автоматической авторизацией
        result = self.admin_client.create_test_question("Тестовый вопрос")
        assert result is True
    
    @pytest.mark.api
    @pytest.mark.question
    def test_search_questions(self):
        """Поиск вопросов через API."""
        questions = self.moder_client.search_questions(query="тестовый")
        assert questions is not None
        assert len(questions) > 0
```

### 2. UI Тесты
Тесты для проверки пользовательского интерфейса.

```python
import pytest
from framework.test_bases.ui_test_base import UITestBase

class TestBurgerMenu(UITestBase):
    """Тесты для бургер-меню."""
    
    @pytest.mark.ui
    @pytest.mark.burger_menu
    def test_navigation_links(self, page):
        """Проверка ссылок в бургер-меню."""
        page.goto("https://bll.by")
        
        # Используем встроенные методы для работы с бургер-меню
        self.open_burger_menu(page)
        
        # Проверяем видимость ссылок
        links = self.get_burger_menu_links(page)
        assert len(links) > 0
        
        # Проверяем переход по ссылкам
        for link in links[:3]:  # Проверяем первые 3 ссылки
            self.click_burger_menu_link(page, link)
            assert self.verify_page_loaded(page)
```

### 3. Интеграционные тесты
Комплексные тесты, проверяющие взаимодействие компонентов.

```python
import pytest
from framework.test_bases.api_test_base import APITestBase

class TestQuestionWorkflow(APITestBase):
    """Интеграционный тест workflow вопроса."""
    
    @pytest.mark.integration
    @pytest.mark.question
    @pytest.mark.regression
    def test_full_question_workflow(self):
        """Полный workflow: создание → поиск → ответ."""
        
        # 1. Создание вопроса
        with allure.step("Создание вопроса"):
            test_question = self.question_factory.generate_question()
            result = self.admin_client.create_test_question(test_question)
            assert result is True
        
        # 2. Поиск вопроса
        with allure.step("Поиск вопроса"):
            questions = self.moder_client.search_questions(query=test_question)
            assert questions is not None
            assert len(questions) > 0
        
        # 3. Ответ на вопрос
        with allure.step("Ответ на вопрос"):
            question_id = questions[0]["id"]
            success = self.moder_client.answer_question(
                question_id=question_id,
                answer_text="Тестовый ответ"
            )
            assert success is True
```

### 4. E2E Тесты
Сквозные тесты, имитирующие пользовательские сценарии.

```python
import pytest
from framework.test_bases.ui_test_base import UITestBase

class TestUserJourney(UITestBase):
    """E2E тест пользовательского сценария."""
    
    @pytest.mark.e2e
    @pytest.mark.user_journey
    @pytest.mark.smoke
    def test_complete_user_flow(self, page):
        """Полный пользовательский сценарий."""
        
        # 1. Переход на главную страницу
        with allure.step("Переход на главную страницу"):
            page.goto("https://bll.by")
            assert page.title() == "BLL - Главная страница"
        
        # 2. Открытие бургер-меню и навигация
        with allure.step("Навигация через бургер-меню"):
            self.open_burger_menu(page)
            self.click_burger_menu_link(page, "Вопросы")
            
        # 3. Проверка загрузки страницы вопросов
        with allure.step("Проверка страницы вопросов"):
            assert self.verify_page_loaded(page)
            assert "вопросы" in page.url.lower()
```

## 🏗️ СТРУКТУРА ТЕСТОВ

### Базовые классы

#### APITestBase
Базовый класс для API тестов с автоматической авторизацией.

```python
from framework.test_bases.api_test_base import APITestBase

class TestExample(APITestBase):
    def test_something(self):
        # Доступные автоматические клиенты:
        # self.admin_client - клиент администратора
        # self.moder_client - клиент модератора  
        # self.user_client - клиент пользователя
        # self.question_factory - фабрика вопросов
        # self.logger - логгер
        pass
```

#### UITestBase
Базовый класс для UI тестов с авторизованным контекстом.

```python
from framework.test_bases.ui_test_base import UITestBase

class TestExample(UITestBase):
    def test_something(self, page):
        # page - уже авторизованная страница Playwright
        # self.context - авторизованный контекст
        # self.logger - логгер
        pass
```

### Маркеры pytest

#### Системные маркеры
```python
@pytest.mark.api          # API тесты
@pytest.mark.ui           # UI тесты
@pytest.mark.integration  # Интеграционные тесты
@pytest.mark.e2e          # E2E тесты
@pytest.mark.smoke        # Smoke тесты
@pytest.mark.regression   # Регрессионные тесты
@pytest.mark.slow         # Медленные тесты
```

#### Функциональные маркеры
```python
@pytest.mark.question     # Тесты вопросов
@pytest.mark.answer       # Тесты ответов
@pytest.mark.moderation  # Тесты модерации
@pytest.mark.auth        # Тесты авторизации
@pytest.mark.search      # Тесты поиска
@pytest.mark.burger_menu # Тесты бургер-меню
```

## 📝 ЛУЧШИЕ ПРАКТИКИ

### 1. Именование тестов
```python
# ✅ Хорошо - понятное именование
def test_admin_can_create_question(self):
    pass

def test_user_cannot_access_admin_panel(self, page):
    pass

def test_question_creation_fails_with_empty_text(self):
    pass

# ❌ Плохо - неинформативные имена
def test_1(self):
    pass

def test_question(self):
    pass
```

### 2. Структура теста (AAA)
```python
def test_question_workflow(self):
    """Полный workflow вопроса."""
    
    # Arrange - Подготовка
    test_question = self.question_factory.generate_question()
    
    # Act - Действие
    result = self.admin_client.create_test_question(test_question)
    
    # Assert - Проверка
    assert result is True
```

### 3. Использование шагов Allure
```python
import allure

def test_complex_workflow(self):
    with allure.step("1. Создание тестового вопроса"):
        question = self.question_factory.generate_question()
        result = self.admin_client.create_test_question(question)
        assert result is True
    
    with allure.step("2. Поиск созданного вопроса"):
        questions = self.moder_client.search_questions(query=question)
        assert len(questions) > 0
```

### 4. Обработка ошибок
```python
import pytest

def test_api_error_handling(self):
    """Проверка обработки ошибок API."""
    
    # Проверяем, что система корректно обрабатывает ошибки
    result = self.admin_client.create_test_question("")  # Пустой текст
    
    # Ожидаем, что система отклонит пустой вопрос
    assert result is False, "Система должна отклонить пустой вопрос"
```

## 🔧 ВСПОМОГАТЕЛЬНЫЕ ИНСТРУМЕНТЫ

### Фабрики данных
```python
def test_with_generated_data(self):
    """Тест с использованием фабрики данных."""
    
    # Генерация уникальных тестовых данных
    question1 = self.question_factory.generate_question()
    question2 = self.question_factory.generate_question(category="техника")
    
    # Использование сгенерированных данных
    result1 = self.admin_client.create_test_question(question1)
    result2 = self.admin_client.create_test_question(question2)
    
    assert result1 is True
    assert result2 is True
```

### Логирование
```python
import logging

def test_with_logging(self):
    """Тест с логированием."""
    
    # Используем встроенный логгер
    self.logger.info("Начало теста создания вопроса")
    
    question = self.question_factory.generate_question()
    self.logger.debug(f"Сгенерирован вопрос: {question}")
    
    result = self.admin_client.create_test_question(question)
    self.logger.info(f"Результат создания: {result}")
    
    assert result is True
```

### Работа с файлами
```python
def test_with_file_attachments(self):
    """Тест с прикреплением файлов."""
    
    # Сохранение артефактов для отладки
    with allure.step("Сохранение тестовых данных"):
        test_data = {"question": "Тестовый вопрос", "timestamp": "2025-09-10"}
        allure.attach(
            str(test_data),
            name="Тестовые данные",
            attachment_type=allure.attachment_type.JSON
        )
```

## 🎯 СПЕЦИФИЧЕСКИЕ ТЕСТЫ

### 1. Тесты авторизации
```python
import pytest
from framework.test_bases.api_test_base import APITestBase

class TestAuthorization(APITestBase):
    """Тесты авторизации."""
    
    @pytest.mark.auth
    @pytest.mark.security
    def test_admin_access_rights(self):
        """Проверка прав доступа администратора."""
        # self.admin_client уже авторизован
        response = self.admin_client.get_moderation_panel()
        assert response.status_code == 200
    
    @pytest.mark.auth
    @pytest.mark.security
    def test_user_access_restrictions(self):
        """Проверка ограничений доступа пользователя."""
        # self.user_client уже авторизован
        with pytest.raises(PermissionError):
            self.user_client.access_admin_panel()
```

### 2. Тесты модерации
```python
class TestModeration(APITestBase):
    """Тесты модерации."""
    
    @pytest.mark.moderation
    @pytest.mark.question
    def test_take_question_for_moderation(self):
        """Взятие вопроса в работу."""
        
        # Получаем список вопросов для модерации
        questions = self.moder_client.get_moderation_questions()
        
        if questions:
            question_id = questions[0]["id"]
            
            # Берем вопрос в работу
            result = self.moder_client.take_question_for_work(question_id)
            assert result is True
```

### 3. Тесты публикации
```python
class TestPublishing(APITestBase):
    """Тесты публикации."""
    
    @pytest.mark.publish
    @pytest.mark.question
    def test_publish_question(self):
        """Публикация вопроса."""
        
        # Создаем вопрос
        question = self.question_factory.generate_question()
        create_result = self.admin_client.create_test_question(question)
        assert create_result is True
        
        # Публикуем вопрос
        publish_result = self.admin_client.publish_question(question)
        assert publish_result is True
```

## 📊 ПАРАМЕТРИЗОВАННЫЕ ТЕСТЫ

### Параметризация данных
```python
import pytest

class TestQuestionValidation(APITestBase):
    """Тесты валидации вопросов."""
    
    @pytest.mark.parametrize("question_text,expected_result", [
        ("Короткий", False),           # Слишком короткий
        ("Нормальный вопрос", True),    # Нормальный
        ("", False),                   # Пустой
        ("Очень длинный вопрос " * 10, False),  # Слишком длинный
    ])
    def test_question_length_validation(self, question_text, expected_result):
        """Проверка валидации длины вопроса."""
        result = self.admin_client.create_test_question(question_text)
        assert result == expected_result
```

### Параметризация ролей
```python
import pytest

class TestRoleAccess(APITestBase):
    """Тесты доступа по ролям."""
    
    @pytest.mark.auth
    @pytest.mark.parametrize("role,can_access_admin_panel", [
        ("admin", True),
        ("moderator", False),
        ("user", False),
    ])
    def test_role_based_access(self, role, can_access_admin_panel):
        """Проверка доступа по ролям."""
        if role == "admin":
            client = self.admin_client
        elif role == "moderator":
            client = self.moder_client
        else:
            client = self.user_client
        
        # Проверяем доступ к админке
        if can_access_admin_panel:
            response = client.get_admin_panel()
            assert response.status_code == 200
        else:
            with pytest.raises(PermissionError):
                client.get_admin_panel()
```

## 🔍 ДИАГНОСТИКА И ОТЛАДКА

### Скриншоты при ошибках
```python
import pytest

class TestWithScreenshots(UITestBase):
    """Тесты с автоматическими скриншотами."""
    
    def test_ui_element_visibility(self, page):
        """Проверка видимости элемента."""
        
        page.goto("https://bll.by")
        
        # Проверяем видимость элемента
        element = page.locator(".burger-menu")
        assert element.is_visible()
        
        # Скриншот сохраняется автоматически при ошибке
```

### Логирование ошибок
```python
import logging

class TestWithErrorLogging(APITestBase):
    """Тесты с логированием ошибок."""
    
    def test_api_error_logging(self):
        """Тест с логированием ошибок API."""
        
        try:
            result = self.admin_client.create_test_question("")
            assert result is False
        except Exception as e:
            self.logger.error(f"Ошибка при создании пустого вопроса: {e}")
            raise
```

## 🚀 ПРОИЗВОДИТЕЛЬНОСТЬ

### Параллельное выполнение
```python
import pytest

class TestParallelizable(APITestBase):
    """Тесты, поддерживающие параллельное выполнение."""
    
    @pytest.mark.parallel
    def test_independent_operation_1(self):
        """Независимая операция 1."""
        result = self.admin_client.create_test_question("Вопрос 1")
        assert result is True
    
    @pytest.mark.parallel
    def test_independent_operation_2(self):
        """Независимая операция 2."""
        result = self.admin_client.create_test_question("Вопрос 2")
        assert result is True
```

### Оптимизация тестов
```python
import pytest

class TestOptimized(APITestBase):
    """Оптимизированные тесты."""
    
    @pytest.fixture(scope="class")
    def prepared_questions(self):
        """Фикстура для подготовки тестовых данных один раз."""
        questions = []
        for i in range(5):
            question = self.question_factory.generate_question()
            self.admin_client.create_test_question(question)
            questions.append(question)
        return questions
    
    def test_search_performance(self, prepared_questions):
        """Тест производительности поиска."""
        # Используем подготовленные данные
        for question in prepared_questions:
            results = self.moder_client.search_questions(query=question)
            assert len(results) > 0
```

## 📚 ПРИМЕРЫ

### Полный пример API теста
```python
import pytest
import allure
from framework.test_bases.api_test_base import APITestBase

class TestQuestionManagement(APITestBase):
    """Комплексный тест управления вопросами."""
    
    @allure.title("Полный цикл управления вопросами")
    @allure.description("Создание → Поиск → Модерация → Публикация")
    @pytest.mark.api
    @pytest.mark.question
    @pytest.mark.regression
    def test_complete_question_lifecycle(self):
        """Полный цикл жизни вопроса."""
        
        with allure.step("1. Создание тестового вопроса"):
            question_text = self.question_factory.generate_question()
            create_result = self.admin_client.create_test_question(question_text)
            assert create_result is True, "Не удалось создать вопрос"
        
        with allure.step("2. Поиск созданного вопроса"):
            questions = self.moder_client.search_questions(query=question_text)
            assert questions is not None, "Поиск вернул None"
            assert len(questions) > 0, "Вопрос не найден"
            question_id = questions[0]["id"]
        
        with allure.step("3. Взятие вопроса в работу"):
            take_result = self.moder_client.take_question_for_work(question_id)
            assert take_result is True, "Не удалось взять вопрос в работу"
        
        with allure.step("4. Ответ на вопрос"):
            answer_result = self.moder_client.answer_question(
                question_id=question_id,
                answer_text="Автоматический тестовый ответ"
            )
            assert answer_result is True, "Не удалось ответить на вопрос"
        
        with allure.step("5. Публикация вопроса"):
            publish_result = self.admin_client.publish_question_by_id(question_id)
            assert publish_result is True, "Не удалось опубликовать вопрос"
```

### Полный пример UI теста
```python
import pytest
import allure
from framework.test_bases.ui_test_base import UITestBase

class TestBurgerMenuNavigation(UITestBase):
    """Комплексный UI тест навигации."""
    
    @allure.title("Комплексная навигация через бургер-меню")
    @allure.description("Открытие меню → Переход по ссылкам → Проверка заголовков")
    @pytest.mark.ui
    @pytest.mark.burger_menu
    @pytest.mark.navigation
    def test_comprehensive_burger_menu_navigation(self, page):
        """Комплексная навигация через бургер-меню."""
        
        with allure.step("1. Переход на главную страницу"):
            page.goto("https://bll.by")
            assert page.title() == "BLL - Главная страницу"
        
        with allure.step("2. Открытие бургер-меню"):
            burger_button = page.locator("a.menu-btn.menu-btn_new")
            burger_button.wait_for(state="visible", timeout=5000)
            burger_button.click()
            
            menu = page.locator(".burger-menu-content")
            assert menu.is_visible(), "Бургер-меню не открылось"
        
        with allure.step("3. Получение списка ссылок"):
            links = page.locator("a.menu_item_link").all()
            assert len(links) > 0, "Ссылки в меню не найдены"
            
            self.logger.info(f"Найдено {len(links)} ссылок в бургер-меню")
        
        with allure.step("4. Проверка переходов по основным ссылкам"):
            # Проверяем первые 3 ссылки
            for i, link in enumerate(links[:3]):
                try:
                    link_text = link.text_content().strip()
                    self.logger.info(f"Проверка ссылки: {link_text}")
                    
                    # Клик по ссылке
                    link.click()
                    
                    # Проверка загрузки страницы
                    page.wait_for_load_state("networkidle", timeout=10000)
                    
                    # Проверка наличия контента
                    body = page.locator("body")
                    assert body.is_visible(), f"Страница {link_text} не загрузилась"
                    
                    # Возвращаемся на главную для следующей итерации
                    page.goto("https://bll.by")
                    page.locator("a.menu-btn.menu-btn_new").click()
                    
                except Exception as e:
                    self.logger.error(f"Ошибка при проверке ссылки {i}: {e}")
                    allure.attach(
                        page.screenshot(),
                        name=f"Ошибка_ссылка_{i}",
                        attachment_type=allure.attachment_type.PNG
                    )
                    raise
```

## 🤝 ПОДДЕРЖКА

При возникновении вопросов по написанию тестов:
1. Изучите [примеры тестов](../REFERENCES/EXAMPLES.md)
2. Посмотрите [лучшие практики](BEST_PRACTICES.md)
3. Создайте issue в репозитории
4. Обратитесь к Lead SDET Architect
