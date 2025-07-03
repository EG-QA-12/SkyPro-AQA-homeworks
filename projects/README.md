# projects/ — интеграционные подпроекты и bulk-операции

В этой папке находятся интеграционные подпроекты, bulk-скрипты и эксперименты, связанные с автоматизацией BLL.

## Основная структура проекта теперь вынесена в корень

- **framework/** — основной код фреймворка, Page Object-ы, утилиты, фикстуры
- **tests/** — все тесты (e2e, integration, unit, visual, auth)
- **scripts/** — вспомогательные и CI/CD-скрипты
- **config/** — конфигурация окружения, секреты, настройки браузеров

## Что находится в projects/

- **auth_management/** — bulk-авторизация, массовое управление пользователями, интеграционные скрипты
- **...** — другие подпроекты и эксперименты

## Примеры запуска bulk-скриптов

```bash
python projects/auth_management/scripts/bulk_add_users.py --csv data/users.csv
python projects/auth_management/scripts/authorize_users_from_csv.py --csv data/users.csv
```

## Документация

- [ARCHITECTURE.md](../ARCHITECTURE.md) — архитектура и структура проекта
- [TESTING_GUIDE.md](../TESTING_GUIDE.md) — гайд по запуску и написанию тестов
- [auth_management/README.md](./auth_management/README.md) — подробности по bulk-скриптам

---

> **Внимание:** Все новые тесты, Page Object-ы и утилиты размещайте только в корневых папках `framework/`, `tests/`, `scripts/`.
