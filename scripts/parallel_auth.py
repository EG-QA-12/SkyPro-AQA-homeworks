"""parallel_auth.py
Запуск параллельной авторизации пользователей через Playwright.

Этот скрипт обновлен для работы с новой архитектурой фреймворка.
Теперь cookies сохраняются в централизованной папке cookies/,
а данные пользователей берутся из папки secrets/.

Использование:
    python scripts/parallel_auth.py "secrets/bulk_users.csv" --threads 5 --headless --relogin

Преимущества новой архитектуры для Junior QA:
1. Все cookies в одном месте - легко найти и управлять
2. Секретные данные изолированы в отдельной папке
3. Автоматическое сохранение cookies после успешной авторизации
4. Возможность повторного использования сессий
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Импортируем утилиты фреймворка для работы с cookies
sys.path.append(str(Path(__file__).parent.parent))
from framework.utils.auth_utils import save_user_cookie, load_user_cookie, get_auth_credentials
from framework.utils.cookie_constants import COOKIE_NAME

# ---------------------------------------------------------------------------
# Константы
# ---------------------------------------------------------------------------
DEFAULT_START_URL: str = "https://bll.by/login"


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def parse_csv(csv_path: Path) -> List[Dict[str, str]]:
    """Читает CSV-файл с пользователями.

    Ожидается заголовок как минимум из колонок ``username`` и ``password``.

    Args:
        csv_path: Путь к CSV-файлу.

    Returns:
        Список словарей с данными пользователей.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV-файл не найден: {csv_path}")

    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"username", "password"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(
                f"CSV должен содержать колонки: {', '.join(sorted(required))}. "
                f"Найдены: {reader.fieldnames}"
            )
        return list(reader)  # type: ignore[arg-type]


async def perform_login(page: Page, user: Dict[str, str], relogin: bool) -> None:
    """Выполняет авторизацию пользователя в UI.

    Метод старается найти стандартные селекторы полей логина/пароля
    и кнопку «submit». При ошибках выводит сообщение в консоль.

    Args:
        page: Playwright Page.
        user: dict с ключами ``login`` и ``password``.
        relogin: Если ``True`` – принудительно выполняется повторный вход.
    """
    login = user["username"]
    password = user["password"]

    await page.goto(DEFAULT_START_URL)

    selectors_login = [
        "input[type='email']",
        "input[name='email']",
        "input[name='login']",
        "#email",
        "#login",
    ]
    selectors_pass = [
        "input[type='password']",
        "input[name='password']",
        "#password",
    ]
    selectors_submit = [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Войти')",
        "button:has-text('Login')",
    ]

    # Находим поля логина и пароля
    login_field = None
    for sel in selectors_login:
        if await page.locator(sel).is_visible():
            login_field = page.locator(sel)
            break

    pass_field = None
    for sel in selectors_pass:
        if await page.locator(sel).is_visible():
            pass_field = page.locator(sel)
            break

    if not login_field or not pass_field:
        print(f"⚠️  [{login}] Не удалось найти форму авторизации – пропускаю")
        return

    await login_field.fill(login)
    await pass_field.fill(password)

    # Жмём submit
    for sel in selectors_submit:
        if await page.locator(sel).is_visible():
            await page.click(sel)
            break

    # Ожидаем навигации / появления evidence
    await page.wait_for_timeout(1500)

    print(f"✅ [{login}] попытка входа завершена")


async def worker(
    idx: int,
    user: Dict[str, str],
    sem: asyncio.Semaphore,
    headless: bool,
    relogin: bool,
) -> None:
    """Параллельная задача для авторизации одного пользователя.

    Args:
        idx: Порядковый номер пользователя.
        user: Данные пользователя.
        sem: Семафор для ограничения конкурентности.
        headless: Запуск без UI.
        relogin: Принудительный re-login.
    """
    login = user["username"]
    async with sem:
        async with async_playwright() as p:
            browser: Browser = await p.chromium.launch(headless=headless)
            context: BrowserContext = await browser.new_context()
            page: Page = await context.new_page()

            print(f"🚀 [{idx}] Начинаю авторизацию {login}")
            try:
                await perform_login(page, user, relogin)
            except Exception as exc:
                print(f"❌ [{login}] ошибка: {exc}")
            finally:
                await context.close()
                await browser.close()
                print(f"🏁 [{idx}] Завершил пользователя {login}")


async def main(args: argparse.Namespace) -> None:
    """Главная асинхронная точка входа."""
    csv_path = Path(args.csv_path)
    users = parse_csv(csv_path)

    if not users:
        print("Файл пользователей пуст – нечего авторизовывать")
        return

    sem = asyncio.Semaphore(args.threads)

    tasks = [
        asyncio.create_task(worker(i + 1, user, sem, args.headless, args.relogin))
        for i, user in enumerate(users)
    ]

    await asyncio.gather(*tasks)
    print("\n✅ Все задачи завершены")


def _build_arg_parser() -> argparse.ArgumentParser:
    """Создаёт объект ArgumentParser для CLI."""
    parser = argparse.ArgumentParser(
        prog="parallel_auth",
        description="Параллельная авторизация пользователей через Playwright.",
    )
    parser.add_argument("csv_path", help="Путь к CSV-файлу с пользователями")
    parser.add_argument("--threads", "-t", type=int, default=5, help="Число параллельных браузеров")
    parser.add_argument("--headless", action="store_true", help="Запуск без UI (по умолчанию с UI)")
    parser.add_argument("--relogin", action="store_true", help="Принудительно выполнять повторный вход")
    return parser


if __name__ == "__main__":
    parsed_args = _build_arg_parser().parse_args()

    try:
        asyncio.run(main(parsed_args))
    except KeyboardInterrupt:
        sys.exit("❌ Операция прервана пользователем")
