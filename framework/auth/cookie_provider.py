"""
Провайдер авторизационных кук для системы авторизации.

Обеспечивает получение кук из различных источников в порядке приоритета.
"""

import json
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from .auth_utils import validate_cookie, load_cookie
from framework.utils.cookie_constants import COOKIE_NAME

logger = logging.getLogger(__name__)


class CookieProvider:
    """
    Провайдер авторизационных кук.
    
    Источники получения куки (в порядке приоритета):
    1) Переменные окружения: SESSION_COOKIE_{ROLE} или SESSION_COOKIE
    2) Локальные файлы: cookies/{role}_session.txt или cookies/{role}_cookies.json
    3) API-логин (если доступны учетные данные)
    """

    def __init__(self):
        """Инициализация провайдера кук."""
        self._config: Optional[Dict] = None

    def get_auth_cookie(self, role: str = "admin", 
                       use_api_login: bool = True) -> Optional[str]:
        """
        Возвращает значение куки для указанной роли.
        
        Args:
            role: Роль пользователя
            use_api_login: Флаг разрешения API-логина
            
        Returns:
            Значение куки или None
        """
        # 1. ENV переменные
        env_cookie = self._get_cookie_from_env(role)
        if env_cookie:
            logger.debug(f"Кука для роли '{role}' получена из "
                       "переменных окружения")
            return env_cookie

        # 2. Локальные файлы
        file_cookie = self._get_cookie_from_files(role)
        if file_cookie:
            logger.debug(f"Кука для роли '{role}' получена из "
                       "локального файла")
            return file_cookie

        # 3. API-логин (если разрешено)
        if use_api_login:
            api_cookie = self._get_cookie_via_api_login(role)
            if api_cookie:
                logger.info(f"Кука для роли '{role}' получена "
                          "через API-логин")
                return api_cookie

        logger.warning(f"Не удалось получить куку для роли '{role}'")
        return None

    def _get_cookie_from_env(self, role: str) -> Optional[str]:
        """
        Получает куку из переменных окружения.
        
        Args:
            role: Роль пользователя
            
        Returns:
            Значение куки или None
        """
        role_key = role.upper().replace("-", "_")
        candidates: List[str] = [f"SESSION_COOKIE_{role_key}", "SESSION_COOKIE"]
        
        for key in candidates:
            value = os.getenv(key)
            if value and validate_cookie(value):
                return value.strip()
        
        return None

    def _get_cookie_from_files(self, role: str) -> Optional[str]:
        """
        Получает куку из локальных файлов.
        
        Args:
            role: Роль пользователя
            
        Returns:
            Значение куки или None
        """
        project_root: Path = Path(__file__).resolve().parent.parent.parent
        cookies_dir: Path = project_root / "cookies"

        # Текстовый файл
        txt_path: Path = cookies_dir / f"{role}_session.txt"
        if txt_path.exists():
            try:
                content = load_cookie(str(txt_path))
                if validate_cookie(content):
                    return content
            except Exception as exc:
                logger.warning(f"Не удалось прочитать {txt_path}: {exc}")

        # JSON-файл Playwright формата
        json_path: Path = cookies_dir / f"{role}_cookies.json"
        if json_path.exists():
            try:
                raw_content = json_path.read_text(encoding="utf-8")
                data = json.loads(raw_content)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("name") == COOKIE_NAME:
                            value = item.get("value")
                            if isinstance(value, str) and validate_cookie(value):
                                return value
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning(f"Не удалось прочитать {json_path}: {exc}")
        
        return None

    def _get_cookie_via_api_login(self, role: str) -> Optional[str]:
        """
        Выполняет API-логин для получения куки.
        
        Args:
            role: Роль пользователя
            
        Returns:
            Значение куки или None
        """
        # Эта функция будет реализована в следующих итерациях
        # Пока возвращаем None для обратной совместимости
        logger.debug(f"API-логин для роли '{role}' временно недоступен")
        return None

    def _get_credentials_for_role(self, role: str) -> Tuple[Optional[str], 
                                                          Optional[str]]:
        """
        Получает учетные данные для указанной роли.
        
        Args:
            role: Роль пользователя
            
        Returns:
            Кортеж (username, password) или (None, None)
        """
        # Пока используем старую логику из существующих провайдеров
        # В следующих итерациях будет улучшена
        return None, None


# Обратно совместимые функции
def get_session_cookie(role: str = "admin") -> Optional[str]:
    """
    Обратно совместимая функция для получения куки.
    
    Args:
        role: Роль пользователя
        
    Returns:
        Значение куки или None
    """
    return CookieProvider().get_auth_cookie(role)


def get_auth_cookies(role: str = "admin", *, 
                    domain: str = ".bll.by") -> list[dict]:
    """
    Обратно совместимая функция для получения кук в формате Playwright.
    
    Args:
        role: Роль пользователя
        domain: Домен для кук
        
    Returns:
        Список кук в формате Playwright
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
