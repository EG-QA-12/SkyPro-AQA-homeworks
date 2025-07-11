# scripts/ — Вспомогательные скрипты проекта

## Назначение

Папка содержит вспомогательные скрипты для автоматизации, диагностики, генерации тестовых данных и CI/CD.

## Структура

- **parallel_auth.py** — параллельная авторизация пользователей через Playwright
- **setup_secrets.py** — инициализация секретов и переменных окружения
- **setup_paths.py** — настройка путей для окружения
- **demo_secure_usage.py** — пример безопасной работы с секретами
- **dev/seed_sqlite.py** — генерация тестовой SQLite БД
- **maintenance/** — диагностика, анализ и тестирование cookies, playwright, окружения

## Примеры запуска

```bash
python scripts/parallel_auth.py secrets/bulk_users.csv --threads 5 --headless
python scripts/setup_secrets.py
python scripts/maintenance/playwright_cookie_tester.py
```

## Рекомендации
- Все скрипты снабжены docstrings и поддерживают --help
- Для CI/CD используйте только актуальные и поддерживаемые скрипты
- Для диагностики используйте maintenance/

## Добавление новых скриптов
1. Поместите скрипт в scripts/ или соответствующую подпапку
2. Добавьте описание и пример использования в этот README.md 