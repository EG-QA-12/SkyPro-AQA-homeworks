#!/usr/bin/env python3
"""
Скрипт авторизации пользователей на базе Playwright (замена Selenium версии).

Основные улучшения:
- Использование Playwright вместо Selenium
- Асинхронная обработка для повышения скорости
- Лучшая стабильность и производительность
- Совместимость с существующим API
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from projects.auth_management.auth_playwright import PlaywrightAuthManager
from projects.auth_management.logger import setup_logger


async def main() -> None:
    """Основная асинхронная функция."""
    parser = argparse.ArgumentParser(
        description="Bulk authorize users from CSV using Playwright"
    )
    parser.add_argument("csv_path", help="Path to CSV file with user credentials")
    parser.add_argument("--db", dest="db_path", help="Path to SQLite DB (optional)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--relogin", action="store_true", help="Принудительно переавторизовать пользователей, игнорируя кэш")
    args = parser.parse_args()

    logger = setup_logger(__name__)

    # Проверяем существование CSV файла
    if not os.path.exists(args.csv_path):
        logger.error("CSV file %s not found", args.csv_path)
        sys.exit(1)

    # Создаем менеджер авторизации
    auth_manager = PlaywrightAuthManager(headless=args.headless)
    
    try:
        # Выполняем авторизацию
        summary = await auth_manager.authenticate_users_from_csv(
            args.csv_path, 
            force_reauth=args.relogin
        )

        # Выводим результаты
        logger.info(
            "Authorization finished. Success: %d, Failed: %d", 
            len(summary['success']), 
            len(summary['failed'])
        )
        
        if summary["failed"]:
            logger.warning("Failed users: %s", ", ".join(summary["failed"]))
            
        # Код выхода в зависимости от результата
        if summary["failed"]:
            sys.exit(1)  # Есть ошибки
        else:
            sys.exit(0)  # Все успешно
            
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
        sys.exit(1)


def sync_main():
    """Синхронная обертка для совместимости."""
    try:
        # Запускаем асинхронную функцию
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Прервано пользователем")
        sys.exit(130)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_main()
