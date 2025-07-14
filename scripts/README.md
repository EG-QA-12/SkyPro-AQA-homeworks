# scripts/ — Вспомогательные скрипты проекта

## Назначение

Папка содержит вспомогательные скрипты для автоматизации, диагностики, генерации тестовых данных и CI/CD.

## Структура

- **projects/auth_management/scripts/parallel_auth_optimized.py** — оптимизированная параллельная авторизация (ThreadPool + прогресс-бар)
- **scripts/maintenance/login_with_cookies.py** — авторизация на любом *.bll.by с использованием сохранённых куков
- **setup_secrets.py** — инициализация секретов и переменных окружения
- **setup_paths.py** — настройка путей для окружения
- **demo_secure_usage.py** — пример безопасной работы с секретами
- **dev/seed_sqlite.py** — генерация тестовой SQLite БД
- **maintenance/** — диагностика, анализ и тестирование cookies, playwright, окружения

## Примеры запуска

```bash
# Параллельная авторизация (рекомендуется)
python projects/auth_management/scripts/parallel_auth_optimized.py secrets/bulk_users.csv --threads 5 --headless

# Настройка секретов
python scripts/setup_secrets.py

# Cookie-тестирование
python scripts/maintenance/playwright_cookie_tester.py

# Авторизация с куками
python scripts/maintenance/login_with_cookies.py --role expert --url https://expert.bll.by/ --headed
```

## Рекомендации
- Все скрипты снабжены docstrings и поддерживают --help
- Для CI/CD используйте только актуальные и поддерживаемые скрипты
- Для диагностики используйте maintenance/

## Добавление новых скриптов
1. Поместите скрипт в scripts/ или соответствующую подпапку
2. Добавьте описание и пример использования в этот README.md 