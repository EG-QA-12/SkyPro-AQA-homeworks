# 📋 ПРИМЕРЫ ИНТЕГРАЦИИ УНИФИЦИРОВАННОГО МЕНЕДЖЕРА АВТОРИЗАЦИИ ЧЕРЕЗ conftest.py

## 🎯 ОБЩАЯ КОНЦЕПЦИЯ

Унифицированный менеджер авторизации интегрируется через `conftest.py` на разных уровнях:
- **Глобальный уровень** (`conftest.py` в корне проекта) - базовые фикстуры
- **Группы тестов** (`tests/*/conftest.py`) - специфичные фикстуры
- **Подгруппы тестов** (`tests/*/*/conftest.py`) - уточненные фикстуры

## 📁 СТРУКТУРА ИНТЕГРАЦИИ

```
project/
├── conftest.py                    # Глобальные фикстуры авторизации
├── tests/
│   ├── integration/
│   │   └── conftest.py           # Интеграционные тесты
│   ├── smoke/
│   │   ├── burger_menu/
│   │   │   └── conftest.py       # Тесты бургер-меню
│   │   └── burger_menu_params/
│   │       └── conftest.py       # Параметризованные тесты
│   └── auth/
│       └── conftest.py           # Тесты авторизации
```

## 🌐 ГЛОБАЛЬНАЯ ИНТЕГРАЦИЯ (корневой conftest.py)

### Базовая интеграция
```python
"""Корневой conftest.py - глобальные фикстуры авторизации."""

import pytest
import os
from pathlib import Path

# Импортируем унифицированный менеджер авторизации
from framework.auth.manager import auth_manager, get_session_cookie, get_auth_cookies
from framework.utils.url_utils import is_headless

# Глобальные настройки
AUTH_CACHE_TTL = int(os.getenv('AUTH_CACHE_TTL', '300'))  # 5 минут
AUTH_MODE = os.getenv('AUTH_MODE', 'auto')  # auto, api, ui, cache


@pytest.fixture(scope="session")
def unified_auth_manager():
    """Глобальный экземпляр унифицированного менеджера авторизации."""
    # Настройка TTL кэша
    auth_manager._cache_ttl = AUTH_CACHE_TTL
    return auth_manager


@pytest.fixture(scope="session")
def auth_mode():
    """Режим авторизации для текущей сессии."""
    return AUTH_MODE


@pytest.fixture(scope="session")
def admin_session_cookie(unified_auth_manager):
    """Кука администратора через унифицированный менеджер."""
    result = unified_auth_manager.get_session_cookie("admin")
    if not result.success:
        pytest.fail(f"Не удалось получить куку администратора: {result.error_message}")
    return result.cookie


@pytest.fixture(scope="session")
def user_session_cookie(unified_auth_manager):
    """Кука обычного пользователя."""
    result = unified_auth_manager.get_session_cookie("user")
    if not result.success:
        pytest.fail(f"Не удалось получить куку пользователя: {result.error_message}")
    return result.cookie


@pytest.fixture(scope="session")
def expert_session_cookie(unified_auth_manager):
    """Кука эксперта."""
    result = unified_auth_manager.get_session_cookie("expert")
    if not result.success:
        pytest.fail(f"Не удалось получить куку эксперта: {result.error_message}")
    return result.cookie


@pytest.fixture(scope="session")
def auth_cookies_factory(unified_auth_manager):
    """Фабрика для получения кук разных ролей."""
    def _get_cookies(role: str = "admin", domain: str = ".bll.by"):
        return unified_auth_manager.get_auth_cookies(role, domain)
    return _get_cookies


@pytest.fixture(scope="session")
def authenticated_context_factory(browser, auth_cookies_factory):
    """Фабрика для создания аутентифицированных браузерных контекстов."""
    def _create_context(role: str = "admin"):
        context = browser.new_context()
        cookies = auth_cookies_factory(role)
        if cookies:
            context.add_cookies(cookies)
        return context
    return _create_context
```

## 🔧 ИНТЕГРАЦИЯ ДЛЯ ИНТЕГРАЦИОННЫХ ТЕСТОВ

### `tests/integration/conftest.py`
```python
"""Конфигурация интеграционных тестов с унифицированной авторизацией."""

import pytest
from framework.auth.manager import auth_manager, get_auth_cookies
from framework.utils.smart_auth_manager import SmartAuthManager


@pytest.fixture(scope="session")
def fx_auth_manager(unified_auth_manager):
    """Менеджер авторизации для интеграционных тестов."""
    return unified_auth_manager


@pytest.fixture(scope="function")
def admin_api_session(fx_auth_manager):
    """Сессия для API тестов администратора."""
    import requests
    
    result = fx_auth_manager.get_session_cookie("admin")
    if not result.success:
        pytest.skip(f"Не удалось получить куку для API тестов: {result.error_message}")
    
    session = requests.Session()
    session.cookies.set("test_joint_session", result.cookie)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8'
    })
    
    return session


@pytest.fixture(scope="class")
def admin_context(browser, admin_session_cookie):
    """Браузерный контекст администратора для интеграционных тестов."""
    context = browser.new_context()
    # Добавляем куки администратора
    context.add_cookies([{
        "name": "test_joint_session",
        "value": admin_session_cookie,
        "domain": ".bll.by",
        "path": "/",
        "sameSite": "Lax"
    }])
    return context


@pytest.fixture(scope="function")
def expert_context(browser, expert_session_cookie):
    """Браузерный контекст эксперта для интеграционных тестов."""
    context = browser.new_context()
    context.add_cookies([{
        "name": "test_joint_session",
        "value": expert_session_cookie,
        "domain": ".bll.by", 
        "path": "/",
        "sameSite": "Lax"
    }])
    return context


@pytest.fixture(scope="function")
def moderation_panel_client(admin_api_session):
    """Клиент для работы с панелью модерации."""
    class ModerationPanelClient:
        def __init__(self, session):
            self.session = session
            self.base_url = "https://expert.bll.by"
        
        def get_questions(self, limit: int = 100):
            """Получить список вопросов."""
            response = self.session.get(f"{self.base_url}/questions", params={"limit": limit})
            return response.json() if response.status_code == 200 else None
        
        def publish_answer(self, question_id: int, answer_text: str):
            """Опубликовать ответ."""
            response = self.session.post(
                f"{self.base_url}/answers",
                json={"question_id": question_id, "text": answer_text}
            )
            return response.status_code == 200
    
    return ModerationPanelClient(admin_api_session)
```

## 🍔 ИНТЕГРАЦИЯ ДЛЯ SMOKE ТЕСТОВ БУРГЕР-МЕНЮ

### `tests/smoke/burger_menu/conftest.py`
```python
"""Конфигурация smoke тестов бургер-меню с унифицированной авторизацией."""

import pytest
from framework.auth.manager import get_auth_cookies
from framework.utils.url_utils import add_allow_session_param, is_headless


@pytest.fixture(scope="class")
def authenticated_burger_context(browser, admin_session_cookie):
    """Аутентифицированный контекст для тестов бургер-меню."""
    context = browser.new_context()
    
    # Добавляем куки администратора
    context.add_cookies([{
        "name": "test_joint_session",
        "value": admin_session_cookie,
        "domain": ".bll.by",
        "path": "/",
        "sameSite": "Lax"
    }])
    
    return context


@pytest.fixture(scope="class") 
def smart_authenticated_context(browser, unified_auth_manager):
    """Контекст с умной авторизацией для бургер-меню."""
    context = browser.new_context()
    
    # Используем умную авторизацию - проверяем валидность куки перед использованием
    session_cookie = unified_auth_manager.get_valid_session_cookie(role="admin")
    
    if session_cookie:
        # Добавляем валидную куку в контекст
        if isinstance(session_cookie, dict):
            context.add_cookies([session_cookie])
        else:
            context.add_cookies([{
                "name": "test_joint_session",
                "value": session_cookie,
                "domain": ".bll.by",
                "path": "/",
                "sameSite": "Lax"
            }])
        print(f"✅ Используется валидная кука для роли 'admin'")
    else:
        # Fallback на стандартную авторизацию
        context.add_cookies(get_auth_cookies(role="admin"))
        print(f"⚠️ Используется fallback кука для роли 'admin'")
    
    return context


@pytest.fixture(scope="function")
def burger_menu_page(authenticated_burger_context):
    """Страница бургер-меню с аутентификацией."""
    from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage
    page = authenticated_burger_context.new_page()
    return BurgerMenuPage(page)


@pytest.fixture(scope="function")
def authenticated_page(authenticated_burger_context):
    """Аутентифицированная страница для тестов."""
    page = authenticated_burger_context.new_page()
    
    # Добавляем allow-session параметр для headless режима
    if is_headless():
        page.goto(add_allow_session_param("https://bll.by/", is_headless()))
    else:
        page.goto("https://bll.by/")
    
    return page
```

## 🔄 ИНТЕГРАЦИЯ ДЛЯ ПАРАМЕТРИЗОВАННЫХ ТЕСТОВ

### `tests/smoke/burger_menu_params/conftest.py`
```python
"""Конфигурация параметризованных тестов с унифицированной авторизацией."""

import pytest
from playwright.sync_api import BrowserContext
from framework.auth.manager import auth_manager
from framework.utils.url_utils import add_allow_session_param, is_headless

# Словарь доменов для мульти-доменных тестов
DOMAINS = {
    'bll': 'https://bll.by',
    'expert': 'https://expert.bll.by', 
    'bonus': 'https://bonus.bll.by',
    'ca': 'https://ca.bll.by',
    'cp': 'https://cp.bll.by'
}

IS_HEADLESS_MODE = is_headless()


@pytest.fixture(scope="session", params=list(DOMAINS.values()), ids=list(DOMAINS.keys()))
def multi_domain_context(request):
    """
    Фикстура для мульти-доменных тестов.
    
    Возвращает кортеж (domain_name, base_url) для параметризации тестов.
    """
    base_url = request.param
    
    # Добавляем параметр allow-session для headless режима
    if IS_HEADLESS_MODE:
        base_url = add_allow_session_param(base_url, headless=True)
    
    # Определяем имя домена по URL
    domain_name = next((name for name, url in DOMAINS.items() if base_url.startswith(url)), 'unknown')
    
    return domain_name, base_url


@pytest.fixture(scope="function")
def domain_aware_authenticated_context(browser, multi_domain_context):
    """
    Контекст с авторизацией, адаптированный под конкретный домен.
    
    Использует унифицированный менеджер авторизации для получения
    валидной куки и адаптирует её под домен.
    """
    context = browser.new_context()
    domain_name, base_url = multi_domain_context
    
    print(f"🎯 Домен {domain_name}: используем унифицированную авторизацию с проверкой кук")
    
    # Используем SmartAuthManager (или унифицированный менеджер) для получения валидной куки
    auth_manager_instance = auth_manager  # Используем унифицированный менеджер
    session_cookie = auth_manager_instance.get_valid_session_cookie(role="admin")
    
    if session_cookie:
        # Адаптируем домен куки под текущий домен
        if isinstance(session_cookie, dict):
            # Обновляем домен куки под текущий домен
            session_cookie['domain'] = f".{domain_name}.bll.by" if domain_name != 'bll' else ".bll.by"
            context.add_cookies([session_cookie])
        else:
            # Если кука строка, создаем правильный формат
            cookie_dict = {
                "name": "test_joint_session",
                "value": session_cookie,
                "domain": f".{domain_name}.bll.by" if domain_name != 'bll' else ".bll.by",
                "path": "/",
                "sameSite": "Lax"
            }
            context.add_cookies([cookie_dict])
        
        print(f"✅ Авторизация для домена {domain_name} выполнена")
    else:
        # Fallback на стандартную авторизацию
        from framework.utils.auth_cookie_provider import get_auth_cookies
        context.add_cookies(get_auth_cookies(role="admin"))
        print(f"⚠️ Fallback авторизация для домена {domain_name}")
    
    return context


@pytest.fixture(scope="class")
def smart_authenticated_context_per_domain(browser):
    """
    Класс-уровневая фикстура с умной авторизацией для каждого домена.
    
    Создает аутентифицированный контекст на уровне класса для оптимизации
    производительности в параметризованных тестах.
    """
    def _create_context(domain_name: str = "bll"):
        context = browser.new_context()
        
        print(f"🎯 Домен {domain_name}: используем умную авторизацию с проверкой кук")
        auth_manager_instance = auth_manager
        session_cookie = auth_manager_instance.get_valid_session_cookie(role="admin")
        
        if session_cookie:
            if isinstance(session_cookie, dict):
                # Адаптируем домен
                session_cookie['domain'] = f".{domain_name}.bll.by" if domain_name != 'bll' else ".bll.by"
                context.add_cookies([session_cookie])
            else:
                cookie_dict = {
                    "name": "test_joint_session", 
                    "value": session_cookie,
                    "domain": f".{domain_name}.bll.by" if domain_name != 'bll' else ".bll.by",
                    "path": "/",
                    "sameSite": "Lax"
                }
                context.add_cookies([cookie_dict])
            
            print(f"✅ Класс-уровневая авторизация для домена {domain_name} выполнена")
        else:
            from framework.utils.auth_cookie_provider import get_auth_cookies
            context.add_cookies(get_auth_cookies(role="admin"))
            print(f"⚠️ Fallback класс-уровневая авторизация для домена {domain_name}")
        
        return context
    
    return _create_context


@pytest.fixture(scope="function")
def page_with_domain_auth(domain_aware_authenticated_context):
    """Аутентифицированная страница для конкретного домена."""
    page = domain_aware_authenticated_context.new_page()
    return page
```

## 🔐 ИНТЕГРАЦИЯ ДЛЯ ТЕСТОВ АВТОРИЗАЦИИ

### `tests/auth/conftest.py`
```python
"""Конфигурация тестов авторизации с унифицированным менеджером."""

import pytest
import time
from framework.auth.manager import auth_manager, AuthResult
from framework.utils.api_auth import APIAuthManager


@pytest.fixture(scope="function")
def auth_test_manager(unified_auth_manager):
    """Менеджер для тестирования авторизации."""
    return unified_auth_manager


@pytest.fixture(scope="function") 
def fresh_admin_cookie(auth_test_manager):
    """Свежая кука администратора (без кэширования)."""
    # Очищаем кэш перед получением
    auth_test_manager.clear_cache("admin")
    result = auth_test_manager.get_session_cookie("admin", mode="api")
    if not result.success:
        pytest.fail(f"Не удалось получить свежую куку администратора: {result.error_message}")
    return result.cookie


@pytest.fixture(scope="function")
def multiple_role_cookies(auth_test_manager):
    """Куки для нескольких ролей."""
    roles = ["admin", "user", "moderator", "expert"]
    cookies = {}
    
    for role in roles:
        result = auth_test_manager.get_session_cookie(role)
        if result.success:
            cookies[role] = result.cookie
        else:
            print(f"⚠️ Не удалось получить куку для роли {role}")
    
    return cookies


@pytest.fixture(scope="function")
def api_auth_client():
    """Клиент для API авторизации."""
    return APIAuthManager()


@pytest.fixture(scope="function")
def auth_performance_monitor():
    """Монитор производительности авторизации."""
    class AuthPerformanceMonitor:
        def __init__(self):
            self.measurements = []
        
        def start_timer(self):
            self.start_time = time.time()
        
        def stop_timer(self, operation: str, role: str = "admin"):
            duration = time.time() - self.start_time
            self.measurements.append({
                "operation": operation,
                "role": role,
                "duration": duration,
                "timestamp": time.time()
            })
            return duration
        
        def get_stats(self):
            if not self.measurements:
                return {}
            
            durations = [m["duration"] for m in self.measurements]
            return {
                "total_operations": len(durations),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "total_time": sum(durations)
            }
    
    return AuthPerformanceMonitor()


@pytest.fixture(scope="function")
def cross_domain_auth_checker():
    """Проверка кросс-доменной авторизации."""
    def _check_auth(cookies: list, domains: list):
        results = {}
        import requests
        
        for domain in domains:
            for cookie in cookies:
                session = requests.Session()
                session.cookies.set("test_joint_session", cookie["value"])
                
                try:
                    response = session.get(domain, timeout=10)
                    results[f"{domain}_{cookie['name']}"] = {
                        "status": response.status_code,
                        "success": response.status_code == 200,
                        "content_length": len(response.text)
                    }
                except Exception as e:
                    results[f"{domain}_{cookie['name']}"] = {
                        "status": 0,
                        "success": False,
                        "error": str(e)
                    }
        
        return results
    
    return _check_auth
```

## 🚀 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ В ТЕСТАХ

### Пример интеграционного теста
```python
# tests/integration/example_test.py
import pytest
import allure

@allure.feature("API Тестирование")
@allure.story("Отправка вопроса через API")
@pytest.mark.api
def test_send_question_via_api(admin_api_session):
    """Тест отправки вопроса через API с использованием аутентифицированной сессии."""
    
    question_data = {
        "text": "Тестовый вопрос через API",
        "category": "general"
    }
    
    response = admin_api_session.post("https://expert.bll.by/questions", json=question_data)
    
    assert response.status_code == 200
    assert response.json().get("success") is True


@allure.feature("UI Тестирование") 
@allure.story("Навигация в бургер-меню")
@pytest.mark.ui
def test_burger_menu_navigation(authenticated_page):
    """Тест навигации в бургер-меню с аутентифицированной страницы."""
    
    # Открываем бургер-меню
    burger_button = authenticated_page.locator("a.menu-btn.menu-btn_new")
    burger_button.click()
    
    # Проверяем наличие ссылок
    links = authenticated_page.locator("a.menu_item_link")
    assert links.count() > 0
```

### Пример параметризованного теста
```python
# tests/smoke/burger_menu_params/example_test.py
import pytest
import allure

@allure.feature("Мульти-доменные тесты")
@allure.story("Навигация по доменам")
@pytest.mark.parametrize('multi_domain_context', 
                       ['bll', 'expert', 'bonus', 'ca', 'cp'], 
                       indirect=True, 
                       ids=['Main(bll.by)', 'Expert', 'Bonus', 'CA', 'CP'])
def test_domain_navigation(domain_aware_authenticated_context, multi_domain_context):
    """Тест навигации по разным доменам с авторизацией."""
    
    domain_name, base_url = multi_domain_context
    page = domain_aware_authenticated_context.new_page()
    
    # Переходим на домен
    page.goto(base_url)
    
    # Проверяем, что пользователь авторизован
    assert page.locator("text=Выход").count() > 0
```

## 📊 МОНИТОРИНГ И ЛОГИРОВАНИЕ

### Уровни логирования в фикстурах:
- **DEBUG**: Подробные внутренние операции менеджера
- **INFO**: Успешные операции авторизации
- **WARNING**: Fallback сценарии
- **ERROR**: Ошибки авторизации

### Метрики производительности:
- Время получения куки
- Использование кэша
- Успешность разных методов
- Время валидации сессии