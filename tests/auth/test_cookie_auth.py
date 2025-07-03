#!/usr/bin/env python3
"""
Тест авторизации через подставление кук.
Проверяет работу авторизации с сохраненными куками без ввода логина/пароля.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
from framework.utils.url_utils import add_allow_session_param, is_headless

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.auth import load_cookies
from src.logger import setup_logger

logger = setup_logger(__name__)

def test_cookie_authentication():
    """
    Тестирует авторизацию через подставление кук.
    
    Pytest тест для проверки авторизации через сохраненные куки.
    Автоматически находит доступных пользователей и тестирует первого.
    """
    # Находим доступных пользователей
    cookies_dir = config.COOKIES_PATH.parent
    cookie_files = list(cookies_dir.glob("*_cookies.json"))
    
    if not cookie_files:
        print("❌ Не найдено ни одного файла кук")
        assert False, "Файлы кук не найдены"
    
    # Берем первый доступный файл
    cookies_file = cookie_files[0]
    user_login = cookies_file.stem.replace("_cookies", "")
    
    print(f"🍪 Начинаем тестирование авторизации через куки для пользователя: {user_login}")
    
    if not cookies_file.exists():
        print(f"❌ Файл кук для пользователя {user_login} не найден: {cookies_file}")
        # Проверяем, есть ли файлы кук в директории
        cookies_dir = config.COOKIES_PATH.parent
        cookie_files = list(cookies_dir.glob("*_cookies.json"))
        if cookie_files:
            print(f"📁 Найдены файлы кук: {[f.name for f in cookie_files]}")
            # Берем первый доступный файл
            cookies_file = cookie_files[0]
            user_login = cookies_file.stem.replace("_cookies", "")
            print(f"🔄 Используем куки пользователя: {user_login}")
        else:
            print("❌ Не найдено ни одного файла кук")
            assert False, "Файлы кук не найдены"
    
    try:
        with sync_playwright() as p:
            # Запускаем браузер
            headless = True  # Всегда запускаем в headless режиме для pytest
            print(f"🌐 Запуск браузера (headless: {headless})...")
            browser = p.chromium.launch(headless=headless)
            
            # ТЕСТ 1: Проверка доступа БЕЗ кук (должен перенаправлять на логин)
            print("\n📋 ТЕСТ 1: Проверка доступа без авторизации")
            context_no_auth = browser.new_context()
            page_no_auth = context_no_auth.new_page()
            page_no_auth.goto(config.TARGET_URL, timeout=30000)
            no_auth_url = page_no_auth.url
            print(f"   🔗 URL без авторизации: {no_auth_url}")
            
            # Проверяем, что происходит редирект на страницу логина
            if "login" in no_auth_url.lower() or no_auth_url == config.LOGIN_URL:
                print("   ✅ Корректно: без кук происходит редирект на страницу логина")
                no_auth_success = True
            else:
                print("   ⚠️ Неожиданно: доступ к целевой странице без авторизации")
                no_auth_success = False
            
            context_no_auth.close()
            
            # ТЕСТ 2: Проверка авторизации С куками
            print(f"\n📋 ТЕСТ 2: Проверка авторизации с куками пользователя {user_login}")
            
            # Загружаем куки
            cookies = load_cookies(cookies_file)
            if not cookies:
                print(f"   ❌ Не удалось загрузить куки из {cookies_file}")
                browser.close()
                assert False, f"Не удалось загрузить куки из {cookies_file}"
            
            print(f"   📊 Загружено {len(cookies)} кук")
            
            # Создаем новый контекст и добавляем куки
            context_with_auth = browser.new_context()
            context_with_auth.add_cookies(cookies)
            page_with_auth = context_with_auth.new_page()
            
            # Переходим на целевую страницу
            print(f"   🔗 Переход на целевую страницу: {config.TARGET_URL}")
            page_with_auth.goto(add_allow_session_param(config.TARGET_URL, is_headless()), timeout=30000)
            auth_url = page_with_auth.url
            print(f"   🔗 URL с авторизацией: {auth_url}")
            
            # Проверяем успешную авторизацию
            if config.TARGET_URL in auth_url or auth_url.startswith(config.BASE_URL):
                print("   ✅ Успешно: авторизация через куки работает")
                auth_success = True
                
                # ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: Ищем элементы, указывающие на авторизацию
                try:
                    # Проверяем наличие элементов профиля или выхода
                    if page_with_auth.locator("text=Выход").count() > 0:
                        print("   ✅ Найден элемент 'Выход' - пользователь авторизован")
                    elif page_with_auth.locator("text=Профиль").count() > 0:
                        print("   ✅ Найден элемент 'Профиль' - пользователь авторизован")
                    elif page_with_auth.locator("[href*='logout']").count() > 0:
                        print("   ✅ Найдена ссылка выхода - пользователь авторизован")
                    else:
                        print("   ⚠️ Не найдены явные признаки авторизации на странице")
                        
                        # Делаем скриншот для анализа
                        screenshot_path = project_root / "logs" / f"auth_test_{user_login}.png"
                        page_with_auth.screenshot(path=str(screenshot_path))
                        print(f"   📸 Скриншот сохранен: {screenshot_path}")
                        
                except Exception as e:
                    print(f"   ⚠️ Ошибка при проверке элементов авторизации: {e}")
                
            else:
                print("   ❌ Ошибка: с куками происходит редирект, авторизация не работает")
                auth_success = False
            
            # ТЕСТ 3: Проверка кук на валидность
            print(f"\n📋 ТЕСТ 3: Анализ кук пользователя {user_login}")
            
            from datetime import datetime
            current_time = datetime.now().timestamp()
            valid_cookies = 0
            expired_cookies = 0
            session_cookies = 0
            
            for cookie in cookies:
                if cookie.get("expires", -1) == -1:
                    session_cookies += 1
                elif cookie.get("expires", 0) > current_time:
                    valid_cookies += 1
                else:
                    expired_cookies += 1
            
            print(f"   📊 Всего кук: {len(cookies)}")
            print(f"   ✅ Валидных кук: {valid_cookies}")
            print(f"   ⏰ Сессионных кук: {session_cookies}")
            print(f"   ❌ Просроченных кук: {expired_cookies}")
            
            # Показываем важные куки
            important_cookies = []
            for cookie in cookies:
                name = cookie.get("name", "")
                if any(keyword in name.lower() for keyword in ["session", "auth", "login", "remember", "token"]):
                    important_cookies.append(name)
            
            if important_cookies:
                print(f"   🔑 Важные куки авторизации: {', '.join(important_cookies)}")
            
            context_with_auth.close()
            browser.close()
            
            # ИТОГОВЫЙ РЕЗУЛЬТАТ
            print(f"\n📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
            print(f"   Пользователь: {user_login}")
            print(f"   Файл кук: {cookies_file.name}")
            print(f"   Тест без авторизации: {'✅ Прошел' if no_auth_success else '❌ Провален'}")
            print(f"   Тест с авторизацией: {'✅ Прошел' if auth_success else '❌ Провален'}")
            print(f"   Статус кук: {valid_cookies + session_cookies} активных из {len(cookies)} общих")
            
            overall_success = no_auth_success and auth_success
            
            if overall_success:
                print(f"\n🎉 ТЕСТ УСПЕШЕН: Авторизация через куки работает корректно!")
                assert True  # Тест прошел успешно
            else:
                print(f"\n⚠️ ТЕСТ ПРОВАЛЕН: Обнаружены проблемы с авторизацией через куки")
                assert False, "Проблемы с авторизацией через куки"
            
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        logger.error(f"Ошибка тестирования авторизации через куки: {e}")
        assert False, f"Ошибка тестирования авторизации через куки: {e}"

def main():
    """Основная функция."""
    print("🚀 Запуск теста авторизации через подставление кук")
    print("=" * 60)
    
    # Можно тестировать разных пользователей
    test_users = ["admin", "DxYZ-Ab7", "yR-SUV-t", "eGH344kH"]  # По файлам кук в data/
    
    success_count = 0
    total_count = 0
    
    # Проверяем доступных пользователей
    cookies_dir = config.COOKIES_PATH.parent
    available_users = []
    
    for user in test_users:
        cookies_file = cookies_dir / f"{user}_cookies.json"
        if cookies_file.exists():
            available_users.append(user)
    
    if not available_users:
        print("❌ Не найдено файлов кук для тестирования")
        return False
    
    print(f"📁 Найдены куки для пользователей: {', '.join(available_users)}")
    
    # Тестируем первого доступного пользователя
    test_user = available_users[0]
    print(f"\n🎯 Тестирование пользователя: {test_user}")
    
    # Спрашиваем, запускать ли в headless режиме
    headless_mode = True  # По умолчанию headless для автоматических тестов
    
    try:
        test_cookie_authentication()  # Функция pytest не принимает параметры
        success = True
    except AssertionError:
        success = False
    
    if success:
        print(f"\n🎉 Тестирование завершено успешно!")
        return True
    else:
        print(f"\n❌ Тестирование провалено!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
