"""
Модуль запуска авторизации и работы с куками через CLI.

Обеспечивает интерфейс командной строки для авторизации,
сохранения и проверки кук.
"""

import os
from pathlib import Path
import argparse

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from src.config import config
from src.logger import setup_logger
from src.cookies import load_cookies


class AuthManager:
    """
    Класс для управления авторизацией и куками браузера.
    """

    def __init__(
        self,
        headless: bool = True,
        cookies_path: Path = config.COOKIES_PATH,
        login_url: str = config.LOGIN_URL,
        target_url: str = config.TARGET_URL,
    ):
        """
        Инициализирует менеджер авторизации.

        Args:
            headless: Запускать ли браузер в безголовом режиме
            cookies_path: Путь к файлу с куками
            login_url: URL страницы авторизации
            target_url: Целевой URL, на который редиректит после авторизации
        """
        self.logger = setup_logger(__name__)
        self.headless = headless
        self.cookies_path = cookies_path
        self.login_url = login_url
        self.target_url = target_url

    def load_credentials(self) -> None:
        """
        Загружает учетные данные из файла .env.

        Raises:
            RuntimeError: Если файл с учетными данными не найден или данные неполные
        """
        self.logger.debug(
            f"Проверка наличия файла "
            f"{config.CREDS_PATH}"
        )
        if not config.CREDS_PATH.exists():
            raise RuntimeError(f"Файл {config.CREDS_PATH} не найден!")

        self.logger.debug(
            f"Загрузка учетных данных из "
            f"{config.CREDS_PATH}"
        )
        load_dotenv(dotenv_path=config.CREDS_PATH, override=True)

        login = os.getenv("LOGIN")
        password = os.getenv("PASS")

        if not login or not password:
            raise RuntimeError(
                f"LOGIN и/или PASS не заданы в {config.CREDS_PATH}"
            )

        self.logger.info(f"Загружены учетные данные для пользователя {login}")

    def perform_authorization(self) -> None:
        """
        Выполняет авторизацию и сохраняет куки.
        """
        self.logger.info("Запуск авторизации...")

        # Загружаем учетные данные
        self.load_credentials()

        # Выполняем авторизацию через наш метод
        self.authorize_and_save_cookies()

        self.logger.info(
            f"Куки сохранены в {self.cookies_path}"
        )

    def open_browser_with_cookies(self) -> None:
        """
        Открывает браузер с сохранёнными куками.

        Raises:
            RuntimeError: Если сохранённые куки не найдены
        """
        self.logger.info("Открытие браузера с сохранёнными куками...")

        cookies = load_cookies(self.cookies_path)
        if not cookies:
            raise RuntimeError(
                f"Нет сохранённых кук в {self.cookies_path}. "
                "Сначала выполните авторизацию."
            )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            context.add_cookies(cookies)

            self.logger.info(f"Переход на {self.target_url}")
            page.goto(self.target_url)

            input("Нажмите Enter для закрытия браузера...")

    def validate_cookies(self) -> bool:
        """
        Проверяет наличие и валидность сохранённых куков.

        Returns:
            bool: True, если куки существуют и валидны, иначе False
        """
        self.logger.info("Проверка сохранённых куков...")

        cookies = load_cookies(self.cookies_path)
        if not cookies:
            self.logger.warning(f"Куки не найдены в {self.cookies_path}")
            return False

        self.logger.info(f"Найдено {len(cookies)} кук")
        # TODO: Добавить дополнительную проверку валидности куков, если необходимо

        return True


def parse_args():
    """
    Разбирает аргументы командной строки.

    Returns:
        argparse.Namespace: Аргументы командной строки
    """
    parser = argparse.ArgumentParser(
        description="Управление авторизацией и куками"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--auth", 
        action="store_true", 
        help="Авторизоваться и сохранить куки"
    )
    group.add_argument(
        "--check", 
        action="store_true", 
        help="Проверить существующие куки"
    )

    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Запуск в режиме отладки (без headless)"
    )
    parser.add_argument(
        "--username", 
        help="Имя пользователя для аутентификации"
    )

    return parser.parse_args()


def main():
    """
    Основная функция приложения.

    Returns:
        int: Код возврата (0 - успех, 1 - ошибка)
    """
    args = parse_args()
    auth_manager = AuthManager(headless=not args.debug)

    try:
        # Если указано имя пользователя и оно отличается от конфигурации
        if (args.username and hasattr(config, 'LOGIN') and 
                args.username != config.LOGIN):
            print(
                f"Используем указанное имя пользователя: {args.username}"
            )
            # TODO: Добавить получение пароля из кредов

        if args.auth:
            if auth_manager.authorize_and_save_cookies():
                print(
                    "Авторизация и сохранение кук выполнены успешно"
                )
                return 0
            print("Ошибка авторизации или сохранения кук")
            return 1
        elif args.check:
            if auth_manager.validate_cookies():
                print(
                    "Куки валидны и могут быть использованы "
                    "для авторизации"
                )
                return 0
            print(
                "Куки невалидны или отсутствуют. "
                "Необходима новая авторизация"
            )
            return 1
    except Exception as e:
        print(f"Ошибка выполнения: {e}")
        return 1


if __name__ == "__main__":
    main()
