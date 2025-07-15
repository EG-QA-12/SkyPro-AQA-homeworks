"""db_inspector.py
Инструмент командной строки для просмотра содержимого единой базы `secrets/users.db`.

Запуск без аргументов выводит таблицу пользователей с основными полями.

Пример:
    python scripts/maintenance/db_inspector.py

Дополнительные опции можно узнать через ``-h``.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any

# Позволяем запускать скрипт из любой директории проекта
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / 'framework') not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / 'framework'))

from framework.utils.db_utils import DatabaseManager  # noqa: E402


def format_users(rows: List[Dict[str, Any]]) -> str:
    """Формирует красивую текстовую таблицу без сторонних зависимостей."""
    if not rows:
        return "<пусто>"

    headers = [
        ("id", 4),
        ("login", 20),
        ("role", 10),
        ("subscription", 12),
        ("cookie_file", 40),
        ("last_cookie_update", 20),
        ("active", 6),
    ]

    # Вычисляем ширину каждой колонки с учётом фактических данных
    col_sizes = {name: width for name, width in headers}
    for row in rows:
        for name, _ in headers:
            col_sizes[name] = max(col_sizes[name], len(str(row.get(name, ""))) + 2)

    # Формируем строку заголовка
    header_line = " | ".join(name.ljust(col_sizes[name]) for name, _ in headers)
    sep_line = "-+-".join("-" * col_sizes[name] for name, _ in headers)

    lines = [header_line, sep_line]
    for row in rows:
        cells = [
            str(row.get("id", "")).ljust(col_sizes["id"]),
            str(row.get("login", "")).ljust(col_sizes["login"]),
            str(row.get("role", "")).ljust(col_sizes["role"]),
            str(row.get("subscription", "")).ljust(col_sizes["subscription"]),
            str(Path(row.get("cookie_file", "")).name).ljust(col_sizes["cookie_file"]),
            str(row.get("last_cookie_update", ""))[:19].ljust(col_sizes["last_cookie_update"]),
            ("✓" if row.get("is_active", True) else "✗").ljust(col_sizes["active"]),
        ]
        lines.append(" | ".join(cells))
    return "\n".join(lines)


def list_users() -> None:
    """Выводит список всех пользователей."""
    with DatabaseManager() as db:
        users = db.get_users_by_role(role="%")  # получим всех (функция фильтрует по LIKE)
        if not users:  # если метод get_users_by_role не поддерживает %
            users = [db.get_user(row["login"]) for row in users] if users else []
        if not users:
            # fallback manual query
            users = db.execute_query(
                "SELECT id, login, role, subscription, cookie_file, last_cookie_update, is_active FROM users",
                fetch=True,
            )
            users = [
                {
                    "id": r[0],
                    "login": r[1],
                    "role": r[2],
                    "subscription": r[3],
                    "cookie_file": r[4],
                    "last_cookie_update": r[5],
                    "is_active": bool(r[6]),
                }
                for r in users
            ]
    print(format_users(users))


def inspect_db(db_path: str) -> None:
    """Инспектирует БД.

    Args:
        db_path: Путь к БД.
    """
    pass # Placeholder for actual inspection logic


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Инспектор базы пользователей: выводит информацию о пользователях и куках.",
    )
    # Будущие расширения (фильтры) можно добавить сюда
    _ = parser.parse_args()
    list_users()


if __name__ == "__main__":
    main() 