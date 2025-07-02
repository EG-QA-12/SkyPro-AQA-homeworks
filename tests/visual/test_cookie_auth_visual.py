#!/usr/bin/env python3
"""
Визуальный тест авторизации через подставление кук.
Запускает браузер в обычном режиме для демонстрации работы авторизации через куки.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import time

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.auth import load_cookies
from src.logger import setup_logger

logger = setup_logger(__name__)

def visual_cookie_auth_demo(user_login: str = None):
    """
    Демонстрирует авторизацию через куки в визуальном режиме.
    
    Args:
        user_login: Логин пользователя для демонстрации
    """
    print(f"🎭 ВИЗУАЛЬНАЯ ДЕМОНСТРАЦИЯ авторизации через куки")
    
    # Определяем пользователя для тестирования
    if not user_login:
        # Проверяем доступных пользователей
        cookies_dir = config.COOKIES_PATH.parent
        cookie_files = list(cookies_dir.glob("*_cookies.json"))
        if cookie_files:
            user_login = cookie_files[0].stem.replace("_cookies", "")
            print(f"🔄 Автоматически выбран пользователь: {user_login}")
        else:
            print("❌ Не найдено файлов кук")
            return False
    
    cookies_file = config.COOKIES_PATH.parent / f"{user_login}_cookies.json"
    
    if not cookies_file.exists():
        print(f"❌ Файл кук для пользователя {user_login} не найден: {cookies_file}")
        return False
    
    try:
        with sync_playwright() as p:
            print(f"🌐 Запуск браузера в визуальном режиме...")
            
            # Запускаем браузер в обычном режиме (не headless)
            browser = p.chromium.launch(
                headless=False,
                slow_mo=1000,  # Замедляем действия для лучшей видимости
                args=['--start-maximized']
            )
            
            print(f"\\n📺 ДЕМОНСТРАЦИЯ 1: Доступ БЕЗ кук")
            print("   Откроется браузер и покажет, что без кук происходит редирект на логин")
            
            # Создаем контекст без кук
            context_no_auth = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page_no_auth = context_no_auth.new_page()
            
            print(f"   🔗 Переходим на: {config.TARGET_URL}")
            page_no_auth.goto(config.TARGET_URL)
            
            print(f"   ⏱️ Пауза 3 секунды для просмотра...")
            time.sleep(3)
            
            current_url = page_no_auth.url
            print(f"   📍 Текущий URL: {current_url}")
            
            if "login" in current_url.lower():
                print("   ✅ Корректно: редирект на страницу логина")
            else:
                print("   ⚠️ Неожиданно: остались на целевой странице")
            
            context_no_auth.close()
            
            print(f"\\n📺 ДЕМОНСТРАЦИЯ 2: Доступ С куками пользователя {user_login}")
            print("   Сейчас загрузим куки и покажем успешную авторизацию")
            
            # Загружаем куки
            cookies = load_cookies(cookies_file)
            if not cookies:
                print(f"   ❌ Не удалось загрузить куки")
                browser.close()
                return False
            
            print(f"   📊 Загружено {len(cookies)} кук")
            
            # Создаем новый контекст с куками
            context_with_auth = browser.new_context(viewport={'width': 1920, 'height': 1080})
            context_with_auth.add_cookies(cookies)
            page_with_auth = context_with_auth.new_page()
            
            print(f"   🔗 Переходим на: {config.TARGET_URL}")
            page_with_auth.goto(config.TARGET_URL)
            
            print(f"   ⏱️ Пауза 5 секунд для просмотра результата...")
            time.sleep(5)
            
            auth_url = page_with_auth.url
            print(f"   📍 Текущий URL: {auth_url}")
            
            if config.TARGET_URL in auth_url or auth_url.startswith(config.BASE_URL):
                print("   ✅ Успешно: авторизация через куки работает!")
                
                # Дополнительная проверка элементов
                try:
                    # Ищем признаки авторизации
                    if page_with_auth.locator("text=Выход").count() > 0:
                        print("   ✅ Найден элемент 'Выход'")
                        page_with_auth.locator("text=Выход").highlight()
                    elif page_with_auth.locator("[href*='logout']").count() > 0:
                        print("   ✅ Найдена ссылка выхода")
                        page_with_auth.locator("[href*='logout']").first.highlight()
                    
                    # Показываем заголовок страницы
                    title = page_with_auth.title()
                    print(f"   📄 Заголовок страницы: {title}")
                    
                except Exception as e:
                    print(f"   ⚠️ Ошибка при поиске элементов: {e}")
                
            else:
                print("   ❌ Ошибка: не удалось авторизоваться через куки")
            
            print(f"\\n⏱️ Пауза 10 секунд для изучения страницы...")
            print("   💡 Вы можете взаимодействовать со страницей в браузере")
            time.sleep(10)
            
            print(f"\\n📊 ИНФОРМАЦИЯ О КУКАХ:")
            
            # Анализируем куки
            from datetime import datetime
            current_time = datetime.now().timestamp()
            
            important_cookies = []
            valid_count = 0
            
            for cookie in cookies:
                name = cookie.get("name", "")
                domain = cookie.get("domain", "")
                expires = cookie.get("expires", -1)
                
                # Проверяем важные куки
                if any(keyword in name.lower() for keyword in ["session", "auth", "login", "remember", "token", "xsrf"]):
                    expiry_status = "сессионная" if expires == -1 else ("валидна" if expires > current_time else "просрочена")
                    important_cookies.append(f"{name} ({domain}) - {expiry_status}")
                
                if expires == -1 or expires > current_time:
                    valid_count += 1
            
            print(f"   📊 Всего кук: {len(cookies)}")
            print(f"   ✅ Активных кук: {valid_count}")
            print(f"   🔑 Важные куки авторизации:")
            for cookie_info in important_cookies:
                print(f"      • {cookie_info}")
            
            context_with_auth.close()
            browser.close()
            
            print(f"\\n🎉 Визуальная демонстрация завершена!")
            print(f"   Результат: Авторизация через куки работает корректно")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка во время демонстрации: {e}")
        logger.error(f"Ошибка визуальной демонстрации: {e}")
        return False

def main():
    """Основная функция."""
    print("🎭 ВИЗУАЛЬНАЯ ДЕМОНСТРАЦИЯ авторизации через подставление кук")
    print("=" * 70)
    print("📢 Внимание: Откроется браузер для демонстрации работы авторизации через куки")
    print("🕒 Демонстрация займет около 20 секунд")
    print("")
    
    # Проверяем доступных пользователей
    cookies_dir = config.COOKIES_PATH.parent
    cookie_files = list(cookies_dir.glob("*_cookies.json"))
    
    if not cookie_files:
        print("❌ Не найдено файлов кук для демонстрации")
        return False
    
    available_users = [f.stem.replace("_cookies", "") for f in cookie_files]
    print(f"📁 Найдены куки для пользователей: {', '.join(available_users)}")
    
    # Выбираем первого пользователя для демонстрации
    demo_user = available_users[0]
    print(f"🎯 Демонстрация с пользователем: {demo_user}")
    
    input("\\n👆 Нажмите Enter для начала демонстрации...")
    
    success = visual_cookie_auth_demo(demo_user)
    
    if success:
        print(f"\\n🎉 Демонстрация завершена успешно!")
        print("✅ Авторизация через подставление кук работает корректно")
    else:
        print(f"\\n❌ Во время демонстрации возникли проблемы")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
