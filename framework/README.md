# Фреймворк автоматизации тестирования

## Обзор

Фреймворк предоставляет современный, типизированный и удобный подход к написанию автоматизированных тестов. Фреймворк включает в себя:

- **API клиенты** с автоматической авторизацией и обработкой ошибок
- **Утилиты** для повторного использования компонентов
- **Вспомогательные инструменты** для типичных операций

## Структура фреймворка

```
framework/
├── api/                    # Современные API клиенты
│   ├── base_client.py     # Базовый API клиент с retry логикой
│   └── admin_client.py    # Административный клиент
├── utils/                 # Общие утилиты
│   ├── auth_utils.py      # Утилиты авторизации
│   ├── html_parser.py     # Парсер HTML
│   ├── smart_auth_manager.py # Интеллектуальный менеджер авторизации
│   └── [другие утилиты]
├── app/                   # Специфичный код приложения
│   └── pages/            # Page Objects
└── README.md             # Этот файл
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

#### AdminAPIClient
Специализированный клиент для административных операций:
- Работа с панелью модерации
- Публикация вопросов и ответов
- Взятие записей в работу

```python
from framework.api.admin_client import AdminAPIClient

client = AdminAPIClient(role="admin")
entries = client.get_moderation_panel_data(limit=100)
```

### 2. Утилиты

#### Auth Utils
```python
from framework.utils.auth_utils import get_valid_session_cookie

# Получение валидной сессионной куки
cookie = get_valid_session_cookie(role="admin")
```

#### HTML Parser
```python
from framework.utils.html_parser import ModerationPanelParser

# Парсинг панели модерации
parser = ModerationPanelParser()
entries = parser.get_moderation_panel_data(session_cookie, limit=100)
```

#### Smart Auth Manager
```python
from framework.utils.smart_auth_manager import SmartAuthManager

# Интеллектуальное управление авторизацией
auth_manager = SmartAuthManager()
cookie = auth_manager.get_valid_session_cookie(role="admin")
```

## Документация

- [Руководство по тестированию авторизации](../docs/auth_testing_guide.md)
- [Справочник API системы авторизации](../docs/auth_api_reference.md)
- [Руководство по миграции](../docs/MIGRATION_GUIDE.md)

## Рекомендации по использованию

1. **Используйте API клиенты** для упрощения работы с API
2. **Используйте утилиты** для повторяющихся операций
3. **Следуйте существующим паттернам** в коде
4. **Добавляйте документацию** к новым функциям
5. **Используйте встроенные методы проверки** для повышения надежности

## Поддержка и развитие

Фреймворк активно развивается и поддерживается. Для вопросов и предложений:
- Создавайте issues в репозитории
- Обращайтесь к Lead SDET Architect
- Участвуйте в code review новых функций

## Лицензия

Этот фреймворк разработан специально для проекта BLL и не предназначен для внешнего использования.
