#!/usr/bin/env python3
"""migrate_users_db.py

Скрипт переносит данные из устаревших SQLite-файлов
(`data/users.db`, `projects/user_data/users.db`) в единственную
актуальную базу `secrets/users.db`.

Запуск (dry-run по умолчанию):
    python scripts/maintenance/migrate_users_db.py

Для сохранения изменений используйте флаг ``--apply``:
    python scripts/maintenance/migrate_users_db.py --apply

Скрипт НЕ удаляет старые файлы автоматически — выводит путь, который
можно безопасно удалить после успешной миграции.
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
from pathlib import Path
from typing import List, Tuple

from config.db_settings import DEFAULT_DB_PATH, PROJECT_ROOT
from framework.db_utils.database_manager import DatabaseManager

# Пути старых БД, которые необходимо слить
LEGACY_DB_PATHS: List[Path] = [
    PROJECT_ROOT / "data" / "users.db",
    PROJECT_ROOT / "projects" / "user_data" / "users.db",
]


def rows_to_tuple(rows: List[Tuple]) -> List[Tuple]:
    """Быстрая конвертация результата sqlite в список tuple (для set)."""
    return [tuple(r) for r in rows]


def migrate(apply: bool = False) -> None:
    target_db = DatabaseManager().db_path  # уже указывает на secrets/users.db
    print(f"🎯 Целевая БД: {target_db}")

    conn_target = sqlite3.connect(target_db)
    cur_target = conn_target.cursor()
    cur_target.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            subscription TEXT NOT NULL,
            cookie_file TEXT,
            last_cookie_update TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )"""
    )

    # Получаем уже существующие записи
    cur_target.execute("SELECT login FROM users")
    existing_logins = {row[0] for row in cur_target.fetchall()}

    migrated_total = 0
    for legacy_path in LEGACY_DB_PATHS:
        if not legacy_path.exists():
            continue

        print(f"\n🔍 Чтение {legacy_path} …")
        conn_src = sqlite3.connect(legacy_path)
        cur_src = conn_src.cursor()

        # Попытка разных схем
        possible_columns = [
            ("username", "cookie", "subscription", "role"),
            ("login", "cookie_file", "subscription", "role"),
        ]
        selected_cols = None
        for cols in possible_columns:
            try:
                cur_src.execute(
                    f"SELECT {', '.join(cols)} FROM users LIMIT 1"
                )
                selected_cols = cols
                break
            except sqlite3.OperationalError:
                continue
        if not selected_cols:
            print("⚠️  Не удалось определить схему, пропускаю файл.")
            continue

        cur_src.execute(f"SELECT {', '.join(selected_cols)} FROM users")
        for row in cur_src.fetchall():
            login = row[0]
            cookie_file = row[1]
            subscription = str(row[2])
            role = row[3].lower().strip()

            if login in existing_logins:
                continue  # уже есть в целевой БД

            if apply:
                cur_target.execute(
                    "INSERT OR IGNORE INTO users (login, role, subscription, cookie_file)\n                     VALUES (?, ?, ?, ?)",
                    (login, role, subscription, cookie_file),
                )
                migrated_total += 1
            else:
                print(f"→ Будет добавлен: {login} (role={role})")

        conn_src.close()

    if apply:
        conn_target.commit()
        print(f"✅ Миграция завершена: добавлено {migrated_total} записей.")
    else:
        print("ℹ️  Dry-run завершён. Запустите со --apply для записи изменений.")

    conn_target.close()

    # Подсказка об удалении legacy файлов
    for legacy_path in LEGACY_DB_PATHS:
        if legacy_path.exists():
            print(f"🗑️  Старый файл можно удалить вручную: {legacy_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Миграция пользователей в secrets/users.db")
    parser.add_argument("--apply", action="store_true", help="Записать изменения в целевую БД")
    args = parser.parse_args()
    migrate(apply=args.apply)


if __name__ == "__main__":
    main() 