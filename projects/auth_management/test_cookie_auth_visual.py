#!/usr/bin/env python3
"""
ВИЗУАЛЬНЫЙ ТЕСТ АВТОРИЗАЦИИ ЧЕРЕЗ КУКИ С ASSERT ПРОВЕРКАМИ

Этот скрипт проверяет авторизацию конкретного пользователя в видимом режиме
с детальными assert проверками для отладки.

Использование:
    python test_cookie_auth_visual.py EvgenQA      # Видимый режим
    python test_cookie_auth_visual.py admin       # Видимый режим для админа
    python test_cookie_auth_visual.py EvgenQA --headless  # Скрытый режим
"""

import argparse
import json
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Добавляем путь к корню проекта
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.logger import setup_logger
from framework.utils.url_utils import add_allow_session_param, is_headless

logger = setup_logger(__name__)


def test_user_auth_with_assertions(user_login: str, headless: bool = False, 
                                  slow_motion: int = 1000) -> bool:
    """
    Тестирует авторизацию пользователя с подробными assert проверками.
    
    Args:
        user_login: Логин пользователя для тестирования
        headless: Запуск в скрытом режиме
        slow_motion: Задержка между действиями в миллисекундах
        
    Returns:
        True если все проверки прошли успешно
    """
    print(f"🧪 ДЕТАЛЬНЫЙ ТЕСТ АВТОРИЗАЦИИ: {user_login}")
    print("=" * 60)
    print(f"👁️ Режим: {'скрытый' if headless else 'ВИДИМЫЙ'}")
    print(f"⏱️ Замедление: {slow_motion}мс между действиями")
    print("=" * 60)
    
    # 1. ПРОВЕРКА ФАЙЛА КУКОВ
    print(f"\n📋 ШАГ 1: Проверка файла куков")
    cookies_path = config.COOKIES_PATH.parent / f"{user_login}_cookies.json"
    print(f"   📂 Путь: {cookies_path}")
    
    assert cookies_path.exists(), f"❌ ASSERT FAILED: Файл куков не найден: {cookies_path}"
    print(f"   ✅ Файл куков существует")
    
    # Загружаем куки
    with open(cookies_path, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    
    assert isinstance(cookies, list), f"❌ ASSERT FAILED: Куки должны быть списком, получен {type(cookies)}"
    assert len(cookies) > 0, f"❌ ASSERT FAILED: Файл куков пустой"
    print(f"   ✅ Загружено {len(cookies)} кук")
    
    # Проверяем важные куки
    important_cookies = []
    for cookie in cookies:
        name = cookie.get('name', '')
        if any(keyword in name.lower() for keyword in ['session', 'auth', 'remember', 'token']):
            important_cookies.append(name)
    
    print(f"   🔑 Важные куки авторизации: {', '.join(important_cookies)}")
    
    # 2. ЗАПУСК БРАУЗЕРА
    print(f"\n📋 ШАГ 2: Запуск браузера")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            slow_mo=slow_motion if not headless else 0  # Замедление только в видимом режиме
        )
        context = browser.new_context()
        
        print(f"   ✅ Браузер запущен")
        
        # 3. ДОБАВЛЕНИЕ КУКОВ
        print(f"\n📋 ШАГ 3: Добавление куков в браузер")
        context.add_cookies(cookies)
        print(f"   ✅ {len(cookies)} кук добавлены в контекст браузера")
        
        page = context.new_page()
        
        # 4. ПЕРЕХОД НА ЦЕЛЕВУЮ СТРАНИЦУ
        print(f"\n📋 ШАГ 4: Переход на целевую страницу")
        print(f"   🔗 URL: {config.TARGET_URL}")
        
        try:
            # Увеличиваем таймаут и добавляем отладку
            response = page.goto(add_allow_session_param(config.TARGET_URL, is_headless()), timeout=60000, wait_until="domcontentloaded")
            print(f"   ✅ Страница загружена")
            print(f"   📄 HTTP статус: {response.status if response else 'N/A'}")
        except Exception as e:
            print(f"   ❌ Ошибка загрузки страницы: {e}")
            browser.close()
            raise AssertionError(f"Не удалось загрузить страницу: {e}")
        
        # Ждем дополнительное время для полной загрузки
        try:
            page.wait_for_load_state('networkidle', timeout=10000)
            print(f"   ✅ Сетевая активность завершена")
        except:
            print(f"   ⚠️ Таймаут ожидания сетевой активности (не критично)")
        
        # 5. АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ
        print(f"\n📋 ШАГ 5: Анализ текущего состояния страницы")
        current_url = page.url
        page_title = page.title()
        
        print(f"   🌐 Текущий URL: {current_url}")
        print(f"   📄 Заголовок: {page_title}")
        
        # Проверяем, что не остались на странице логина
        if "login" in current_url.lower():
            print(f"   ❌ ПРОБЛЕМА: Остались на странице логина!")
            print(f"   💡 Это означает, что куки недействительны или не работают")
        else:
            print(f"   ✅ Успешно покинули страницу логина")
        
        # 6. ОСНОВНАЯ ПРОВЕРКА НИКНЕЙМА
        print(f"\n📋 ШАГ 6: ПРОВЕРКА НИКНЕЙМА ПОЛЬЗОВАТЕЛЯ")
        print(f"   🔍 Ищем локатор: .user-in__nick")
        print(f"   🎯 Ожидаемый никнейм: '{user_login}'")
        
        nickname_locator = page.locator('.user-in__nick')
        element_count = nickname_locator.count()
        print(f"   🔢 Найдено элементов .user-in__nick: {element_count}")
        
        # КРИТИЧЕСКИЙ ASSERT
        assert element_count > 0, f"❌ ASSERT FAILED: Элемент .user-in__nick не найден на странице!"
        print(f"   ✅ ASSERT PASSED: Элемент .user-in__nick найден")
        
        # Проверяем видимость
        is_visible = nickname_locator.first.is_visible(timeout=5000)
        assert is_visible, f"❌ ASSERT FAILED: Элемент .user-in__nick найден, но не виден!"
        print(f"   ✅ ASSERT PASSED: Элемент .user-in__nick видим")
        
        # Получаем текст никнейма
        nickname_text = nickname_locator.first.text_content().strip()
        print(f"   📝 Текст никнейма: '{nickname_text}'")
        
        # ФИНАЛЬНЫЙ ASSERT - СОВПАДЕНИЕ НИКНЕЙМА
        assert nickname_text.lower() == user_login.lower(), \
            f"❌ ASSERT FAILED: Никнейм не совпадает! Найден: '{nickname_text}', ожидался: '{user_login}'"
        print(f"   ✅ ASSERT PASSED: Никнейм совпадает!")
        
        # 7. ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ
        print(f"\n📋 ШАГ 7: Дополнительные проверки авторизации")
        
        # Проверяем другие индикаторы
        auth_indicators = [
            ("[data-testid='user-menu']", "Меню пользователя"),
            (".user-profile", "Профиль пользователя"), 
            ("#logout", "Кнопка выхода"),
            ("[href*='logout']", "Ссылка выхода"),
            (".user-name", "Имя пользователя"),
            ("[class*='user']", "Элементы пользователя")
        ]
        
        found_indicators = []
        for selector, description in auth_indicators:
            try:
                if page.locator(selector).first.is_visible(timeout=1000):
                    found_indicators.append(description)
                    print(f"   ✅ Найден: {description}")
            except:
                pass
        
        print(f"   📊 Всего найдено индикаторов авторизации: {len(found_indicators)}")
        
        # 8. ИТОГОВАЯ ПРОВЕРКА
        print(f"\n📋 ШАГ 8: Итоговая оценка")
        
        # Основные критерии успеха
        nickname_ok = nickname_text.lower() == user_login.lower()
        not_on_login = "login" not in current_url.lower()
        has_indicators = len(found_indicators) > 0
        
        print(f"   ✅ Никнейм совпадает: {nickname_ok}")
        print(f"   ✅ Не на странице логина: {not_on_login}")
        print(f"   ✅ Есть индикаторы авторизации: {has_indicators}")
        
        overall_success = nickname_ok and not_on_login
        
        if not headless:
            print(f"\n⏸️ Браузер остается открытым для просмотра...")
            print(f"   💡 Проверьте страницу визуально")
            print(f"   💡 Закройте браузер когда закончите")
            input("\n🔄 Нажмите Enter чтобы закрыть браузер...")
        
        browser.close()
        
        # ФИНАЛЬНЫЙ ASSERT
        assert overall_success, \
            f"❌ ASSERT FAILED: Общая проверка авторизации провалена. " \
            f"Никнейм: {nickname_ok}, Не на логине: {not_on_login}"
        
        print(f"\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print(f"   👤 Пользователь {user_login} успешно авторизован")
        print(f"   🔍 Никнейм '{nickname_text}' найден и совпадает")
        print(f"   🌐 URL: {current_url}")
        
        return True


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description="Визуальный тест авторизации с assert проверками",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Видимый режим (браузер откроется)
  python test_cookie_auth_visual.py EvgenQA
  
  # Видимый режим для админа
  python test_cookie_auth_visual.py admin
  
  # Скрытый режим
  python test_cookie_auth_visual.py EvgenQA --headless
  
  # Медленный режим для отладки (2 секунды между действиями)
  python test_cookie_auth_visual.py EvgenQA --slow 2000
        """
    )
    
    parser.add_argument(
        "user_login",
        help="Логин пользователя для тестирования (например: EvgenQA, admin)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Запуск в скрытом режиме"
    )
    
    parser.add_argument(
        "--slow",
        type=int,
        default=1000,
        help="Задержка между действиями в миллисекундах (по умолчанию: 1000)"
    )
    
    args = parser.parse_args()
    
    try:
        success = test_user_auth_with_assertions(
            user_login=args.user_login,
            headless=args.headless,
            slow_motion=args.slow
        )
        
        if success:
            print(f"\n✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО")
            sys.exit(0)
        else:
            print(f"\n❌ ТЕСТ ПРОВАЛЕН")
            sys.exit(1)
            
    except AssertionError as e:
        print(f"\n❌ ASSERT ERROR: {e}")
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
