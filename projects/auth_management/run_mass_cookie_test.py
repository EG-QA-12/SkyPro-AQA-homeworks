#!/usr/bin/env python3
"""
МАССОВАЯ ПРОВЕРКА АВТОРИЗАЦИИ ЧЕРЕЗ КУКИ В CLI РЕЖИМЕ

Этот скрипт проверяет авторизацию всех пользователей с сохраненными куками
без необходимости GUI интерфейса.

Использование:
    python run_mass_cookie_test.py                    # Обычная проверка
    python run_mass_cookie_test.py --headless         # Скрытый режим
    python run_mass_cookie_test.py --fast             # Быстрая проверка (без детального анализа)
    python run_mass_cookie_test.py --parallel         # Параллельная проверка (быстрее)
    python run_mass_cookie_test.py --user admin       # Проверка конкретного пользователя
"""

import argparse
import concurrent.futures
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Добавляем путь к корню проекта
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from projects.auth_management.config import config
from projects.auth_management.logger import setup_logger
from projects.auth_management.user_manager import UserManager
from playwright.sync_api import sync_playwright

logger = setup_logger(__name__)


class MassCookieAuthTester:
    """Класс для массовой проверки авторизации через куки."""
    
    def __init__(self, headless: bool = True, fast_mode: bool = False):
        """
        Инициализация тестера.
        
        Args:
            headless: Запуск браузера в скрытом режиме
            fast_mode: Быстрый режим (менее детальные проверки)
        """
        self.headless = headless
        self.fast_mode = fast_mode
        self.user_manager = UserManager()
        
    def test_single_user_cookies(self, user_login: str) -> Dict[str, Any]:
        """
        Проверяет авторизацию одного пользователя через куки.
        
        Args:
            user_login: Логин пользователя
            
        Returns:
            Результат проверки
        """
        start_time = time.time()
        result = {
            'user_login': user_login,
            'success': False,
            'auth_confirmed': False,
            'cookies_loaded': False,
            'cookies_count': 0,
            'current_url': '',
            'page_title': '',
            'nickname_found': '',
            'error': None,
            'duration_seconds': 0
        }
        
        try:
            # Проверяем файл куков
            cookies_path = config.COOKIES_PATH.parent / f"{user_login}_cookies.json"
            
            if not cookies_path.exists():
                result['error'] = f"Файл куков не найден: {cookies_path}"
                return result
            
            # Загружаем куки
            with open(cookies_path, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            result['cookies_loaded'] = True
            result['cookies_count'] = len(cookies)
            
            # Проверяем авторизацию через браузер
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context()
                
                # Добавляем куки
                context.add_cookies(cookies)
                page = context.new_page()
                
                # Переходим на целевую страницу
                page.goto(config.TARGET_URL, timeout=30000)
                
                # Ждем загрузки страницы
                try:
                    page.wait_for_load_state('domcontentloaded', timeout=5000)
                except:
                    pass
                
                result['current_url'] = page.url
                result['page_title'] = page.title()
                
                # Проверяем авторизацию
                auth_confirmed = False
                
                # 1. Проверяем никнейм пользователя
                try:
                    nickname_locator = page.locator('.user-in__nick')
                    if nickname_locator.count() > 0 and nickname_locator.first.is_visible(timeout=2000):
                        nickname_text = nickname_locator.first.text_content().strip()
                        result['nickname_found'] = nickname_text
                        
                        if nickname_text.lower() == user_login.lower():
                            auth_confirmed = True
                        
                except Exception:
                    pass
                
                # 2. Если никнейм не найден, проверяем другие индикаторы
                if not auth_confirmed and not self.fast_mode:
                    auth_indicators = [
                        "[data-testid='user-menu']",
                        ".user-profile",
                        "#logout",
                        "[href*='logout']",
                        ".user-name",
                        "[class*='user']"
                    ]
                    
                    found_indicators = []
                    for indicator in auth_indicators:
                        try:
                            if page.locator(indicator).first.is_visible(timeout=500):
                                found_indicators.append(indicator)
                        except:
                            pass
                    
                    if found_indicators:
                        auth_confirmed = True
                
                # 3. Проверяем URL
                if not auth_confirmed:
                    if (config.TARGET_URL in result['current_url'] and 
                        "login" not in result['current_url'].lower()):
                        auth_confirmed = True
                
                result['auth_confirmed'] = auth_confirmed
                result['success'] = True
                
                browser.close()
                
        except Exception as e:
            result['error'] = str(e)
        
        result['duration_seconds'] = round(time.time() - start_time, 2)
        return result
    
    def test_all_users(self, specific_user: Optional[str] = None, 
                      max_parallel: int = 3) -> Dict[str, Any]:
        """
        Проверяет авторизацию всех пользователей с куками.
        
        Args:
            specific_user: Проверить только конкретного пользователя
            max_parallel: Максимальное количество параллельных проверок
            
        Returns:
            Результаты всех проверок
        """
        print("🚀 МАССОВАЯ ПРОВЕРКА АВТОРИЗАЦИИ ЧЕРЕЗ КУКИ")
        print("=" * 70)
        
        # Находим файлы куков
        cookies_dir = config.COOKIES_PATH.parent
        cookie_files = list(cookies_dir.glob("*_cookies.json"))
        
        if not cookie_files:
            print("❌ Не найдено файлов куков для проверки")
            return {'success': False, 'error': 'Файлы куков не найдены'}
        
        # Фильтруем пользователей
        if specific_user:
            user_logins = [specific_user]
            print(f"🎯 Проверка конкретного пользователя: {specific_user}")
        else:
            user_logins = [f.stem.replace('_cookies', '') for f in cookie_files]
            print(f"📊 Найдено {len(user_logins)} пользователей с куками")
        
        print(f"⚙️ Режим: {'скрытый' if self.headless else 'видимый'}")
        print(f"⚡ Быстрый режим: {'включен' if self.fast_mode else 'отключен'}")
        print(f"🔄 Параллельность: {max_parallel} потоков")
        print("=" * 70)
        
        results = {
            'success': True,
            'total_users': len(user_logins),
            'auth_success': 0,
            'auth_failed': 0,
            'errors': 0,
            'user_results': [],
            'start_time': datetime.now().isoformat(),
            'duration_seconds': 0
        }
        
        start_time = time.time()
        
        # Последовательная проверка (если один пользователь или headless=False)
        if len(user_logins) == 1 or not self.headless:
            for i, user_login in enumerate(user_logins, 1):
                print(f"\n🧪 Тест {i}/{len(user_logins)}: {user_login}")
                result = self.test_single_user_cookies(user_login)
                self._print_user_result(result)
                results['user_results'].append(result)
                self._update_counters(results, result)
        
        # Параллельная проверка (только в headless режиме)
        else:
            print(f"\n🔄 Параллельная проверка {len(user_logins)} пользователей...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as executor:
                future_to_user = {
                    executor.submit(self.test_single_user_cookies, user_login): user_login 
                    for user_login in user_logins
                }
                
                completed = 0
                for future in concurrent.futures.as_completed(future_to_user):
                    user_login = future_to_user[future]
                    completed += 1
                    
                    print(f"✅ Завершен {completed}/{len(user_logins)}: {user_login}")
                    
                    try:
                        result = future.result()
                        results['user_results'].append(result)
                        self._update_counters(results, result)
                    except Exception as e:
                        error_result = {
                            'user_login': user_login,
                            'success': False,
                            'error': str(e)
                        }
                        results['user_results'].append(error_result)
                        results['errors'] += 1
        
        results['duration_seconds'] = round(time.time() - start_time, 2)
        
        # Выводим итоговый отчет
        self._print_summary_report(results)
        
        return results
    
    def _print_user_result(self, result: Dict[str, Any]) -> None:
        """Выводит результат проверки одного пользователя."""
        user_login = result['user_login']
        
        if not result['success']:
            print(f"   ❌ ОШИБКА: {result.get('error', 'Неизвестная ошибка')}")
            return
        
        if not result['cookies_loaded']:
            print(f"   ❌ Куки не загружены")
            return
        
        print(f"   🍪 Куки: {result['cookies_count']} шт.")
        print(f"   🌐 URL: {result['current_url']}")
        print(f"   📄 Заголовок: {result['page_title']}")
        
        if result['auth_confirmed']:
            if result['nickname_found']:
                print(f"   ✅ АВТОРИЗОВАН - никнейм: '{result['nickname_found']}'")
            else:
                print(f"   ✅ АВТОРИЗОВАН - по индикаторам")
        else:
            print(f"   ❌ НЕ АВТОРИЗОВАН")
        
        print(f"   ⏱️ Время: {result['duration_seconds']}с")
    
    def _update_counters(self, results: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Обновляет счетчики результатов."""
        if not result['success']:
            results['errors'] += 1
        elif result['auth_confirmed']:
            results['auth_success'] += 1
        else:
            results['auth_failed'] += 1
    
    def _print_summary_report(self, results: Dict[str, Any]) -> None:
        """Выводит итоговый отчет."""
        print("\n" + "=" * 70)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 70)
        print(f"👥 Всего пользователей: {results['total_users']}")
        print(f"✅ Успешно авторизованы: {results['auth_success']}")
        print(f"❌ Не авторизованы: {results['auth_failed']}")
        print(f"🚫 Ошибки: {results['errors']}")
        print(f"⏱️ Общее время: {results['duration_seconds']}с")
        print(f"📅 Время проверки: {results['start_time']}")
        
        # Детальная разбивка
        if results['user_results']:
            print(f"\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:")
            
            # Успешно авторизованные
            auth_users = [r for r in results['user_results'] 
                         if r.get('success') and r.get('auth_confirmed')]
            if auth_users:
                print(f"\n✅ Авторизованные пользователи ({len(auth_users)}):")
                for result in auth_users:
                    nickname = f" ({result['nickname_found']})" if result.get('nickname_found') else ""
                    print(f"   • {result['user_login']}{nickname}")
            
            # Не авторизованные
            unauth_users = [r for r in results['user_results'] 
                           if r.get('success') and not r.get('auth_confirmed')]
            if unauth_users:
                print(f"\n❌ НЕ авторизованные пользователи ({len(unauth_users)}):")
                for result in unauth_users:
                    print(f"   • {result['user_login']} - {result.get('current_url', 'N/A')}")
            
            # Ошибки
            error_users = [r for r in results['user_results'] if not r.get('success')]
            if error_users:
                print(f"\n🚫 Ошибки ({len(error_users)}):")
                for result in error_users:
                    print(f"   • {result['user_login']}: {result.get('error', 'N/A')}")
        
        print("=" * 70)


def main():
    """Основная функция CLI скрипта."""
    parser = argparse.ArgumentParser(
        description="Массовая проверка авторизации пользователей через куки",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Обычная проверка всех пользователей
  python run_mass_cookie_test.py

  # Скрытый режим (headless)
  python run_mass_cookie_test.py --headless

  # Быстрая проверка без детального анализа
  python run_mass_cookie_test.py --fast

  # Параллельная проверка (быстрее)
  python run_mass_cookie_test.py --parallel --headless

  # Проверка конкретного пользователя
  python run_mass_cookie_test.py --user admin

  # Все опции вместе
  python run_mass_cookie_test.py --headless --fast --parallel --user admin
        """
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Запуск браузера в скрытом режиме (рекомендуется для массовых проверок)"
    )
    
    parser.add_argument(
        "--fast",
        action="store_true", 
        help="Быстрый режим: менее детальные проверки, быстрее работает"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Параллельная проверка нескольких пользователей (только с --headless)"
    )
    
    parser.add_argument(
        "--user",
        type=str,
        help="Проверить только конкретного пользователя (например: admin)"
    )
    
    parser.add_argument(
        "--threads",
        type=int,
        default=3,
        help="Количество параллельных потоков (по умолчанию: 3)"
    )
    
    args = parser.parse_args()
    
    # Проверяем ограничения
    if args.parallel and not args.headless:
        print("⚠️ Параллельный режим требует --headless. Включаем headless режим.")
        args.headless = True
    
    # Создаем тестер
    tester = MassCookieAuthTester(
        headless=args.headless,
        fast_mode=args.fast
    )
    
    # Запускаем проверку
    try:
        if args.parallel and not args.user:
            results = tester.test_all_users(
                specific_user=args.user,
                max_parallel=args.threads
            )
        else:
            results = tester.test_all_users(specific_user=args.user)
        
        # Определяем код выхода
        if results['success'] and results['errors'] == 0:
            sys.exit(0)  # Успех
        else:
            sys.exit(1)  # Есть ошибки
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Проверка прервана пользователем")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
