# Подробный план создания E2E тестов для бургер-меню

## 1. Архитектура проекта (обновленная с учетом существующих компонентов)

### 1.1. Структура Page Objects

#### 1.1.1. Базовые классы
- Используем существующий `framework/app/pages/base_page.py` как основу
  - Методы: `save_cookies()`
  - Расширяем функциональность для E2E тестов

- `tests/e2e/pages/authenticated_base_page.py` - базовый класс для авторизованных страниц
  - Наследует от базового Page Object
  - Добавляет методы работы с авторизацией используя существующие утилиты

#### 1.1.2. Специфические Page Objects
- `tests/e2e/pages/burger_menu_page.py` - основной Page Object для бургер-меню
  - Использует локаторы из `authenticated_ui_locators_bll_by.json`
  - Методы:
    - `open_menu()` - открытие бургер-меню
    - `close_menu()` - закрытие бургер-меню
    - `click_link_by_text(text: str)` - клик по ссылке по тексту
    - `click_link_by_href(href: str)` - клик по ссылке по href
    - `get_all_menu_items()` - получение всех элементов меню
    - `is_menu_open()` - проверка открытия меню
    - `wait_for_menu_loaded()` - ожидание загрузки меню
    - `get_menu_item_by_text(text: str)` - получение элемента меню по тексту
    - `get_menu_item_by_href(href: str)` - получение элемента меню по href

- `tests/e2e/pages/main_page.py` - Page Object для главной страницы
  - Использует существующую структуру из framework
  - Методы: `click_burger_menu_button()`, `is_burger_menu_visible()`

#### 1.1.3. Вспомогательные классы
- Используем существующие утилиты из `framework/utils/`:
 - `smart_auth_manager.py` для управления сессией
  - `auth_cookie_provider.py` для получения куки
  - `url_utils.py` для работы с URL и параметрами
  - `cookie_constants.py` для работы с куки

- `tests/e2e/utils/burger_menu_validator.py` - валидатор структуры меню
  - Методы: `validate_menu_structure()`, `validate_menu_links()`, `compare_with_csv_data()`

- `tests/e2e/utils/link_checker.py` - проверка доступности ссылок
  - Методы: `check_link_accessibility()`, `check_external_link()`, `check_telephone_link()`

### 1.2. Управление авторизацией

- Используем существующие компоненты:
  - `framework/utils/smart_auth_manager.py` для управления сессией
  - `framework/utils/auth_cookie_provider.py` для получения куки
  - `framework/fixtures/auth_fixtures.py` для фикстур авторизации
  - Фикстуры: `authenticated_admin`, `authenticated_user`, `clean_context`

### 1.3. Data Providers

- Используем существующие данные:
  - `burger_menu_elements.csv` для списка ссылок
 - `authenticated_ui_locators_bll_by.json` для локаторов
  - `tests/data/burger_menu_links.csv` для тестовых данных
  - `framework/utils/auth_cookie_provider.py` для получения куки

## 2. Структура тестов

### 2.1. Тесты навигации
- `tests/e2e/test_burger_menu_navigation.py`
  - `test_burger_menu_opens()` - проверка открытия меню
  - `test_burger_menu_closes()` - проверка закрытия меню
  - `test_burger_menu_structure()` - проверка структуры меню
  - `test_all_burger_menu_links_navigation()` - параметризованный тест для всех 83 ссылок
 - `test_burger_menu_links_by_category()` - тестирование ссылок по категориям

### 2.2. Функциональные тесты
- `tests/e2e/test_burger_menu_functionality.py`
  - `test_burger_menu_links_accessibility()` - доступность ссылок
 - `test_burger_menu_external_links()` - проверка внешних ссылок
 - `test_burger_menu_telephone_links()` - проверка телефонных ссылок
 - `test_burger_menu_search_functionality()` - функциональность поиска в меню
  - `test_burger_menu_responsive_behavior()` - адаптивное поведение меню

### 2.3. Тесты производительности
- `tests/e2e/test_burger_menu_performance.py`
  - `test_burger_menu_load_time()` - время загрузки меню
  - `test_burger_menu_response_time()` - время отклика на клики
  - `test_burger_menu_memory_usage()` - использование памяти при открытии меню

### 2.4. Тесты безопасности
- `tests/e2e/test_burger_menu_security.py`
  - `test_burger_menu_xss_protection()` - защита от XSS
 - `test_burger_menu_url_validation()` - валидация URL ссылок
  - `test_burger_menu_auth_protection()` - проверка авторизации для защищенных ссылок

## 3. Проверки и сценарии

### 3.1. Основные проверки
- Открытие/закрытие бургер-меню
- Доступность всех 83 ссылок
- Переход по внутренним ссылкам
- Проверка заголовков на целевых страницах
- Доступность внешних ссылок
- Работа телефонных ссылок
- Сохранение сессии при навигации
- Корректная работа с allow-session параметром

### 3.2. Сценарии тестирования
- **Сценарий 1: Полная навигация**
  - Открытие главной страницы
  - Открытие бургер-меню
  - Последовательный переход по всем категориям
  - Проверка заголовков на каждой странице
  - Возврат на главную страницу

- **Сценарий 2: Быстрая проверка**
  - Открытие меню
  - Проверка видимости ключевых ссылок
  - Клик по случайным ссылкам
  - Проверка корректности переходов

- **Сценарий 3: Адаптивное поведение**
  - Открытие меню на разных разрешениях
  - Проверка корректного отображения
  - Тестирование touch событий

### 3.3. Параметризованные тесты
- `test_burger_menu_link_navigation(link_text, href)` - для каждой из 83 ссылок
- Параметры: текст ссылки, URL, тип ссылки (внутренняя/внешняя/телефонная)

## 4. Вспомогательные файлы

### 4.1. Конфигурация тестов
- Используем существующую конфигурацию:
  - `tests/e2e/conftest.py` - общие фикстуры
  - `framework/fixtures/auth_fixtures.py` - фикстуры авторизации
  - `framework/utils/reporting/allure_utils.py` - интеграция с Allure

### 4.2. Утилиты
- Используем существующие утилиты из framework:
 - `framework/utils/auth_utils.py` - утилиты авторизации
 - `framework/utils/url_utils.py` - утилиты для работы с URL
  - `framework/utils/cookie_constants.py` - константы для куки

## 5. План реализации

### Этап 1: Подготовка инфраструктуры (День 1)
1. Создание Page Objects с использованием существующих компонентов
2. Настройка авторизации через существующие фикстуры
3. Создание data providers на основе существующих данных

### Этап 2: Основные тесты (День 2-3)
1. Реализация тестов навигации
2. Реализация функциональных тестов
3. Параметризованные тесты для всех ссылок

### Этап 3: Дополнительные тесты (День 4)
1. Тесты производительности
2. Тесты безопасности
3. Тесты адаптивности

### Этап 4: Тестирование и отладка (День 5)
1. Запуск всех тестов
2. Исправление багов
3. Оптимизация производительности

## 6. Критерии качества

- Каждый тест должен быть изолированным
- Использование явных ожиданий вместо sleep
- Понятные сообщения об ошибках
- Логирование действий
- Интеграция с Allure для отчетности
- Соответствие принципам Page Object Model
- Повторное использование существующих компонентов
- Минимизация дублирования кода