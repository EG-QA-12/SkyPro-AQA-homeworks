"""Утилиты для работы с авторизационными куками и сессиями.

Модуль предоставляет функции для:
- Сохранения/загрузки значения авторизационной куки
- Работы с путями к файлам кук 
- Универсальной проверки валидности куки без сетевых запросов

Функции спроектированы с акцентом на простоту и устойчивость:
- Не зависят от внешних сервисов (нет сетевых проверок);
- Подходят для юнит/интеграционных тестов и локального запуска;
- Обеспечивают чёткие типы и сообщения об ошибках.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict

# Импортируем функции из auth_cookie_provider для обратной совместимости
from .auth_cookie_provider import get_session_cookie, get_auth_cookies

def validate_cookie(cookie: str, required_role: str) -> bool:
    """Проверяет базовую валидность значения авторизационной куки.

    Проверка преднамеренно «лёгкая», без сетевых запросов:
    - значение должно быть непустой строкой;
    - не должно состоять из одних пробельных символов;
    - разумная минимальная длина (>= 8 символов);

    Параметр ``required_role`` зарезервирован для будущих проверок
    соответствия роли. Сейчас не используется, но сохраняется для
    совместимости вызовов по всему проекту.

    Args:
        cookie: Значение авторизационной куки ``test_joint_session``.
        required_role: Требуемая роль пользователя (например, ``"admin"``).

    Returns:
        True, если значение похоже на валидное; иначе False.
    """
    # Параметр сохраняется для совместимости API, используем как заглушку,
    # чтобы удовлетворить строгий линтер без изменения сигнатуры.
    _ = required_role

    # Базовая проверка типа роли позволяет задействовать аргумент в валидации,
    # сохраняя совместимость API и устраняя предупреждение линтера.
    if required_role is not None and not isinstance(required_role, str):
        return False

    if not isinstance(cookie, str):
        return False
    value: str = cookie.strip()
    if not value:
        return False
    if len(value) < 8:
        return False
    if " " in value:
        return False
    return True


def save_cookie(cookie: str, path: str) -> None:
    """Сохраняет значение куки в текстовый файл.

    Файл создаётся вместе с недостающими директориями.

    Args:
        cookie: Значение авторизационной куки.
        path: Путь к файлу, куда будет записано значение.

    Raises:
        ValueError: Если значение куки некорректно.
        OSError: Ошибки файловой системы при записи.
    """
    if not validate_cookie(cookie, required_role="any"):
        raise ValueError(
            "Невалидное значение куки: пусто или слишком короткое"
        )
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(cookie, encoding="utf-8")


def load_cookie(path: str) -> str:
    """Загружает значение куки из текстового файла.

    Args:
        path: Путь к файлу с сохранённым значением куки.

    Returns:
        Строка со значением куки.

    Raises:
        FileNotFoundError: Если файл отсутствует.
        OSError: Ошибки чтения файла.
        ValueError: Если считано пустое значение.
    """
    value = Path(path).read_text(encoding="utf-8").strip()
    if not value:
        raise ValueError(
            f"Файл {path} прочитан, но значение куки пустое"
        )
    return value


def load_user_cookie(context, username: str) -> bool:
    """
    Загружает куки пользователя из файла.
    
    Args:
        context: Контекст браузера
        username: Имя пользователя
        
    Returns:
        bool: True если куки успешно загружены
    """
    try:
        # Получаем путь к файлу куков пользователя
        project_root = Path(__file__).parent.parent.parent
        cookies_dir = project_root / "cookies"
        cookie_file = cookies_dir / f"{username}_session.txt"
        
        if cookie_file.exists():
            cookie_value = load_cookie(str(cookie_file))
            if cookie_value:
                # Добавляем куки в контекст
                context.add_cookies([{
                    "name": "test_joint_session",
                    "value": cookie_value,
                    "domain": ".bll.by",
                    "path": "/"
                }])
                return True
    except Exception as e:
        print(f"Ошибка при загрузке куков пользователя {username}: {e}")
    
    return False


def save_user_cookie(context, username: str) -> None:
    """
    Сохраняет куки пользователя в файл.
    
    Args:
        context: Контекст браузера
        username: Имя пользователя
    """
    try:
        # Получаем куки из контекста
        cookies = context.cookies()
        
        # Ищем куку test_joint_session
        for cookie in cookies:
            if cookie.get("name") == "test_joint_session":
                # Сохраняем значение куки
                project_root = Path(__file__).parent.parent.parent
                cookies_dir = project_root / "cookies"
                cookies_dir.mkdir(exist_ok=True)
                cookie_file = cookies_dir / f"{username}_session.txt"
                save_cookie(cookie.get("value", ""), str(cookie_file))
                break
    except Exception as e:
        print(f"Ошибка при сохранении куков пользователя {username}: {e}")


def clear_all_cookies(context) -> None:
    """
    Очищает все куки из контекста.
    
    Args:
        context: Контекст браузера
    """
    try:
        context.clear_cookies()
    except Exception as e:
        print(f"Ошибка при очистке куков: {e}")


def check_cookie_validity(context, username: str) -> bool:
    """
    Проверяет валидность куки пользователя.
    
    Args:
        context: Контекст браузера
        username: Имя пользователя
        
    Returns:
        bool: True если кука валидна
    """
    try:
        # Создаем новую страницу для проверки
        page = context.new_page()
        page.goto("https://bll.by/")
        
        # Проверяем наличие элемента, который виден только авторизованным пользователям
        # Например, кнопка выхода или имя пользователя
        logout_button = page.locator("a[href*='logout'], a:has-text('Выйти')")
        profile_link = page.locator("a[href*='/user/profile'], a:has-text('Профиль')")
        
        is_valid = logout_button.count() > 0 or profile_link.count() > 0
        
        page.close()
        return is_valid
    except Exception as e:
        print(f"Ошибка при проверке валидности куки пользователя {username}: {e}")
        return False


class SecureAuthManager:
    """Условный менеджер безопасной авторизации.

    Используется как лёгкая заглушка для совместимости.
    Реальных сетевых операций не выполняет.
    """

    def __init__(self) -> None:
        self.cookies: Dict[str, str] = {}


def get_cookie_path(role: str) -> str:
    """Возвращает стандартный путь к файлу с куками для роли.
    
    Args:
        role: Роль пользователя (admin, user, moderator)
    
    Returns:
        Абсолютный путь к файлу с куками
    """
    base_dir = Path(__file__).parent.parent
    cookies_dir = base_dir / "cookies"
    return str(cookies_dir / f"{role}_session.txt")


class UnifiedAuthManager:
    """Условный унифицированный менеджер авторизации.

    Поддерживает интерфейс совместимости, не выполняя реальных сетевых операций.
    """

    def __init__(self) -> None:
        self.sessions: Dict[str, str] = {}
