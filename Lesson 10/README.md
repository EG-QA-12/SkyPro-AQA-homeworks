# SkyPro QA Homework - Lesson 10

## Обзор проекта

Этот проект представляет собой объединенную и доработанную версию домашних заданий по автоматизации тестирования с полной документацией, type hints и интеграцией Allure для красивых отчетов.

**Типы тестов:**
- **UI тесты** (Selenium WebDriver) — калькулятор, формы, интернет-магазин
- **API тесты** (requests) — CRUD операции с учителями
- **Database тесты** (SQLAlchemy/PostgreSQL) — работа с таблицей учителей

## Структура проекта

```
Lesson 10/
├── README.md                    # Документация проекта
├── requirements.txt             # Зависимости Python
├── pytest.ini                 # Конфигурация pytest и Allure
├── .gitignore                 # Исключения для Git
├── pages/                     # Page Object классы (UI)
│   ├── __init__.py
│   ├── base_page.py           # Базовый класс страницы
│   ├── calculator_page.py      # Калькулятор
│   ├── form_page.py           # Форма ввода данных
│   ├── home_page.py           # Домашняя страница
│   └── shopping_page.py         # Интернет-магазин
├── database/                  # Классы для работы с БД
│   ├── __init__.py
│   ├── teacher_table.py        # TeacherTable с полной документацией
│   └── db_connection.py       # Модуль подключения к БД
├── api/                      # API клиенты
│   ├── __init__.py
│   ├── base_client.py         # Базовый API клиент
│   └── teacher_api.py          # API для работы с учителями
├── tests/                     # Все тесты с Allure разметкой
│   ├── __init__.py
│   ├── conftest.py           # Общие фикстуры
│   ├── ui/                   # UI тесты
│   │   ├── __init__.py
│   │   ├── test_calculator.py
│   │   ├── test_form.py
│   │   └── test_shopping.py
│   └── database/             # БД тесты
│       ├── __init__.py
│       └── test_teacher_table.py
├── data/                      # Тестовые данные
│   ├── __init__.py
│   ├── test_data.py          # Статичные тестовые данные
│   └── faker_data.py         # Генерация данных через Faker
└── config/                    # Конфигурация
    ├── __init__.py
    └── db_config.py          # Конфигурация БД
```

## Установка и настройка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка базы данных

Убедитесь, что PostgreSQL установлен и запущен. Создайте базу данных `postgres`:

```sql
CREATE DATABASE postgres;
CREATE TABLE teacher (
    teacher_id INTEGER PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    group_id INTEGER NOT NULL
);
```

### 3. Переменные окружения (опционально)

```bash
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="postgres"
export DB_USER="postgres"
export DB_PASSWORD="1844"
```

## Запуск тестов

### Запуск всех тестов

```bash
# Запуск всех тестов с генерацией Allure отчетов
pytest tests/ --alluredir=allure-results

# Запуск только UI тестов
pytest tests/ui/ --alluredir=allure-results

# Запуск только тестов БД
pytest tests/database/ --alluredir=allure-results

# Запуск с параллельным выполнением
pytest -n auto tests/ --alluredir=allure-results

# Запуск с фильтрацией по маркерам
pytest tests/ -m "smoke" --alluredir=allure-results
pytest tests/ -m "database" --alluredir=allure-results
pytest tests/ -m "critical" --alluredir=allure-results
```

### Просмотр Allure отчетов

```bash
# Генерация и открытие отчета
allure generate allure-results --clean

# Открытие отчета в браузере
allure open allure-report
```

## Архитектура и стандарты

### Page Object Model

- **BasePage**: Базовый класс с общими методами
- **CalculatorPage**: Работа с калькулятором
- **FormPage**: Работа с формами ввода данных
- **ShoppingPage**: Набор классов для интернет-магазина
- Все методы имеют `@allure.step` декораторы для трассировки
- Используются семантические локаторы и явные ожидания

### Работа с базой данных

- **TeacherTable**: CRUD операции с валидацией данных
- **DbConnection**: Унифицированное подключение к БД
- Все методы имеют `@allure.step` декораторы
- Полная обработка ошибок с rollback транзакций

### API тестирование

- **BaseAPIClient**: Базовый HTTP клиент
- **TeacherAPI**: Специализированный клиент для учителей
- Поддержка всех HTTP методов (GET, POST, PUT, DELETE)
- Управление заголовками и авторизацией

### Тестирование

- Все тесты размечены декораторами Allure:
  - `@allure.epic` - верхний уровень
  - `@allure.feature` - функциональная область
  - `@allure.story` - пользовательская история
  - `@allure.title` - название теста
  - `@allure.description` - описание теста
  - `@allure.severity` - уровень важности
  - `@allure.tag` - теги для фильтрации

- Шаги тестов размечены через `with allure.step()` или `@allure.step`
- Проверки также размечены для детализации в отчетах

## Документация кода

### Type Hints

Все методы классов содержат полную типизацию:
- Параметры методов с указанием типов (кроме `self`)
- Возвращаемые значения с указанием типов
- Использование `Optional` для необязательных параметров

### Docstrings

Каждый метод содержит подробную документацию:
- Назначение метода
- Описание всех параметров с типами
- Описание возвращаемого значения
- Информация об исключениях (если есть)

## Примеры использования

### UI тесты

```python
# Пример теста калькулятора
def test_calculator_example(driver):
    calculator = CalculatorPage(driver)
    
    with allure.step("Открыть страницу калькулятора"):
        calculator.open_page("https://example.com/calculator")
    
    with allure.step("Выполнить вычисление"):
        calculator.enter_delay_value("5")
        calculator.click_button("7")
        calculator.click_operator_button("+")
        calculator.click_button("3")
        calculator.click_equals_button()
    
    with allure.step("Проверить результат"):
        result = calculator.get_result_text()
        assert result == "10"
```

### БД тесты

```python
# Пример теста TeacherTable
def test_teacher_example(db):
    teacher_data = {
        'teacher_id': 12345,
        'email': 'test@example.com',
        'group_id': 100
    }
    
    with allure.step("Добавить учителя"):
        db.add_teacher(**teacher_data)
    
    with allure.step("Проверить добавление"):
        teachers = db.get_teacher()
        assert (12345, 'test@example.com', 100) in teachers
```

### API тесты

```python
# Пример теста API
def test_api_example():
    api = TeacherAPI()
    
    with allure.step("Создать учителя через API"):
        teacher_data = {'email': 'test@example.com', 'group_id': 100}
        result = api.create_teacher(teacher_data)
        assert result['email'] == teacher_data['email']
```

## Маркеры тестов

- `@pytest.mark.ui` - UI тесты
- `@pytest.mark.database` - Тесты базы данных
- `@pytest.mark.api` - API тесты
- `@pytest.mark.smoke` - Смоук тесты
- `@pytest.mark.regression` - Регрессионные тесты
- `@pytest.mark.critical` - Критические тесты
- `@pytest.mark.normal` - Обычные тесты
- `@pytest.mark.minor` - Маловажные тесты

## Уровни критичности (Severity)

- **BLOCKER** - Блокирующий функционал
- **CRITICAL** - Критические ошибки
- **HIGH** - Важные ошибки
- **NORMAL** - Обычный уровень
- **MINOR** - Маловажные проблемы

## Лучшие практики

1. **Изоляция тестов**: Каждый тест независим, использует собственные фикстуры
2. **Читаемые имена**: `test_<feature>_<scenario>_<expected>`
3. **AAA паттерн**: Arrange, Act, Assert структура тестов
4. **Явные ожидания**: Использование WebDriverWait вместо time.sleep
5. **Обработка ошибок**: Корректная обработка исключений и очистка ресурсов
6. **Документация**: Все методы и классы имеют полную документацию

## Требования

- Python 3.9+
- PostgreSQL 12+
- Selenium WebDriver (Chrome/Firefox)
- Доступ к интернету (для UI тестов)

## Troubleshooting

### Проблемы с запуском тестов

1. **Проблема**: WebDriver не найден
   **Решение**: Установить webdriver-manager или указать путь к драйверу

2. **Проблема**: Нет подключения к БД
   **Решение**: Проверить конфигурацию БД и статус PostgreSQL

3. **Проблема**: Тесты падают с timeout
   **Решение**: Увеличить таймауты в фикстурах

### Полезные команды

```bash
# Проверить установленные пакеты
pip list

# Обновить зависимости
pip install -r requirements.txt --upgrade

# Запуск с детальным выводом
pytest -v -s tests/

# Запуск только упавших тестов
pytest --lf --alluredir=allure-results
```

