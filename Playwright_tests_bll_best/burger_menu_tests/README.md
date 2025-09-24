# Burger Menu Tests

Автоматизированные тесты для проверки функциональности burger menu.

## Установка

1. Клонировать репозиторий:
```bash
git clone <repository-url>
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Установить Playwright:
```bash
playwright install
```

4. Создать файл creds.txt с учетными данными:
```bash
echo "your_username" > creds.txt
echo "your_password" >> creds.txt
```
5. Запустить Codegen
```bash
playwright codegen https://bll.by
```
## Запуск тестов

Запуск всех тестов:
```bash
pytest
```

Запуск конкретного теста:
```bash
pytest smoke_test_burger_menu_part1.py
```

## Структура проекта

```
burger_menu_tests/
├── __init__.py           # Инициализация пакета
├── conftest.py          # Фикстуры pytest
├── test_utils.py        # Утилиты для тестов
├── smoke_test_burger_menu_part1.py
├── smoke_test_burger_menu_part2.py
├── smoke_test_burger_menu_part3.py
└── smoke_test_burger_menu_part4.py
```

## Отчеты и логи

- Скриншоты сохраняются в директорию `screenshots/`
- Логи сохраняются в `logs/errors.log`