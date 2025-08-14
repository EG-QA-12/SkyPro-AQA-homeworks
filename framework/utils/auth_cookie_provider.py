import json
import os
import logging
from pathlib import Path
from typing import Optional, List

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

        # 3) API-логин (если заданы креды в ENV)
        api_cookie = self._get_cookie_via_api_login()
        if api_cookie:
            logger.info("Кука получена через API-логин")
            return api_cookie

        logger.error("Не удалось получить авторизационную куку ни одним из способов")
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

    def _get_cookie_via_api_login(self) -> Optional[str]:
        """Выполняет API-логин, если заданы `API_USERNAME` и `API_PASSWORD`.

        Returns:
            Значение авторизационной куки или ``None`` при неуспехе.
        """
        username = os.getenv("API_USERNAME")
        password = os.getenv("API_PASSWORD")
        if not username or not password:
            return None

        # Импортируем здесь, чтобы избежать циклических зависимостей при импорте модулей
        try:
            from .api_auth import APIAuthManager
        except ImportError as exc:
            logger.error("Не удалось импортировать APIAuthManager: %s", exc)
            return None

        manager = APIAuthManager(base_url=os.getenv("API_BASE_URL", "https://ca.bll.by"))
        result = manager.login_user(username=username, password=password)
        if result and result.success and isinstance(result.session_token, str):
            return result.session_token
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
