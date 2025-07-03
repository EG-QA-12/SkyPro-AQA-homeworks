"""
Вспомогательные функции для обновления информации о пользователях в базе данных.

Этот модуль предназначен для централизованного обновления или добавления пользователей после успешной авторизации в UI- и bulk-тестах.

Пример использования:
    from framework.utils.db_helpers import update_user_in_db
    update_user_in_db(login, role, subscription, cookie_file)
"""
from framework.db_utils.database_manager import DatabaseManager
from datetime import datetime
from typing import Optional

def update_user_in_db(
    login: str,
    role: str,
    subscription: str,
    cookie_file: str,
    last_cookie_update: Optional[datetime] = None
) -> None:
    """
    Обновляет или добавляет пользователя в БД с актуальной информацией.

    Args:
        login: Логин пользователя
        role: Роль пользователя (например, 'admin', 'moderator', 'user', 'expert')
        subscription: Подписка пользователя (например, 'basic', 'premium')
        cookie_file: Путь к файлу куки
        last_cookie_update: Время обновления куки (по умолчанию — текущее)
    """
    if last_cookie_update is None:
        last_cookie_update = datetime.now()
    with DatabaseManager() as db:
        db.add_or_update_user(
            login=login,
            role=role,
            subscription=subscription,
            cookie_file=cookie_file,
            last_cookie_update=last_cookie_update
        ) 