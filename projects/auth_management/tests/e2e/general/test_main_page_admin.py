#!/usr/bin/env python3
"""
Скрипт для запуска теста главной страницы под администратором.
"""

import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.user_manager import UserManager
from src.auth import load_cookies
from src.logger import setup_logger
from framework.utils.url_utils import add_allow_session_param, is_headless

def test_main_page_admin():
    """Тест главной страницы под администратором."""
    logger = setup_logger(__name__)
    logger.info("🚀 Запуск теста главной страницы под администратором")
    
    try:
        # Инициализация менеджера пользователей
        user_manager = UserManager()
        
        # Получаем пользователя admin
        admin_user = user_manager.get_user("admin")
        if not admin_user:
            logger.error("❌ Пользователь admin не найден в базе данных")
            return False
        
        logger.info(f"✅ Найден пользователь: {admin_user.get('login')} (роль: {admin_user.get('role')})")
        
        # Путь к куки admin'а
        admin_login = admin_user.get('login') or admin_user.get('username', 'admin')
        cookies_path = config.COOKIES_PATH.parent / f"{admin_login}_cookies.json"
        logger.info(f"📂 Путь к куки: {cookies_path}")
        
        # Загружаем куки
        cookies = load_cookies(cookies_path)
        if not cookies:
            logger.error("❌ Куки для администратора не найдены или невалидны")
            logger.info("💡 Сначала выполните авторизацию администратора через GUI или CLI")
            return False
        
        logger.info(f"🍪 Загружено {len(cookies)} куки")
        
        # Запускаем браузер
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=config.HEADLESS)
            context = browser.new_context()
            
            # Добавляем куки
            context.add_cookies(cookies)
            logger.info("🔐 Куки добавлены в контекст браузера")
            
            page = context.new_page()
            
            # Отслеживаем JS ошибки
            js_errors = []
            page.on("pageerror", lambda error: js_errors.append(str(error)))
            
            logger.info("🌐 Переходим на главную страницу...")
            
            # Переходим на главную страницу (используем TARGET_URL для авторизованных пользователей)
            target_url = getattr(config, 'TARGET_URL', config.BASE_URL)
            logger.info(f"🎯 Целевой URL: {target_url}")
            
            response = page.goto(add_allow_session_param(target_url, is_headless()), timeout=30000)
            
            # Проверяем статус ответа
            logger.info(f"📊 Статус ответа: {response.status}")
            if response.status == 500:
                logger.warning("⚠️ Сервер вернул статус 500, попробуем BASE_URL")
                response = page.goto(add_allow_session_param(config.BASE_URL, is_headless()), timeout=30000)
                
            if response.status not in [200, 302, 303]:
                logger.error(f"❌ Неожиданный статус ответа: {response.status}")
                browser.close()
                return False
            
            logger.info(f"✅ Статус ответа: {response.status}")
            
            # Ждем полной загрузки страницы
            page.wait_for_load_state('networkidle')
            logger.info("⏳ Страница полностью загружена")
            
            # Проверяем JS ошибки
            if js_errors:
                logger.warning(f"⚠️ Обнаружены JS ошибки: {js_errors}")
            else:
                logger.info("✅ JS ошибок не обнаружено")
            
            # Проверяем заголовок страницы
            title = page.title()
            logger.info(f"📄 Заголовок страницы: '{title}'")
            
            if "BLL" not in title:
                logger.warning(f"⚠️ Неожиданный заголовок: '{title}'")
            else:
                logger.info("✅ Заголовок страницы корректен")
            
            # Проверяем основной контент
            content_selectors = [
                "body",
                "header", 
                "main",
                ".container",
                "#header",
                ".header"
            ]
            
            content_found = False
            for selector in content_selectors:
                try:
                    if page.is_visible(selector):
                        logger.info(f"✅ Найден видимый элемент: {selector}")
                        content_found = True
                        break
                except Exception:
                    continue
            
            if not content_found:
                logger.error("❌ Основной контент страницы не найден")
                browser.close()
                return False
            
            # Делаем скриншот для документации
            screenshot_path = project_root / "data" / "main_page_admin_screenshot.png"
            screenshot_path.parent.mkdir(exist_ok=True)
            page.screenshot(path=str(screenshot_path))
            logger.info(f"📸 Скриншот сохранен: {screenshot_path}")
            
            # Проверяем URL после возможных редиректов
            current_url = page.url
            logger.info(f"🔗 Текущий URL: {current_url}")
            
            browser.close()
            
            logger.info("🎉 Тест главной страницы под администратором завершен успешно!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка теста: {e}")
        return False

def main():
    """Главная функция."""
    print("=" * 60)
    print("🔬 ТЕСТ ГЛАВНОЙ СТРАНИЦЫ ПОД АДМИНИСТРАТОРОМ")
    print("=" * 60)
    
    success = test_main_page_admin()
    
    print("=" * 60)
    if success:
        print("✅ ТЕСТ ПРОЙДЕН УСПЕШНО")
    else:
        print("❌ ТЕСТ ПРОВАЛЕН")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
