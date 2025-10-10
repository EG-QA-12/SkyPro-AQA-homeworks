# 🏗️ ПЛАН РЕАЛИЗАЦИИ ОБНОВЛЕННОГО МЕНЕДЖЕРА АВТОРИЗАЦИИ

## 📋 ОБЗОР

Данный план описывает реализацию унифицированного менеджера авторизации с интеграцией через `conftest.py` для всех групп тестов.

## 🎯 ЦЕЛЬ

Создать единый менеджер авторизации, который будет:
- Интегрирован через `conftest.py` для всех групп тестов
- Поддерживать все существующие сценарии авторизации
- Обеспечивать обратную совместимость
- Упрощать поддержку и расширение

## 📝 ПЛАН РЕАЛИЗАЦИИ

### Этап 1: Создание основного менеджера авторизации

#### 1.1. Создать файл `framework/auth/manager.py`
```python
"""
Унифицированный менеджер авторизации.

Единая точка входа для всех типов авторизации в проекте.
Интегрируется через conftest.py для всех групп тестов.
"""

import json
import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from framework.utils.cookie_constants import COOKIE_NAME
from framework.utils.url_utils import add_allow_session_param, is_headless

logger = logging.getLogger(__name__)


class AuthMode(Enum):
    """Режимы авторизации."""
    AUTO = "auto" # Автоматический выбор
    API = "api"    # API авторизация
    UI = "ui"      # UI авторизация
    CACHE = "cache"  # Только из кэша


@dataclass
class AuthResult:
    """Результат авторизации."""
    success: bool
    cookie: Optional[str] = None
    method: str = ""
    duration: float = 0.0
    from_cache: bool = False
    error_message: Optional[str] = None


class UnifiedAuthManager:
    """
    Унифицированный менеджер авторизации.
    
    Интегрируется через conftest.py и предоставляет единый интерфейс
    для всех типов авторизации (API, UI, кросс-доменная).
    """
    
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 минут
        self._api_timeout = 30
        self._base_url = "https://ca.bll.by"
        
    def get_session_cookie(self, role: str = "admin", 
                          mode: AuthMode = AuthMode.AUTO) -> AuthResult:
        """
        Получить сессионную куку для указанной роли.
        
        Args:
            role: Роль пользователя (admin, user, moderator, expert)
            mode: Режим авторизации
            
        Returns:
            AuthResult: Результат авторизации с кукой
        """
        start_time = time.time()
        
        # Проверяем кэш если не в UI режиме
        if mode != AuthMode.UI:
            cached_cookie = self._get_cached_cookie(role)
            if cached_cookie:
                duration = time.time() - start_time
                return AuthResult(
                    success=True,
                    cookie=cached_cookie,
                    method="cache",
                    duration=duration,
                    from_cache=True
                )
        
        # Выбираем метод в зависимости от режима
        if mode == AuthMode.API or (mode == AuthMode.AUTO and self._should_use_api()):
            result = self._api_authenticate(role)
        elif mode == AuthMode.UI or (mode == AuthMode.AUTO and not self._should_use_api()):
            result = self._ui_authenticate(role)
        else:
            result = self._try_all_methods(role)
        
        duration = time.time() - start_time
        result.duration = duration
        
        # Сохраняем в кэш при успехе
        if result.success and result.cookie:
            self._set_cached_cookie(role, result.cookie)
        
        return result
    
    def _get_cached_cookie(self, role: str) -> Optional[str]:
        """Получить куку из кэша."""
        cache_entry = self._cache.get(role)
        if not cache_entry:
            return None
            
        cookie, timestamp = cache_entry
        if time.time() - timestamp < self._cache_ttl:
            logger.debug(f"Кука для роли {role} получена из кэша")
            return cookie
        else:
            # Удаляем устаревшую куку
            del self._cache[role]
            return None
    
    def _set_cached_cookie(self, role: str, cookie: str):
        """Сохранить куку в кэш."""
        self._cache[role] = (cookie, time.time())
        logger.debug(f"Кука для роли {role} сохранена в кэш")
    
    def _should_use_api(self) -> bool:
        """Определить, использовать ли API авторизацию."""
        # В headless режиме предпочитаем API
        return is_headless() or os.getenv('USE_API_AUTH', 'false').lower() == 'true'
    
    def _api_authenticate(self, role: str) -> AuthResult:
        """API авторизация."""
        try:
            # Получаем учетные данные
            username, password = self._get_credentials_for_role(role)
            if not username or not password:
                return AuthResult(
                    success=False,
                    error_message=f"Учетные данные для роли {role} не найдены"
                )
            
            # Выполняем API авторизацию
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f"{self._base_url}/login"
            })
            
            login_data = {
                'lgn': username,
                'password': password,
                'remember': '1'
            }
            
            response = session.post(
                f"{self._base_url}/login",
                data=login_data,
                timeout=self._api_timeout,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                # Ищем нужную куку
                for cookie in response.cookies:
                    if cookie.name == COOKIE_NAME:
                        return AuthResult(
                            success=True,
                            cookie=cookie.value,
                            method="api"
                        )
            
            return AuthResult(
                success=False,
                error_message=f"API авторизация не удалась: {response.status_code}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка API авторизации для роли {role}: {e}")
            return AuthResult(
                success=False,
                error_message=str(e)
            )
    
    def _ui_authenticate(self, role: str) -> AuthResult:
        """UI авторизация (через Playwright - заглушка)."""
        # Этот метод будет реализован позже через интеграцию с Playwright
        # Пока возвращаем ошибку
        return AuthResult(
            success=False,
            error_message="UI авторизация временно недоступна"
        )
    
    def _try_all_methods(self, role: str) -> AuthResult:
        """Попробовать все методы авторизации."""
        methods = [self._try_env_auth, self._try_file_auth, self._api_authenticate]
        
        for method in methods:
            try:
                result = method(role)
                if result.success and result.cookie:
                    logger.info(f"Авторизация для роли {role} успешна через {result.method or method.__name__}")
                    return result
            except Exception as e:
                logger.warning(f"Метод {method.__name__} не удался: {e}")
                continue
        
        return AuthResult(
            success=False,
            error_message="Все методы авторизации не удалась"
        )
    
    def _try_env_auth(self, role: str) -> AuthResult:
        """Попробовать получить куку из ENV переменных."""
        role_key = role.upper().replace("-", "_")
        candidates = [f"SESSION_COOKIE_{role_key}", "SESSION_COOKIE"]
        
        for key in candidates:
            cookie = os.getenv(key)
            if cookie:
                # Проверяем валидность куки
                if self._validate_cookie(cookie):
                    return AuthResult(
                        success=True,
                        cookie=cookie.strip(),
                        method="env"
                    )
        
        return AuthResult(success=False)
    
    def _try_file_auth(self, role: str) -> AuthResult:
        """Попробовать получить куку из файлов."""
        project_root = Path(__file__).parent.parent.parent
        cookies_dir = project_root / "cookies"
        
        # Текстовый файл
        txt_path = cookies_dir / f"{role}_session.txt"
        if txt_path.exists():
            try:
                content = txt_path.read_text(encoding="utf-8").strip()
                if self._validate_cookie(content):
                    return AuthResult(
                        success=True,
                        cookie=content,
                        method="file_txt"
                    )
            except Exception as e:
                logger.warning(f"Ошибка чтения {txt_path}: {e}")
        
        # JSON файл Playwright формата
        json_path = cookies_dir / f"{role}_cookies.json"
        if json_path.exists():
            try:
                raw_content = json_path.read_text(encoding="utf-8")
                data = json.loads(raw_content)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("name") == COOKIE_NAME:
                            value = item.get("value")
                            if isinstance(value, str) and self._validate_cookie(value):
                                return AuthResult(
                                    success=True,
                                    cookie=value,
                                    method="file_json"
                                )
            except Exception as e:
                logger.warning(f"Ошибка чтения {json_path}: {e}")
        
        return AuthResult(success=False)
    
    def _validate_cookie(self, cookie: str) -> bool:
        """Базовая валидация куки."""
        if not isinstance(cookie, str):
            return False
        value = cookie.strip()
        if not value:
            return False
        if len(value) < 8:
            return False
        if " " in value:
            return False
        return True
    
    def _get_credentials_for_role(self, role: str) -> Tuple[Optional[str], Optional[str]]:
        """Получить учетные данные для роли."""
        # Попробуем получить из ENV
        username_key = f"AUTH_USERNAME_{role.upper()}"
        password_key = f"AUTH_PASSWORD_{role.upper()}"
        
        username = os.getenv(username_key) or os.getenv("AUTH_USERNAME")
        password = os.getenv(password_key) or os.getenv("AUTH_PASSWORD")
        
        # Попробуем получить из конфигурационного файла
        if not username or not password:
            config_path = Path(__file__).parent.parent / "config" / "auth_config.json"
            if config_path.exists():
                try:
                    config = json.loads(config_path.read_text('utf-8'))
                    user_config = config.get("users", {}).get(role, {})
                    username = user_config.get("username", username)
                    password = user_config.get("password", password)
                except Exception as e:
                    logger.warning(f"Ошибка чтения конфигурации: {e}")
        
        return username, password
    
    def get_auth_cookies(self, role: str = "admin", domain: str = ".bll.by") -> List[Dict[str, Any]]:
        """Получить куки в формате Playwright."""
        result = self.get_session_cookie(role)
        if result.success and result.cookie:
            return [{
                "name": COOKIE_NAME,
                "value": result.cookie,
                "domain": domain,
                "path": "/",
                "sameSite": "Lax"
            }]
        return []
    
    def clear_cache(self, role: Optional[str] = None):
        """Очистить кэш авторизации."""
        if role:
            if role in self._cache:
                del self._cache[role]
                logger.debug(f"Кэш для роли {role} очищен")
        else:
            self._cache.clear()
            logger.debug("Весь кэш авторизации очищен")
    
    def validate_session(self, cookie: str) -> bool:
        """Валидация сессии."""
        # Простая валидация - проверка длины и формата
        return self._validate_cookie(cookie)


# Глобальный экземпляр для использования в conftest.py
auth_manager = UnifiedAuthManager()


def get_session_cookie(role: str = "admin") -> Optional[str]:
    """Удобная функция для получения куки (для обратной совместимости)."""
    result = auth_manager.get_session_cookie(role)
    return result.cookie if result.success else None


def get_auth_cookies(role: str = "admin", domain: str = ".bll.by") -> List[Dict[str, Any]]:
    """Удобная функция для получения кук в формате Playwright."""
    return auth_manager.get_auth_cookies(role, domain)
```

### Этап 2: Интеграция через conftest.py

#### 2.1. Обновить корневой `conftest.py`
```python
"""Корневой conftest для интеграции унифицированного менеджера авторизации."""

import pytest
from framework.auth.manager import auth_manager, get_session_cookie, get_auth_cookies

# Добавляем фикстуры авторизации в глобальный доступ
@pytest.fixture(scope="session")
def unified_auth_manager():
    """Унифицированный менеджер авторизации."""
    return auth_manager

@pytest.fixture(scope="session") 
def admin_session_cookie():
    """Кука администратора через унифицированный менеджер."""
    return get_session_cookie("admin")

@pytest.fixture(scope="session")
def user_session_cookie():
    """Кука обычного пользователя через унифицированный менеджер."""
    return get_session_cookie("user")
```

#### 2.2. Обновить `tests/integration/conftest.py`
```python
"""Конфигурация интеграционных тестов с унифицированной авторизацией."""

import pytest
from framework.auth.manager import get_auth_cookies

@pytest.fixture
def fx_auth_manager():
    """Менеджер авторизации для интеграционных тестов."""
    from framework.auth.manager import auth_manager
    return auth_manager

@pytest.fixture
def admin_context(browser):
    """Браузерный контекст с авторизацией администратора."""
    context = browser.new_context()
    cookies = get_auth_cookies("admin")
    if cookies:
        context.add_cookies(cookies)
    return context
```

#### 2.3. Обновить `tests/smoke/burger_menu/conftest.py`
```python
"""Конфигурация smoke тестов бургер-меню с унифицированной авторизацией."""

import pytest
from framework.auth.manager import get_auth_cookies

@pytest.fixture(scope="class")
def authenticated_burger_context(browser):
    """Аутентифицированный контекст для тестов бургер-меню."""
    context = browser.new_context()
    cookies = get_auth_cookies("admin")
    if cookies:
        context.add_cookies(cookies)
    return context
```

#### 2.4. Обновить `tests/smoke/burger_menu_params/conftest.py`
```python
"""Конфигурация параметризованных тестов с унифицированной авторизацией."""

import pytest
from framework.auth.manager import auth_manager

@pytest.fixture(scope="function")
def domain_aware_authenticated_context(browser, multi_domain_context):
    """Контекст с авторизацией, адаптированный под домен."""
    context = browser.new_context()
    domain_name, base_url = multi_domain_context
    
    print(f"🎯 Домен {domain_name}: используем унифицированную авторизацию")
    session_cookie = auth_manager.get_valid_session_cookie(role="admin")
    
    if session_cookie:
        # Добавляем куку в контекст
        context.add_cookies([session_cookie])
        print(f"✅ Авторизация для домена {domain_name} выполнена")
    else:
        # Fallback на стандартную авторизацию
        from framework.utils.auth_cookie_provider import get_auth_cookies
        context.add_cookies(get_auth_cookies(role="admin"))
    
    return context
```

### Этап 3: Создание вспомогательных утилит

#### 3.1. Создать `framework/auth/utils.py`
```python
"""Вспомогательные утилиты для унифицированной авторизации."""

from typing import Dict, Any, List
from framework.auth.manager import auth_manager

def is_guest(page) -> bool:
    """Проверить, является ли пользователь гостем."""
    try:
        # Проверяем наличие элементов авторизации
        logout_elements = page.locator("text=Выход").count() + \
                         page.locator("[href*='logout']").count() + \
                         page.locator(".user-in__nick").count()
        return logout_elements == 0
    except:
        return True

def is_authorized(page) -> bool:
    """Проверить, авторизован ли пользователь."""
    try:
        # Проверяем наличие элементов авторизации
        logout_elements = page.locator("text=Выход").count() + \
                         page.locator("[href*='logout']").count()
        return logout_elements > 0
    except:
        return False

def get_random_user_cookie(context) -> List[Dict[str, Any]]:
    """Получить куки случайного пользователя (для тестов)."""
    # Попробуем разные роли
    for role in ["admin", "user", "moderator"]:
        cookies = auth_manager.get_auth_cookies(role)
        if cookies:
            return cookies
    return []
```

### Этап 4: Обновление фикстур

#### 4.1. Обновить `framework/fixtures/auth_fixtures.py`
```python
"""Обновленные фикстуры авторизации с использованием унифицированного менеджера."""

import pytest
from typing import Generator
from playwright.sync_api import Browser, BrowserContext, Page

from framework.auth.manager import auth_manager, get_auth_cookies


@pytest.fixture(scope="function")
def browser_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Базовая фикстура для создания браузерного контекста."""
    context = browser.new_context()
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function") 
def clean_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Фикстура для создания контекста без авторизации."""
    context = browser.new_context()
    # Очищаем все куки
    context.clear_cookies()
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def authenticated_admin(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Фикстура для авторизованного администратора через унифицированный менеджер."""
    context = browser.new_context()
    
    # Получаем куки через унифицированный менеджер
    cookies = get_auth_cookies("admin")
    
    if cookies:
        context.add_cookies(cookies)
        print("✅ Авторизация администратора через унифицированный менеджер")
    else:
        print("❌ Не удалось получить куки администратора")
    
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def authenticated_user(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Фикстура для обычного авторизованного пользователя."""
    context = browser.new_context()
    
    cookies = get_auth_cookies("user")
    
    if cookies:
        context.add_cookies(cookies)
        print("✅ Авторизация пользователя через унифицированный менеджер")
    else:
        print("❌ Не удалось получить куки пользователя")
    
    try:
        yield context
    finally:
        context.close()


@pytest.fixture(scope="function")
def auth_page(authenticated_admin) -> Generator[Page, None, None]:
    """Фикстура для страницы с авторизованным администратором."""
    page = authenticated_admin.new_page()
    try:
        yield page
    finally:
        page.close()


@pytest.fixture(scope="function")
def isolated_context(browser: Browser) -> Generator[tuple[BrowserContext, Page], None, None]:
    """Фикстура для создания полностью изолированного контекста."""
    context = browser.new_context()
    page = context.new_page()
    try:
        yield context, page
    finally:
        page.close()
        context.close()
```

### Этап 5: Обновление тестов

#### 5.1. Пример обновления интеграционного теста
```python
# tests/integration/test_question_submission_optimized.py
import pytest
from framework.auth.manager import auth_manager

@pytest.fixture
def fx_auth_manager():
    """Обновленная фикстура для менеджера авторизации."""
    return auth_manager

def test_send_question_with_unified_auth(fx_auth_manager):
    """Тест отправки вопроса с унифицированной авторизацией."""
    # Получаем валидную куку через унифицированный менеджер
    result = fx_auth_manager.get_session_cookie(role="admin")
    assert result.success, "Не удалось получить валидную куку"
    
    # Используем куку для отправки вопроса
    # ... остальная логика теста
```

### Этап 6: Создание миграционного гайда

#### 6.1. Документ `docs/MIGRATION_GUIDE_UNIFIED_AUTH.md`
```markdown
# 🔄 Гайд по миграции на унифицированный менеджер авторизации

## 📋 План миграции

### Этап 1: Подготовка (1 день)
1. Установить новый менеджер авторизации
2. Обновить conftest.py файлы
3. Проверить обратную совместимость

### Этап 2: Интеграция (2 дня) 
1. Обновить фикстуры
2. Обновить тесты по группам
3. Провести тестирование

### Этап 3: Очистка (1 день)
1. Удалить устаревший код
2. Обновить документацию
3. Финальное тестирование
```

## 🎯 ПРЕИМУЩЕСТВА НОВОГО ПОДХОДА

### 1. Единая точка интеграции
- Все группы тестов используют один и тот же менеджер
- Легко обновлять и поддерживать
- Централизованное управление

### 2. Гибкость и расширяемость
- Поддержка разных режимов авторизации
- Автоматическое кэширование
- Интеллектуальный выбор метода

### 3. Совместимость
- Обратная совместимость с существующими тестами
- Поддержка всех типов авторизации
- Интеграция с существующими фикстурами

## 🔧 ТЕХНИЧЕСКИЕ ДЕТАЛИ

### Архитектура
```
conftest.py (глобальный уровень)
    ↓
UnifiedAuthManager
    ├─ API авторизация
    ├─ Файловая авторизация  
    ├─ ENV авторизация
    └─ Кэширование
    ↓
Все группы тестов
```

### Поток выполнения
1. Тест запрашивает авторизацию через фикстуру
2. conftest.py предоставляет унифицированный менеджер
3. Менеджер выбирает оптимальный метод авторизации
4. Результат кэшируется и предоставляется тесту

## 📊 МЕТРИКИ И МОНИТОРИНГ

### Логирование
- Метод авторизации
- Время выполнения
- Источник куки
- Статус кэширования

### Мониторинг
- Уровень успеха авторизации
- Время отклика
- Использование разных методов

## 🚀 ПЛАН ВНЕДРЕНИЯ

### Фаза 1: Параллельный запуск
- Новый менеджер работает параллельно со старым
- Постепенная миграция тестов
- Проверка стабильности

### Фаза 2: Миграция
- Перевод всех тестов на новый менеджер
- Удаление старого кода
- Обновление документации

### Фаза 3: Оптимизация
- Оптимизация производительности
- Улучшение кэширования
- Добавление новых функций
```
