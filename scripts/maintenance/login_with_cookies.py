#!/usr/bin/env python3
"""login_with_cookies.py

Утилита демонстрирует полный цикл «БД → куки → браузер».

Что делает:
1. Берёт пользователя либо по роли (например ``expert``), либо по логину.
2. Проверяет, что для пользователя сохранены куки (``UserManager.get_cookie_path``).
3. Загружает куки и добавляет их в контекст Playwright.
4. Открывает указанный URL (``--url``). Поддерживаются любые поддомены ``*.bll.by``.
5. Проверяет, что профиль отобразился: ищет элемент
   ``a.top-nav__item.top-nav__profile#myProfile_id`` и сверяет ``title`` с логином.
6. Выводит результат в консоль (SUCCESS/ERROR).

Usage::

    # Авторизация эксперта на https://expert.bll.by (headless)
    python login_with_cookies.py --role expert --url https://expert.bll.by/

    # Авторизация конкретного пользователя в GUI-режиме
    python login_with_cookies.py --user admin --url https://bll.by/ --headed

Примечания:
* Для первого запуска пользователь должен иметь сохранённые куки в БД/файле.
* Скрипт не выполняет авторизацию через UI — он использует уже сохранённые куки.
* Куки в БД хранятся с доменом ``.bll.by`` поэтому подходят для всех поддоменов.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from playwright.sync_api import sync_playwright, Browser, BrowserContext

# Добавляем корень проекта для абсолютных импортов
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from projects.auth_management.user_manager import UserManager  # noqa: E402
from framework.utils.auth_utils import load_cookie  # noqa: E402

# ---------------------------------------------------------------------------
# Константы
# ---------------------------------------------------------------------------
PROFILE_ANCHOR_SELECTOR: str = (
    "a.top-nav__item.top-nav__profile#myProfile_id"
)


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Авторизация пользователя через сохранённые куки и открытие URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--role",
        help="Роль пользователя (например: expert, admin)",
    )
    group.add_argument(
        "--user",
        help="Логин пользователя (например: john_doe)",
    )

    parser.add_argument(
        "--url",
        required=True,
        help="URL, который нужно открыть (должен быть поддоменом bll.by)",
    )

    parser.add_argument(
        "--headed",
        action="store_true",
        help="Открыть браузер в GUI-режиме (по умолчанию headless)",
    )

    return parser.parse_args()


def _load_cookies_from_file(cookie_path: Path) -> List[dict]:
    """Загружает cookies из файла JSON."""
    with cookie_path.open(encoding="utf-8") as fp:
        return json.load(fp)


# ---------------------------------------------------------------------------
# Основная логика
# ---------------------------------------------------------------------------

def main() -> None:
    args = _parse_args()

    user_manager = UserManager()

    # 1. Получаем пользователя
    if args.user:
        user = user_manager.get_user(login=args.user)
        if not user:
            print(f"❌ Пользователь '{args.user}' не найден в БД")
            sys.exit(1)
    else:
        user = user_manager.get_user_by_role(args.role)
        if not user:
            # Фолбэк: ищем в основной БД фреймворка, куда массовая авторизация пишет данные
            try:
                from framework.db_utils.database_manager import DatabaseManager  # noqa: E402
                db_fm = DatabaseManager()
                users_by_role = db_fm.get_users_by_role(args.role)
                if users_by_role:
                    user_dict = users_by_role[0]
                    user = {
                        "login": user_dict["login"],
                        "username": user_dict["login"],
                    }
                    # Пусть cookie_path берётся из записанного cookie_file столбца
                    if user_dict.get("cookie_file"):
                        user["cookie_path"] = Path(user_dict["cookie_file"])
                else:
                    user = None
            except Exception:
                user = None
        if not user:
            print(f"❌ Пользователь с ролью '{args.role}' не найден")
            sys.exit(1)

    login = user.get("login") or user.get("username") or str(user.get("id"))
    # Определяем путь к файлу куки. Если запись пришла из фреймворк-БД, там уже указан cookie_file
    if user.get("cookie_path"):
        cookie_path = Path(user["cookie_path"])
    else:
        cookie_path = user_manager.get_cookie_path(login)

    if not cookie_path.exists():
        print(f"❌ Cookie-файл не найден: {cookie_path}\n" "Сначала выполните авторизацию и сохранение куков.")
        sys.exit(1)

    print("========================================")
    print("  Авторизация через куки")
    print("========================================")
    print(f"👤 Пользователь : {login}")
    print(f"📂 Cookie файл : {cookie_path}")
    print(f"🌍 URL         : {args.url}")
    print(f"🖥️  Headless   : {'нет (GUI)' if args.headed else 'да'}")
    print("========================================\n")

    # 2. Запуск браузера
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch(headless=not args.headed)
        context: BrowserContext = browser.new_context()

        # 3. Подставляем куки (универсальные .bll.by)
        cookies = _load_cookies_from_file(cookie_path)
        context.add_cookies(cookies)
        page = context.new_page()

        # 4. Переходим на URL
        print("🌐 Переходим на страницу...")
        page.goto(args.url, timeout=30000)

        try:
            # 5. Проверяем наличие профиля
            print("🔍 Проверяем наличие профиля...")
            page.wait_for_selector(PROFILE_ANCHOR_SELECTOR, timeout=10000)
            anchor = page.query_selector(PROFILE_ANCHOR_SELECTOR)
            title_attr = anchor.get_attribute("title") if anchor else None

            if title_attr and login.lower() in title_attr.lower():
                print(f"✅ Авторизация подтверждена! Пользователь: {title_attr}")
            else:
                print("⚠️  Элемент найден, но title не совпадает. Возможна проблема авторизации.")
        except Exception:
            print("❌ Не удалось найти элемент профиля. Авторизация неуспешна.")
            browser.close()
            sys.exit(1)

        print("\n🎉 Сессия активна. Можно продолжать работу.")
        if args.headed:
            print("Нажмите CTRL+C в консоли для завершения.")
            try:
                while True:
                    page.wait_for_timeout(1000)
            except KeyboardInterrupt:
                print("\nЗавершение по CTRL+C...")
        browser.close()


if __name__ == "__main__":
    main() 