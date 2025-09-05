# Руководство по тестированию авторизации

## Обзор

Это руководство описывает систему авторизации в проекте BLL Tests и как с ней работать в контексте автоматизированного тестирования. Система авторизации построена на нескольких ключевых компонентах, обеспечивающих гибкость, надежность и безопасность.

## Компоненты системы авторизации

### 1. AuthCookieProvider

`AuthCookieProvider` - это основной провайдер авторизационных кук. Он реализует стратегию получения куки `test_joint_session` из различных источников в порядке приоритета:

1. **Переменные окружения**: `SESSION_COOKIE_{ROLE}` или `SESSION_COOKIE`
2. **Локальные файлы**: `cookies/{role}_session.txt` или `cookies/{role}_cookies.json`
3. **API-логин**: автоматический логин через `APIAuthManager` (если разрешено)

#### Пример использования:
```python
from framework.utils.auth_cookie_provider import AuthCookieProvider

provider = AuthCookieProvider()
cookie = provider.get_auth_cookie(role="admin")
```

### 2. APIAuthManager

`APIAuthManager` обеспечивает быструю и надежную авторизацию через HTTP запросы, минуя проблемы браузерной автоматизации и антибот защиты. Он поддерживает параллельную обработку для максимальной производительности.

#### Пример использования:
```python
from framework.utils.api_auth import APIAuthManager

manager = APIAuthManager()
result = manager.login_user(username="admin", password="password")
if result.success:
    session_token = result.session_token
```

### 3. SmartAuthManager

`SmartAuthManager` управляет авторизацией, проверяя валидность кук и обновляя их только при необходимости. Он обеспечивает интеллектуальное кэширование и автоматическое обновление сессий.

#### Пример использования:
```python
from framework.utils.smart_auth_manager import SmartAuthManager

auth_manager = SmartAuthManager()
cookie = auth_manager.get_valid_session_cookie(role="admin")
```

### 4. BaseAPIClient и AdminAPIClient

API клиенты автоматически обрабатывают авторизацию и обновление сессий. Они интегрированы с `SmartAuthManager` для обеспечения прозрачной авторизации.

#### Пример использования:
```python
from framework.api.admin_client import AdminAPIClient

client = AdminAPIClient(role="admin")
# Авторизация происходит автоматически
questions = client.get_moderation_panel_data()
```

## Порядок получения кук

Система авторизации следует четко определенному порядку получения кук:

1. **ENV**: Сначала проверяются переменные окружения
2. **Файлы**: Затем проверяются локальные файлы с куками
3. **API-логин**: Только в крайнем случае выполняется API-логин

Этот порядок соответствует принципам Управления Окружением и Изоляции: сначала используются явные конфиги, затем артефакты прошлых запусков, и только в крайнем случае выполняется сетевой логин.

## Конфигурация

### Переменные окружения

Для работы системы авторизации используются следующие переменные окружения:

- `SESSION_COOKIE_{ROLE}` - кука для конкретной роли (например, `SESSION_COOKIE_ADMIN`)
- `SESSION_COOKIE` - кука по умолчанию
- `API_USERNAME_{ROLE}` - имя пользователя для API-логина конкретной роли
- `API_PASSWORD_{ROLE}` - пароль для API-логина конкретной роли
- `API_USERNAME` - имя пользователя для API-логина по умолчанию
- `API_PASSWORD` - пароль для API-логина по умолчанию

### Файлы кук

Файлы кук хранятся в директории `cookies/` и могут быть двух форматов:

1. **Текстовый файл**: `cookies/{role}_session.txt` - содержит только значение куки
2. **JSON файл**: `cookies/{role}_cookies.json` - содержит полную информацию о куках в формате Playwright

### Файл конфигурации

Конфигурация авторизации также может храниться в файле `config/auth_config.json`:

```json
{
  "login_url": "https://ca.bll.by",
  "users": {
    "admin": {
      "username": "admin_user",
      "password": "admin_password"
    },
    "moderator": {
      "username": "moderator_user",
      "password": "moderator_password"
    },
    "user": {
      "username": "user_user",
      "password": "user_password"
    }
  }
}
```

## Тестирование авторизации

### Быстрое тестирование

Для быстрого тестирования авторизации можно использовать скрипт:

```bash
python tests/integration/test_auth_quick.py
```

### Массовая авторизация

Для массовой авторизации пользователей используется скрипт:

```bash
python scripts/run_auth_tests.py
```

### Тесты с фикстурами

В новом фреймворке доступны удобные фикстуры для работы с авторизацией:

```python
import pytest

def test_with_admin_client(admin_client):
    # admin_client уже авторизован
    questions = admin_client.get_moderation_panel_data()
    assert len(questions) > 0

def test_with_session_cookie(session_cookie):
    # session_cookie содержит валидную куку
    assert session_cookie is not None
```

## Лучшие практики

### 1. Безопасность

- Никогда не храните пароли в коде
- Используйте переменные окружения для чувствительных данных
- Регулярно обновляйте куки и проверяйте их валидность

### 2. Производительность

- Используйте кэширование кук через `SmartAuthManager`
- Избегайте частых API-логинов
- Используйте параллельную авторизацию при массовых операциях

### 3. Надежность

- Всегда проверяйте валидность кук перед использованием
- Обрабатывайте ошибки авторизации корректно
- Используйте автоматическое обновление сессий при 401/419 ошибках

## Диагностика проблем

### Частые ошибки

1. **Кука не найдена**: Проверьте наличие кук в ENV, файлах или возможность API-логина
2. **Невалидная кука**: Кука истекла или была отозвана
3. **Ошибка API-логина**: Неверные учетные данные или проблемы с сетью

### Логирование

Система авторизации имеет подробное логирование, которое помогает диагностировать проблемы:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Отладка

Для отладки авторизации можно использовать специальные скрипты:

```bash
python scripts/maintenance/cookie_tester.py
python scripts/maintenance/flexible_auth.py
```

## Расширение системы авторизации

### Добавление новых ролей

Для добавления новой роли необходимо:

1. Добавить учетные данные в `config/auth_config.json`
2. Установить соответствующие переменные окружения
3. Создать файлы кук в директории `cookies/`

### Создание собственных провайдеров

Для создания собственного провайдера кук унаследуйтесь от `AuthCookieProvider`:

```python
from framework.utils.auth_cookie_provider import AuthCookieProvider

class CustomAuthCookieProvider(AuthCookieProvider):
    def _get_cookie_from_custom_source(self, role: str) -> Optional[str]:
        # Реализация получения куки из собственного источника
        pass
    
    def get_auth_cookie(self, role: str = "admin", use_api_login: bool = True) -> Optional[str]:
        # Сначала пробуем собственный источник
        custom_cookie = self._get_cookie_from_custom_source(role)
        if custom_cookie:
            return custom_cookie
        
        # Затем используем стандартную логику
        return super().get_auth_cookie(role, use_api_login)