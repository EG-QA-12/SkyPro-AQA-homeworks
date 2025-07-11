#!/usr/bin/env python3
"""
ПРОСТОЙ ТЕСТ АВТОРИЗАЦИИ - ПРОВЕРКА НАЛИЧИЯ ЭЛЕМЕНТА .user-in__nick

Этот скрипт проверяет авторизацию любого пользователя просто по наличию
элемента с классом "user-in__nick" на странице.

Использование:
    python test_simple_auth.py EvgenQA        # Видимый режим
    python test_simple_auth.py admin          # Видимый режим для админа  
    python test_simple_auth.py 100 --headless # Скрытый режим
"""

import argparse
import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from framework.utils.url_utils import add_allow_session_param, is_headless

# Добавляем путь к корню проекта
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from .config import config
from .logger import setup_logger

logger = setup_logger(__name__)


def test_auth_simple(user_login: str, headless: bool = False) -> bool:
    """
    Простой тест авторизации - проверяет только наличие элемента .user-in__nick
    
    Args:
        user_login: Логин пользователя для тестирования
        headless: Запуск в скрытом режиме
        
    Returns:
        True если элемент найден (пользователь авторизован)
    """
    print(f"🧪 ПРОСТОЙ ТЕСТ АВТОРИЗАЦИИ: {user_login}")
    print("=" * 50)
    print(f"👁️ Режим: {'скрытый' if headless else 'ВИДИМЫЙ'}")
    print("=" * 50)
    
    # Проверяем файл куков
    cookies_path = config.COOKIES_PATH.parent / f"{user_login}_cookies.json"
    print(f"📂 Файл куков: {cookies_path.name}")
    
    if not cookies_path.exists():
        print(f"❌ ОШИБКА: Файл куков не найден!")
        return False
    
    # Загружаем куки
    with open(cookies_path, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    
    print(f"🍪 Загружено {len(cookies)} кук")
    
    # Запускаем браузер
    print(f"🌐 Запуск браузера...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=500 if not headless else 0)
        context = browser.new_context()
        
        # Добавляем куки
        context.add_cookies(cookies)
        page = context.new_page()
        
        print(f"🔗 Переход на: {config.TARGET_URL}")
        
        try:
            # Переходим на целевую страницу
            response = page.goto(add_allow_session_param(config.TARGET_URL, is_headless()), timeout=45000)
            print(f"✅ Страница загружена (HTTP {response.status if response else 'N/A'})")
            
            # Ждем загрузки страницы
            try:
                page.wait_for_load_state('domcontentloaded', timeout=10000)
            except:
                pass
            
            # Получаем информацию о странице
            current_url = page.url
            page_title = page.title()
            
            print(f"📍 Текущий URL: {current_url}")
            print(f"📄 Заголовок: {page_title}")
            
            # ГЛАВНАЯ ПРОВЕРКА: ищем элемент .user-in__nick
            print(f"\n🔍 ГЛАВНАЯ ПРОВЕРКА: Поиск элемента .user-in__nick")
            
            nickname_locator = page.locator('.user-in__nick')
            element_count = nickname_locator.count()
            
            print(f"🔢 Найдено элементов: {element_count}")
            
            if element_count > 0:
                # Проверяем видимость
                is_visible = nickname_locator.first.is_visible(timeout=3000)
                
                if is_visible:
                    # Получаем текст (для информации)
                    try:
                        nickname_text = nickname_locator.first.text_content().strip()
                        print(f"📝 Текст никнейма: '{nickname_text}'")
                    except:
                        nickname_text = "не удалось получить"
                        print(f"📝 Текст никнейма: {nickname_text}")
                    
                    print(f"✅ УСПЕХ: Элемент .user-in__nick найден и видим!")
                    print(f"✅ РЕЗУЛЬТАТ: Пользователь АВТОРИЗОВАН")
                    
                    auth_success = True
                else:
                    print(f"❌ Элемент .user-in__nick найден, но НЕ ВИДЕН")
                    print(f"❌ РЕЗУЛЬТАТ: Пользователь НЕ авторизован")
                    auth_success = False
            else:
                print(f"❌ Элемент .user-in__nick НЕ НАЙДЕН на странице")
                
                # Дополнительная диагностика
                if "login" in current_url.lower():
                    print(f"💡 Причина: Остались на странице логина - куки не работают")
                else:
                    print(f"💡 Возможные причины:")
                    print(f"   - Изменилась структура страницы")
                    print(f"   - Страница загружается медленно")
                    print(f"   - Куки недействительны")
                
                print(f"❌ РЕЗУЛЬТАТ: Пользователь НЕ авторизован")
                auth_success = False
            
            # В видимом режиме оставляем браузер открытым
            if not headless:
                print(f"\n⏸️ Браузер открыт для визуального анализа")
                print(f"💡 Проверьте страницу самостоятельно")
                print(f"💡 Элемент должен быть: <div class=\"user-in__nick\">НикнеймПользователя</div>")
                input(f"\n🔄 Нажмите Enter для закрытия браузера...")
            
            browser.close()
            return auth_success
            
        except Exception as e:
            print(f"❌ ОШИБКА при загрузке страницы: {e}")
            browser.close()
            return False


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description="Простой тест авторизации по наличию элемента .user-in__nick",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Видимый режим (браузер откроется)
  python test_simple_auth.py EvgenQA
  
  # Видимый режим для админа
  python test_simple_auth.py admin
  
  # Видимый режим для пользователя с цифровым ID
  python test_simple_auth.py 100
  
  # Скрытый режим
  python test_simple_auth.py EvgenQA --headless
        """
    )
    
    parser.add_argument(
        "user_login",
        help="Логин пользователя для тестирования (например: EvgenQA, admin, 100)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Запуск в скрытом режиме"
    )
    
    args = parser.parse_args()
    
    try:
        print(f"🚀 Запуск простого теста авторизации")
        print(f"🎯 Проверяем наличие элемента: .user-in__nick")
        print(f"👤 Пользователь: {args.user_login}")
        print()
        
        success = test_auth_simple(
            user_login=args.user_login,
            headless=args.headless
        )
        
        print(f"\n" + "=" * 50)
        if success:
            print(f"🎉 ТЕСТ ПРОЙДЕН: Пользователь {args.user_login} авторизован!")
            print(f"✅ Элемент .user-in__nick найден и видим")
            sys.exit(0)
        else:
            print(f"❌ ТЕСТ ПРОВАЛЕН: Пользователь {args.user_login} НЕ авторизован")
            print(f"❌ Элемент .user-in__nick не найден или не виден")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Тест прерван пользователем")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        logger.error(f"Критическая ошибка в тесте: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
