# test_utils.py

import logging
import os
import random
import string
from typing import Tuple, List, Dict
from playwright.sync_api import Page, ConsoleMessage, Dialog, Error


class Config:
    BaseUrl = "https://bll.by"
    BonusUrl = "https://bonus.bll.by/bonus"
    creds_path = "creds.txt"
    valid_status_codes = set(range(200, 300)) | {301, 302, 304, 307, 308}


def setup_logging():
    """Настройка системы логирования"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("errors.log", mode='w', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def generate_random_text(length: int = 6) -> str:
    """Генерирует случайный текст заданной длины"""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))


class RequestHandler:
    def __init__(self):
        self.failed_requests: List[Tuple[str, int, str]] = []
        self.failed_images: List[Tuple[str, int, str]] = []
        self.all_requests: List[Tuple[str, int, str]] = []
        self.current_step: str = ""
        self.js_errors: List[Dict] = []
        self.console_messages: List[str] = []

    def setup_js_monitoring(self, page: Page):
        """Настройка отслеживания JS ошибок и консольных сообщений"""
        page.on("pageerror", lambda err: self.handle_js_error(err))
        page.on("console", lambda msg: self.handle_console_message(msg))

    def handle_js_error(self, error: Error):
        """Обработка JS ошибок"""
        error_info = {
            'message': str(error),
            'step': self.current_step,
            'timestamp': logging.Formatter.formatTime(logging.LogRecord('', 0, '', 0, None, None, None))
        }
        self.js_errors.append(error_info)
        logging.error(f"JavaScript error on step '{self.current_step}': {error}")

    def handle_console_message(self, message: ConsoleMessage):
        """Обработка консольных сообщений"""
        if message.type == "error":
            msg = f"Console error: {message.text} (at {self.current_step})"
            self.console_messages.append(msg)
            logging.error(msg)

    def set_current_step(self, step: str) -> None:
        """Устанавливает текущий шаг теста"""
        self.current_step = step
        logging.info(f"Выполняется шаг: {step}")

    def handle_response(self, response) -> None:
        """Обработчик ответов от сервера"""
        status = response.status
        url = response.url
        method = response.request.method
        content_type = response.headers.get("content-type", "").lower()

        self.all_requests.append((url, status, method))

        if status not in Config.valid_status_codes:
            is_image = (
                    url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico')) or
                    'image' in content_type
            )

            if is_image:
                self.failed_images.append((url, status, method))
            else:
                self.failed_requests.append((url, status, method))

            message = f"Запрос {method} к {url} вернул статус {status} на шаге: {self.current_step}"
            message += " (изображение)" if is_image else ""
            logging.warning(message)

    def get_requests_summary(self) -> str:
        """Возвращает расширенную статистику по запросам и ошибкам"""
        summary = ["\nПодробный отчет о выполнении теста:"]

        # Статистика по статусам
        status_stats = {}
        method_stats = {}

        for url, status, method in self.all_requests:
            status_stats[status] = status_stats.get(status, 0) + 1
            method_stats[method] = method_stats.get(method, 0) + 1

        # Добавляем информацию о неуспешных запросах с детализацией по шагам
        if self.failed_requests:
            summary.append("\n🔴 Критичные ошибки запросов по шагам:")
            current_step = None
            for url, status, method in self.failed_requests:
                if current_step != self.current_step:
                    current_step = self.current_step
                    summary.append(f"\nШаг: {current_step}")
                summary.append(f"  • {method} {url} (статус {status})")

        # Добавляем информацию о неуспешных запросах изображений
        if self.failed_images:
            summary.append("\n🟡 Ошибки загрузки изображений:")
            current_step = None
            for url, status, method in self.failed_images:
                if current_step != self.current_step:
                    current_step = self.current_step
                    summary.append(f"\nШаг: {current_step}")
                summary.append(f"  • {method} {url} (статус {status})")

        # Добавляем информацию о JavaScript ошибках
        if self.js_errors:
            summary.append("\n🔴 JavaScript ошибки:")
            for error in self.js_errors:
                summary.append(f"  • Шаг: {error['step']}")
                summary.append(f"    Ошибка: {error['message']}")
                summary.append(f"    Время: {error['timestamp']}")

        # Добавляем информацию о консольных ошибках
        if self.console_messages:
            summary.append("\n🔴 Консольные ошибки:")
            for msg in self.console_messages:
                summary.append(f"  • {msg}")

        # Общая статистика
        summary.append("\n📊 Общая статистика:")
        summary.append(f"  • Всего запросов: {len(self.all_requests)}")
        summary.append(f"  • Критичных ошибок: {len(self.failed_requests)}")
        summary.append(f"  • Ошибок загрузки изображений: {len(self.failed_images)}")
        summary.append(f"  • JavaScript ошибок: {len(self.js_errors)}")
        summary.append(f"  • Консольных ошибок: {len(self.console_messages)}")

        # Добавляем распределение по статусам
        summary.append("\nРаспределение по статус-кодам:")
        for status, count in sorted(status_stats.items()):
            status_type = "✅" if status in Config.valid_status_codes else "❌"
            summary.append(f"  {status_type} {status}: {count} запросов")

        # Добавляем распределение по методам
        summary.append("\nРаспределение по HTTP-методам:")
        for method, count in sorted(method_stats.items()):
            summary.append(f"  • {method}: {count} запросов")

        return "\n".join(summary)

    def assert_all_responses_successful(self) -> None:
        """Проверяет успешность всех запросов и отсутствие JS ошибок"""
        has_errors = False
        error_message = []

        # Проверяем критичные запросы
        if self.failed_requests:
            has_errors = True
            error_message.append(f"\n❌ Критичные ошибки в запросах на шаге: {self.current_step}")
            error_message.append(f"Последний успешный URL: {self.get_last_successful_url()}")
            for url, status, method in self.failed_requests:
                error_message.append(f"  • {method} {url} - статус {status}")

        # Добавляем информацию об ошибках загрузки изображений
        if self.failed_images:
            error_message.append("\n⚠️ Ошибки загрузки изображений:")
            for url, status, method in self.failed_images:
                error_message.append(f"  • {method} {url} - статус {status}")

        # Проверяем JavaScript ошибки
        if self.js_errors:
            has_errors = True
            error_message.append("\n❌ JavaScript ошибки:")
            for error in self.js_errors:
                error_message.append(f"  • Шаг: {error['step']}")
                error_message.append(f"    Ошибка: {error['message']}")

        if has_errors:
            full_error = "\n".join(error_message)
            logging.error(full_error)
            raise AssertionError(full_error)

    def get_last_successful_url(self) -> str:
        """Возвращает последний успешный URL перед ошибкой"""
        for url, status, method in reversed(self.all_requests):
            if status in Config.valid_status_codes:
                return url
        return ""


class Auth:
    @staticmethod
    def get_credentials() -> Tuple[str, str]:
        """
        Получает первую пару учетных данных из файла creds.txt в формате login;password
        Returns:
            Tuple[str, str]: пара (логин, пароль)
        """
        try:
            if not os.path.exists(Config.creds_path):
                raise FileNotFoundError(f"Файл с учетными данными не найден: {Config.creds_path}")

            with open(Config.creds_path, "r", encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # Пропускаем пустые строки и комментарии
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Проверяем формат строки
                    if ';' not in line:
                        logging.warning(f"Пропущена строка {line_num}: неверный формат (нет разделителя ';')")
                        continue

                    parts = line.split(';')
                    if len(parts) != 2:
                        logging.warning(
                            f"Пропущена строка {line_num}: неверное количество частей (ожидается 2, получено {len(parts)})")
                        continue

                    login, password = parts
                    login = login.strip()
                    password = password.strip()

                    # Проверяем, что логин и пароль не пустые
                    if not login or not password:
                        logging.warning(f"Пропущена строка {line_num}: пустой логин или пароль")
                        continue

                    logging.info(f"Успешно загружены учетные данные")
                    return login, password

                raise ValueError(
                    "Не найдено валидных учетных данных в файле. "
                    "Формат должен быть: login;password"
                )

        except Exception as e:
            logging.error(f"Ошибка при чтении учетных данных: {e}")
            raise

    @staticmethod
    def login(page: Page, username: str, password: str) -> None:
        """Выполняет авторизацию пользователя"""
        try:
            page.goto(Config.BaseUrl)
            page.get_by_role("link", name="Войти").click()
            page.get_by_label("Логин").fill(username)
            page.get_by_label("Пароль").fill(password)
            page.get_by_role("button", name="Войти").click()
        except Exception as e:
            logging.error(f"Ошибка при авторизации: {e}")
            ScreenshotManager.take_screenshot(page, "auth_error")
            raise




class ScreenshotManager:
    @staticmethod
    def take_screenshot(page: Page, name: str) -> None:
        """Создает скриншот страницы"""
        try:
            filename = f"screenshots/{name}_{generate_random_text()}.png"
            page.screenshot(path=filename)
            logging.info(f"Создан скриншот: {filename}")
        except Exception as e:
            logging.error(f"Ошибка при создании скриншота: {e}")


class FolderUtils:
    @staticmethod
    def create_and_delete_folder(page: Page) -> None:
        """Создает и удаляет тестовую папку"""
        try:
            folder_name = FolderUtils.generate_unique_folder_name(page)
            FolderUtils._create_folder(page, folder_name)
            FolderUtils._verify_folder_creation(page, folder_name)
            FolderUtils._delete_folder(page, folder_name)
        except Exception as e:
            logging.error(f"Ошибка при работе с папкой: {e}")
            ScreenshotManager.take_screenshot(page, "folder_error")
            raise

    @staticmethod
    def generate_unique_folder_name(page: Page, base_name="Новая папка") -> str:
        """Генерирует уникальное имя папки"""
        folder_number = 1
        while page.locator(f"a.jstree-anchor:text('{base_name} {folder_number}')").count() > 0:
            folder_number += 1
        return f"{base_name} {folder_number}"

    @staticmethod
    def _create_folder(page: Page, folder_name: str) -> None:
        """Создает новую папку"""
        try:
            page.get_by_role("button", name="Новая папка").click()
            page.get_by_label("Избранное").get_by_role("textbox").fill(folder_name)
            page.get_by_role("button", name="Готово").click()
            page.wait_for_timeout(1000)  # Ждем обновления DOM
            ScreenshotManager.take_screenshot(page, f"folder_creation_{folder_name}")
            logging.info(f"Попытка создания папки: {folder_name}")
        except Exception as e:
            logging.error(f"Ошибка при создании папки {folder_name}: {e}")
            raise

    @staticmethod
    def _verify_folder_creation(page: Page, folder_name: str) -> None:
        """Проверяет успешность создания папки"""
        try:
            folder = page.locator(f"a.jstree-anchor:text('{folder_name}')")
            if not folder.is_visible(timeout=2000):
                raise Exception(f"Папка {folder_name} не была создана")
            logging.info(f"Папка {folder_name} успешно создана")
        except Exception as e:
            logging.error(f"Ошибка при проверке создания папки {folder_name}: {e}")
            raise

    @staticmethod
    def _delete_folder(page: Page, folder_name: str) -> None:
        """Удаляет папку"""
        try:
            folder = page.locator(f"a.jstree-anchor:text('{folder_name}')")
            folder.click()
            page.get_by_role("img", name="Удалить папку").click()
            page.once("dialog", lambda dialog: dialog.accept())
            page.wait_for_timeout(1000)  # Ждем обновления DOM
            ScreenshotManager.take_screenshot(page, f"folder_deletion_{folder_name}")
            logging.info(f"Папка {folder_name} удалена")
        except Exception as e:
            logging.error(f"Ошибка при удалении папки {folder_name}: {e}")
            raise

    @staticmethod
    def rename_folder(page: Page, old_name: str, new_name: str) -> None:
        """Переименовывает папку"""
        try:
            folder = page.locator(f"a.jstree-anchor:text('{old_name}')")
            folder.click()
            page.get_by_role("img", name="Переименовать папку").click()
            page.get_by_label("Избранное").get_by_role("textbox").fill(new_name)
            page.get_by_role("button", name="Готово").click()
            page.wait_for_timeout(1000)  # Ждем обновления DOM
            logging.info(f"Папка {old_name} переименована в {new_name}")

            # Проверяем успешность переименования
            new_folder = page.locator(f"a.jstree-anchor:text('{new_name}')")
            if not new_folder.is_visible(timeout=2000):
                raise Exception(f"Папка не была переименована в {new_name}")

        except Exception as e:
            logging.error(f"Ошибка при переименовании папки {old_name}: {e}")
            ScreenshotManager.take_screenshot(page, "rename_folder_error")
            raise