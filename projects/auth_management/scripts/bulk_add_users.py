#!/usr/bin/env python
"""
Массовое добавление пользователей в БД.

Перемещён в `scripts/`.
Поддерживает:
1. Добавление пользователей из встроенного списка `bulk_users` (пример).
2. Добавление пользователей из CSV (`--csv path`).

CSV-формат:
    username,password,role,subscription

- Для ролей `admin` и `moderator` subscription автоматически устанавливается равным `3`.
- Пароли хешируются (bcrypt) через DatabaseManager.
"""
import argparse
import csv
import os
import sys
from typing import List, Dict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from projects.auth_management.database import DatabaseManager  # noqa: E402
from projects.auth_management.logger import logger  # noqa: E402

# ---------------------------------------------------------------------------
# Данные «по умолчанию» (используются, если не указан --csv)
# ---------------------------------------------------------------------------

bulk_users: List[Dict[str, str]] = [
    {"username": "test_bulk1", "password": "BulkPass1", "role": "tester", "subscription": 1},
    {"username": "test_bulk2", "password": "BulkPass2", "role": "tester", "subscription": 2},
]


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def add_users_from_list(users: List[Dict[str, str]]) -> int:
    """Добавляет пользователей из списка словарей.

    Returns:
        Количество успешно добавленных пользователей.
    """
    db = DatabaseManager()
    created = 0
    for user in users:
        username = user.get("username")
        password = user.get("password")
        if not username or not password:
            logger.warning("Пропуск записи без username/password: %s", user)
            continue

        role = user.get("role", "user")
        subscription = int(user.get("subscription", 1))
        if role in {"admin", "moderator"}:
            subscription = 3

        try:
            db.create_user(username, password, role, subscription)
            created += 1
            logger.info("Добавлен пользователь %s (role=%s, sub=%s)", username, role, subscription)
        except Exception as exc:  # noqa: BLE001
            logger.error("Не удалось добавить %s: %s", username, exc)
    return created


def add_users_from_csv(csv_path: str) -> int:
    """Читает CSV и передаёт данные в `add_users_from_list`."""
    if not os.path.exists(csv_path):
        logger.error("CSV %s не найден", csv_path)
        return 0
    with open(csv_path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        users = []
        for row in reader:
            users.append({
                "username": row.get("username") or row.get("login"),
                "password": row.get("password"),
                "role": row.get("role", "user"),
                "subscription": row.get("subscription", 1),
            })
    return add_users_from_list(users)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Массовое добавление пользователей в БД")
    parser.add_argument("--csv", help="Путь к CSV с пользователями", required=False)
    args = parser.parse_args()

    if args.csv:
        count = add_users_from_csv(args.csv)
        print(f"Импортировано пользователей: {count}")
    else:
        count = add_users_from_list(bulk_users)
        print(f"Добавлено пользователей из встроенного списка: {count}")


if __name__ == "__main__":
    main()
