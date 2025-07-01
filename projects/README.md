# Проект автоматизации тестирования BLL

Этот проект содержит автоматизированные тесты для сайта `https://ca.bll.by`.

## Структура проекта

```
projects/
├── helpers/              # Вспомогательные модули
│   ├── cookie_helper.py  # Работа с cookie-файлами
│   └── README.md         # Документация модуля
├── tests/                # Тестовые сценарии
│   └── test_cookie_auth.py # Тесты авторизации
├── conftest.py           # Конфигурация Pytest
└── README.md             # Этот файл
```

## Настройка окружения

1. Установите Python 3.8+.
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Запуск тестов

Запуск всех тестов:
```bash
pytest
```

Запуск теста авторизации с конкретным cookie-файлом:
```bash
pytest tests/test_cookie_auth.py --cookie-file 1_cookies.json
```

## Документация

- [helpers](./helpers/README.md) - документация вспомогательных модулей.
