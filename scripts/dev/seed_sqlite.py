import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from framework.db_utils.database_manager import DatabaseManager


def seed_database():
    """Заполняет базу данных тестовыми пользователями."""
    users_to_add = [
        {"login": "admin@example.com", "password": "adminpass", "role": "admin", "subscription": "premium"},
        {"login": "user@example.com", "password": "userpass", "role": "user", "subscription": "free"}
    ]

    with DatabaseManager() as db:
        print("Очистка таблицы пользователей...")
        db.conn.execute("DELETE FROM users")
        db.conn.commit()

        print("Добавление тестовых пользователей...")
        for user_data in users_to_add:
            db.add_user(**user_data)
        print("Тестовые пользователи успешно добавлены.")

if __name__ == "__main__":
    seed_database()
