#!/usr/bin/env python3
"""
Скрипт для реальной авторизации всех пользователей через браузер.

Использование:
    python scripts/real_auth_all_users.py [--headless] [--force]
    
Аргументы:
    --headless: Запуск браузера в безголовом режиме
    --force: Принудительная переавторизация даже для пользователей с валидными куками
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Добавляем путь к корню проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.user_manager import UserManager
from src.auth import perform_login_on_page
from src.config import config
from src.logger import setup_logger
from playwright.sync_api import sync_playwright

logger = setup_logger(__name__)


def get_user_credentials(user: Dict[str, Any]) -> tuple[str, str]:
    """
    Получает учетные данные пользователя для авторизации.
    
    Args:
        user: Данные пользователя из базы
        
    Returns:
        Кортеж (логин, пароль)
    """
    username = user.get('username') or user.get('login')
    role = user.get('role', '').lower()
    
    # Маппинг ролей к учетным данным из конфигурации
    role_credentials_map = {
        'admin': (config.ADMIN_LOGIN, config.ADMIN_PASS),
        'moderator': (config.MODERATOR_LOGIN, config.MODERATOR_PASS),
        'expert': (config.EXPERT_LOGIN, config.EXPERT_PASS),
        'user': (config.USER_LOGIN, config.USER_PASS),
        'qa': (config.USER_LOGIN, config.USER_PASS),  # QA используют обычные учетные данные
        'tester': (config.USER_LOGIN, config.USER_PASS)  # Тестеры тоже
    }
    
    # Если есть соответствие роли в конфигурации, используем его
    if role in role_credentials_map:
        return role_credentials_map[role]
    
    # Иначе используем учетные данные по умолчанию
    return config.LOGIN, config.PASS


def authorize_user_real(user: Dict[str, Any], headless: bool = True) -> bool:
    """
    Выполняет реальную авторизацию пользователя через браузер.
    
    Args:
        user: Данные пользователя
        headless: Запуск в безголовом режиме
        
    Returns:
        True если авторизация успешна
    """
    username = user.get('username') or user.get('login')
    
    try:
        logger.info(f"Начинаем авторизацию пользователя: {username}")
        
        # Получаем учетные данные для пользователя
        login, password = get_user_credentials(user)
        
        if not login or not password:
            logger.error(f"Не удалось получить учетные данные для пользователя {username}")
            return False
        
        logger.debug(f"Используем логин: {login} для пользователя {username}")
        
        # Формируем путь для сохранения куков
        cookies_path = config.COOKIES_PATH.parent / f"{username}_cookies.json"
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True
            )
            page = context.new_page()
            
            # Выполняем авторизацию
            perform_login_on_page(
                page=page,
                login=login,
                password=password,
                cookies_path=cookies_path,
                login_url=config.LOGIN_URL,
                target_url=config.TARGET_URL
            )
            
            # Сохраняем куки в базу данных
            cookies = context.cookies()
            user_manager = UserManager()
            user_manager.save_cookies(user['id'], cookies)
            user_manager.update_cookie_expiry(user['id'])
            
            browser.close()
            
        logger.info(f"Авторизация пользователя {username} успешно завершена")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка авторизации пользователя {username}: {e}")
        return False


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(
        description="Реальная авторизация всех пользователей.\n"
                    "По умолчанию перед авторизацией выполняется импорт CSV, "
                    "если файл найден. Используйте --skip-csv-import, чтобы пропустить.")
    parser.add_argument("--headless", action="store_true", 
                       help="Запуск браузера в безголовом режиме")
    parser.add_argument("--force", action="store_true",
                       help="Принудительная переавторизация всех пользователей")
    parser.add_argument("--skip-csv-import", action="store_true",
                       help="Не выполнять импорт пользователей из CSV перед авторизацией")

    args = parser.parse_args()
    
    user_manager = UserManager()

    # ------------------------------------------------------------------
    # Импорт пользователей из CSV (если не пропущен флагом и файл есть)
    # ------------------------------------------------------------------
    if not args.skip_csv_import and config.BULK_CSV_PATH.exists():
        logger.info("Импортируем пользователей из CSV: %s", config.BULK_CSV_PATH)
        csv_result = user_manager.authorize_users_from_csv(str(config.BULK_CSV_PATH), headless=args.headless)
        logger.info("Импорт CSV завершён: добавлено %d, ошибок %d", len(csv_result.get('success', {})), len(csv_result.get('failed', [])))
    elif not args.skip_csv_import:
        logger.warning("Файл CSV %s не найден. Импорт пропущен.", config.BULK_CSV_PATH)
    users = user_manager.get_all_users()
    
    if not users:
        logger.warning("В базе данных нет пользователей для авторизации")
        return
    
    logger.info(f"Найдено {len(users)} пользователей для авторизации")
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for user in users:
        username = user.get('username') or user.get('login')
        
        # Проверяем, нужна ли авторизация
        if not args.force and user_manager.is_cookie_valid(user['id']):
            logger.info(f"Пользователь {username} уже имеет валидные куки, пропускаем")
            skipped_count += 1
            continue
        
        # Выполняем авторизацию
        if authorize_user_real(user, headless=args.headless):
            success_count += 1
        else:
            failed_count += 1
        
        # Небольшая пауза между авторизациями
        time.sleep(2)
    
    logger.info(f"Авторизация завершена. Успешно: {success_count}, "
               f"Ошибок: {failed_count}, Пропущено: {skipped_count}")
    
    if failed_count > 0:
        logger.warning(f"Некоторые пользователи ({failed_count}) не были авторизованы")
        sys.exit(1)
    else:
        logger.info("Все пользователи успешно авторизованы!")


if __name__ == "__main__":
    main()
