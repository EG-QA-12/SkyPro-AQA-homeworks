import sys
import os

# Add project root to sys.path for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.user_manager import UserManager
from src.config import config
import csv
from datetime import datetime, timezone
import sqlite3
from typing import List, Dict

"""
Скрипт для инициализации пользователей в системе.
"""

def get_user_credentials(role_prefix: str, cfg: config):  
    """Получает учетные данные пользователя из переменных окружения."""
    user_id = getattr(cfg, f'{role_prefix.upper()}_ID', None)
    login = getattr(cfg, f'{role_prefix.upper()}_LOGIN', None)
    password = getattr(cfg, f'{role_prefix.upper()}_PASS', None)
    email = getattr(cfg, f'{role_prefix.upper()}_EMAIL', None)
    phone = getattr(cfg, f'{role_prefix.upper()}_PHONE', None)

    if not login or not password:
        print(f"Предупреждение: Логин или пароль для {role_prefix} не найдены. Пропускаем.")
        return None

    return {'id': user_id, 'login': login, 'password': password, 'email': email, 'phone': phone}


def load_users_from_csv(csv_path, user_manager):
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Assuming CSV has columns: login, password, role, etc.
            user_manager.add_user(row['login'], row['password'], row['role'], email=row.get('email'), phone=row.get('phone'))


def load_users_from_csv_new(csv_path, user_manager):
    """Загружает пользователей из CSV-файла (новая реализация)."""
    if not os.path.exists(csv_path):
        print(f"Файл {csv_path} не найден.")
        return

    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # CSV формат: username,password,role,subscription
                username = row.get('username', None)
                password = row.get('password', None)
                role = row.get('role', 'user')
                subscription = row.get('subscription', None)
                
                # Добавляем пользователя с данными из CSV
                if username and password:
                    user_manager.add_user(username, password, role)
                    print(f"Пользователь {username} добавлен.")
                else:
                    print(f"Пропущена строка из CSV: отсутствуют обязательные поля username или password")
    except Exception as e:
        print(f"Ошибка при загрузке пользователей из CSV: {e}")


def main():
    """Основная функция для инициализации пользователей."""
    print("--- Скрипт init_users.py запущен ---")
    print("Создаем экземпляр UserManager...")
    try:
        user_manager = UserManager()
        print("Экземпляр UserManager успешно создан.")
    except Exception as e:
        print(f"Критическая ошибка при создании UserManager: {e}")
        return

    # Импорт пользователей из bulk CSV через общий метод UserManager
    if config.BULK_CSV_PATH.exists():
        result = user_manager.authorize_users_from_csv(str(config.BULK_CSV_PATH))
        print(f"Импортировано пользователей из {config.BULK_CSV_PATH}: {len(result.get('success', {}))} успешных, {len(result.get('failed', []))} ошибок")
    else:
        print(f"CSV-файл {config.BULK_CSV_PATH} не найден, импорт пропущен.")

    users_to_create = {
        'admin': 'ADMIN',
        'moderator': 'MODERATOR',
        'expert': 'EXPERT'
    }

    for role, role_prefix in users_to_create.items():
        print(f"Обрабатываем пользователя: {role}")
        creds = get_user_credentials(role_prefix, config)

        if creds:
            # Проверяем, существует ли пользователь, перед добавлением
            if not user_manager.get_user(creds['login']):
                print(f"Добавляем нового пользователя: {creds['login']}")
                user_manager.add_user(
                    login=creds['login'],
                    password=creds['password'],
                    role=role.lower().replace('_user', ''),
                    email=creds['email'],
                    phone=creds['phone'],
                    is_active=True,
                    last_password_change=datetime.now(timezone.utc).isoformat(),
                    user_id=creds['id']
                )
            else:
                print(f"Пользователь '{creds['login']}' уже существует. Пропускаем.")

    print("\n--- Инициализация пользователей завершена успешно ---")


if __name__ == "__main__":
    print(f"Debug: Loaded ENV ADMIN_LOGIN: {os.getenv('ADMIN_LOGIN')}")
    main()
