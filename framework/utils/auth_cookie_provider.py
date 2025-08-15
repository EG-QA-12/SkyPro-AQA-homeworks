import json
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import re

from .cookie_constants import COOKIE_NAME

logger = logging.getLogger(__name__)


class AuthCookieProvider:
    """Провайдер авторизационной куки `test_joint_session`.

    Источники получения куки (в порядке приоритета):
    1) Переменные окружения: `SESSION_COOKIE_{ROLE}` или `SESSION_COOKIE`
    2) Локальные файлы: `cookies/{role}_session.txt` или `cookies/{role}_cookies.json`
       (в JSON берётся запись с именем `test_joint_session`)
    3) API-логин (если заданы `API_USERNAME` и `API_PASSWORD`) через `APIAuthManager`

    Такой порядок соответствует принципам Управления Окружением и Изоляции: сначала
    используем явные конфиги, затем артефакты прошлых запусков, и только в крайнем случае
    выполняем сетевой логин.

    Все пути и операции имеют минимальные побочные эффекты и снабжены логированием.
    """
    _config: Optional[Dict[str, Any]] = None

    def _load_config(self) -> Dict[str, Any]:
        """Загружает и кэширует конфигурацию авторизации из JSON-файла."""
        if self._config is not None:
            return self._config

        project_root = Path(__file__).resolve().parents[2]
        config_path = project_root / "config" / "auth_config.json"
        if not config_path.exists():
            logger.error(f"Файл конфигурации не найден: {config_path}")
            self._config = {}
            return self._config
        
        try:
            raw_content = config_path.read_text('utf-8')
            self._config = json.loads(raw_content)
            logger.info(f"Конфигурация авторизации успешно загружена из {config_path}")
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Ошибка чтения или парсинга auth_config.json: {e}")
            self._config = {}
        
        return self._config


    def get_auth_cookie(self, role: str = "admin") -> Optional[str]:
        """Возвращает значение куки `test_joint_session` для указанной роли.

        Args:
            role: Роль пользователя (например, "admin").

        Returns:
            Строка со значением куки или ``None``, если получить не удалось.
        """
        # 1) ENV: SESSION_COOKIE_{ROLE} или SESSION_COOKIE
        env_cookie = self._get_cookie_from_env(role)
        if env_cookie:
            logger.debug("Используется кука из ENV")
            return env_cookie

        # 2) Файлы: cookies/{role}_session.txt или cookies/{role}_cookies.json
        file_cookie = self._get_cookie_from_files(role)
        if file_cookie:
            logger.debug("Используется кука из локального файла")
            return file_cookie

        # 3) API-логин (если заданы креды в ENV или конфиге)
        api_cookie = self._get_cookie_via_api_login(role)
        if api_cookie:
            logger.info(f"Кука для роли '{role}' получена через API-логин")
            return api_cookie

        logger.error(f"Не удалось получить авторизационную куку для роли '{role}' ни одним из способов")
        return None

    # ------------------------ Вспомогательные методы ------------------------ #

    def _get_cookie_from_env(self, role: str) -> Optional[str]:
        """Пытается прочитать куку из переменных окружения.

        Ищутся переменные: `SESSION_COOKIE_{ROLE_UPPER}` затем `SESSION_COOKIE`.
        """
        role_key = role.upper().replace("-", "_")
        candidates: List[str] = [f"SESSION_COOKIE_{role_key}", "SESSION_COOKIE"]
        for key in candidates:
            value = os.getenv(key)
            if value:
                return value.strip()
        return None

    def _get_cookie_from_files(self, role: str) -> Optional[str]:
        """Пытается прочитать куку из артефактов прошлых запусков.

        Поддерживаются два формата:
        - Простой текст: cookies/{role}_session.txt — содержит только значение куки
        - JSON Playwright: cookies/{role}_cookies.json — список словарей, ищем name==COOKIE_NAME
        """
        project_root: Path = Path(__file__).resolve().parents[2]
        cookies_dir: Path = project_root / "cookies"

        # Текстовый файл
        txt_path: Path = cookies_dir / f"{role}_session.txt"
        if txt_path.exists():
            try:
                return txt_path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                logger.warning("Не удалось прочитать %s: %s", txt_path, exc)

        # JSON-файл Playwright формата
        json_path: Path = cookies_dir / f"{role}_cookies.json"
        if json_path.exists():
            try:
                raw = json_path.read_text(encoding="utf-8")
                data = json.loads(raw)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("name") == COOKIE_NAME:
                            value = item.get("value")
                            if isinstance(value, str) and value:
                                return value
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("Не удалось прочитать %s: %s", json_path, exc)
        return None

    def _get_cookie_via_api_login(self, role: str) -> Optional[str]:
        """Выполняет API-логин для указанной роли.
        
        Ищет учетные данные в следующем порядке:
        1. Переменные окружения (например, API_USERNAME_EXPERT, API_PASSWORD_EXPERT)
        2. Общие переменные окружения (API_USERNAME, API_PASSWORD)
        3. Файл `config/auth_config.json`

        Returns:
            Значение авторизационной куки или ``None`` при неуспехе.
        """
        config = self._load_config()
        role_key = role.upper()

        # Определяем username и password
        username = (
            os.getenv(f"API_USERNAME_{role_key}") or
            os.getenv("API_USERNAME") or
            config.get("users", {}).get(role, {}).get("username")
        )
        password = (
            os.getenv(f"API_PASSWORD_{role_key}") or
            os.getenv("API_PASSWORD") or
            config.get("users", {}).get(role, {}).get("password")
        )

        if not username or not password or "REPLACE_WITH_REAL" in (password or ""):
            logger.warning(f"Учетные данные для роли '{role}' не найдены или являются плейсхолдерами.")
            return None

        # Импортируем здесь, чтобы избежать циклических зависимостей
        try:
            from .api_auth import APIAuthManager
        except ImportError as exc:
            logger.error("Не удалось импортировать APIAuthManager: %s", exc)
            return None

        base_url = config.get("login_url", "https://ca.bll.by")
        manager = APIAuthManager(base_url=base_url)
        
        logger.info(f"Попытка API-логина для роли '{role}' с пользователем '{username}'...")
        result = manager.login_user(username=username, password=password)
        
        if result and result.success and isinstance(result.session_token, str):
            logger.info(f"API-логин для роли '{role}' успешен.")
            return result.session_token
        
        logger.error(f"API-логин для роли '{role}' не удался. Ответ: {getattr(result, 'message', 'N/A')}")
        return None


# ------------------------- Совместимые обёртки API ------------------------- #

def get_session_cookie(role: str = "admin") -> Optional[str]:
    """Возвращает строковое значение `test_joint_session` для указанной роли.

    Предназначено для HTTP-запросов через requests.
    Источники: ENV → cookies/*.txt|*.json → API-логин (если доступны креды).
    """
    return AuthCookieProvider().get_auth_cookie(role)


def get_auth_cookies(role: str = "admin", *, domain: str = ".bll.by") -> list[dict]:
    """Возвращает cookies в формате Playwright для указанной роли.

    Формат: список словарей, содержащих как минимум `name`, `value`, `domain`, `path`.
    Используется интеграционными тестами и скриптами, полагающимися на старый интерфейс.
    """
    value = get_session_cookie(role)
    if not value:
        return []
    return [{
        "name": COOKIE_NAME,
        "value": value,
        "domain": domain,
        "path": "/",
    }]
