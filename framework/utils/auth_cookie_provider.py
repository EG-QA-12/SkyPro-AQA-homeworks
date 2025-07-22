"""
Модуль для централизованного получения кук авторизации по роли и подписке.
Использует БД пользователей и cookie-файлы, совместим с Playwright и requests.

Пример использования:
    from framework.utils.auth_cookie_provider import get_auth_cookies
    cookies = get_auth_cookies(role="admin")
"""
from typing import List, Optional, Dict, Any
from pathlib import Path
from framework.utils.db_utils import DatabaseManager
from framework.utils.auth_utils import UnifiedAuthManager
import json


def get_auth_cookies(role: str, subscription: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Получить куки для авторизации пользователя с заданной ролью и подпиской.

    Args:
        role: Роль пользователя (например, 'admin', 'moderator', 'user').
        subscription: Тип подписки (например, 'basic', 'premium').

    Returns:
        Список кук в формате, совместимом с Playwright/requests.

    Raises:
        ValueError: Если не найден подходящий пользователь или файл кук.
    """
    # 1. Получаем пользователя по роли/подписке
    with DatabaseManager() as db:
        users = db.get_users_by_role(role)
        if subscription:
            users = [u for u in users if u.get("subscription") == subscription]
        # Берём первого активного пользователя
        user = next((u for u in users if u.get("is_active") and u.get("cookie_file")), None)
        if not user:
            raise ValueError(f"Не найден активный пользователь с ролью '{role}' и подпиской '{subscription}'")
        cookie_file = user["cookie_file"]

    # 2. Получаем путь к cookie-файлу
    cookie_path = Path(cookie_file)
    if not cookie_path.exists():
        raise ValueError(f"Файл куки не найден: {cookie_path}")

    # 3. Загружаем куки из файла
    with open(cookie_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    if not isinstance(cookies, list) or not cookies:
        raise ValueError(f"Файл куки пуст или некорректен: {cookie_path}")

    # 4. Возвращаем куки (Playwright/requests)
    return cookies 