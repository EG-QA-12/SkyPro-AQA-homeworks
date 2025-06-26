# BLL Tests: Монорепозиторий автотестов и сервисов

## Структура проекта

```
BLL_tests/
├── README.md                 # (этот файл)
├── auth_project/             # Бэкенд: логика авторизации, работа с БД, скрипты
│   ├── src/                  # Основная бизнес-логика
│   ├── scripts/              # Утилитарные скрипты
│   ├── tests/                # Тесты (unit, integration, e2e)
│   │   ├── integration/      # Unit и интеграционные тесты
│   │   └── e2e/             # End-to-end тесты
│   └── README.md            # Документация проекта
└── e2e_tests/               # [DEPRECATED] Переехало в auth_project/tests/e2e/

## Быстрый старт

1. Клонируйте репозиторий и перейдите в нужную директорию
2. Перейдите в `auth_project/` и выполните:
   ```bash
   pip install -r requirements.txt
   python scripts/init_users.py
   ```
3. Перейдите в `e2e_tests/` и выполните:
   ```bash
   pip install playwright pytest pytest-playwright
   playwright install
   pytest -v tests/
   ```

## Описание подпроектов

### [auth_project/](auth_project/README.md)
- Бэкенд, управление пользователями, авторизация, работа с базой данных
- Скрипты для инициализации и импорта пользователей
- Подробная документация: [auth_project/README.md](auth_project/README.md)

### [e2e_tests/](e2e_tests/README.md)
- End-to-End тесты (Playwright + Pytest)
- Примеры тестов, фикстуры, инфраструктура для CI/CD
- Подробная документация: [e2e_tests/README.md](e2e_tests/README.md)

## Советы по развитию
- Храните реальные секреты только в локальных файлах (`creds.env`), не коммитьте их в git
- Используйте `.gitignore` для исключения временных и чувствительных данных
- Для новых подпроектов создавайте отдельный README.md с подробностями

---

_Если вы впервые — начните с чтения README в каждой ключевой папке!_
