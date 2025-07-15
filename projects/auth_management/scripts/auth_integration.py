#!/usr/bin/env python
"""
Интеграция аутентификации для E2E-тестов.

Перемещено в `scripts/` для единообразия.
"""
import os
import sys
import json
from typing import Optional

# Добавляем корень проекта в PYTHONPATH, чтобы работали абсолютные импорты
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from playwright.sync_api import BrowserContext  # type: ignore
from projects.auth_management.user_manager import UserManager  # noqa: E402
from projects.auth_management.logger import logger  # noqa: E402


class AuthIntegration:
    """Класс-помощник для авторизации в Playwright-контексте."""

    def __init__(self, env_path: Optional[str] = None):
        """Создает интеграцию.

        Args:
            env_path: путь к .env (по умолчанию `data/creds.env`).
        """
        from projects.auth_management.config import config  # noqa: E402, импорт после PYTHONPATH

        # config уже загружен; просто проверяем путь для отладочных целей
        if env_path and os.path.exists(env_path):
            logger.info("Используется конфигурация из %s", env_path)
        self.user_manager = UserManager()

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------

    def setup_authenticated_context(self, context: BrowserContext, login: str) -> BrowserContext:
        """Применяет сохранённые куки пользователя к контексту.

        Args:
            context: экземпляр BrowserContext
            login: логин пользователя
        Returns:
            Тот же контекст с добавленными куками.
        """
        user = self.user_manager.get_user(login=login)
        if not user or not user.get("cookie"):
            raise ValueError(f"Пользователь {login} не найден или нет кук в БД")

        cookies_json = user["cookie"]
        cookies = json.loads(cookies_json)
        context.add_cookies(cookies)
        logger.debug("Куки для %s добавлены в контекст", login)
        return context

    def save_auth_state(self, context: BrowserContext, login: str) -> None:
        """Сохраняет текущее состояние (куки) в `user_data/{login}_auth.json`."""
        cookies = context.cookies()
        os.makedirs("user_data", exist_ok=True)
        path = os.path.join("user_data", f"{login}_auth.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(cookies, fh, ensure_ascii=False, indent=2)
        logger.info("Сохранено auth-состояние для %s → %s", login, path)

    def load_auth_state(self, context: BrowserContext, login: str) -> bool:
        """Пробует загрузить сохранённое auth-состояние.

        Returns:
            True, если куки загружены, иначе False.
        """
        path = os.path.join("user_data", f"{login}_auth.json")
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as fh:
            cookies = json.load(fh)
        context.add_cookies(cookies)
        logger.info("Загружено auth-состояние из %s", path)
        return True
