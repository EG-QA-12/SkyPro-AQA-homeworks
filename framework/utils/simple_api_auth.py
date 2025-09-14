"""
Простая API авторизация для массовой авторизации пользователей.

Этот модуль предоставляет минимальную, но эффективную реализацию
API авторизации через HTTP запросы без использования браузера.
Подходит для новичков и простых сценариев использования.

Основные функции:
- api_login() - авторизация одного пользователя
- mass_api_auth() - массовая авторизация с сохранением кук
- save_user_cookies() - сохранение кук в файлы
"""

import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы
BASE_URL = "https://ca.bll.by"
LOGIN_ENDPOINT = f"{BASE_URL}/login"
COOKIE_NAME = "test_joint_session"
DEFAULT_TIMEOUT = 30


def api_login(username: str, password: str) -> Dict[str, Any]:
    """
    Простая авторизация пользователя через API.
    
    Args:
        username: Логин пользователя
        password: Пароль пользователя
        
    Returns:
        Словарь с результатом авторизации:
        {
            'success': bool,
            'username': str,
            'cookies': dict или None,
            'error': str или None
        }
    """
    logger.info(f"Авторизация пользователя: {username}")
    
    try:
        # Создаем сессию с реалистичными заголовками
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f"{BASE_URL}/login"
        })
        
        # Данные для авторизации
        login_data = {
            'lgn': username,
            'password': password,
            'remember': '1'
        }
        
        # Отправляем POST запрос
        response = session.post(
            LOGIN_ENDPOINT,
            data=login_data,
            timeout=DEFAULT_TIMEOUT,
            allow_redirects=True
        )
        
        # Проверяем успешность
        if response.status_code == 200:
            # Ищем нужную куку
            auth_cookies = {}
            for cookie in response.cookies:
                if cookie.name == COOKIE_NAME:
                    auth_cookies[cookie.name] = {
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain or '.bll.by',
                        'path': cookie.path or '/',
                        'secure': cookie.secure,
                        'httpOnly': getattr(cookie, 'httpOnly', False),
                        'sameSite': 'Lax'
                    }
                    break
            
            if auth_cookies:
                logger.info(f"✅ Успешная авторизация: {username}")
                return {
                    'success': True,
                    'username': username,
                    'cookies': auth_cookies,
                    'error': None
                }
            else:
                logger.warning(f"❌ Кука не найдена: {username}")
                return {
                    'success': False,
                    'username': username,
                    'cookies': None,
                    'error': 'Кука авторизации не найдена'
                }
        else:
            logger.error(f"❌ Ошибка авторизации {username}: {response.status_code}")
            return {
                'success': False,
                'username': username,
                'cookies': None,
                'error': f'HTTP {response.status_code}'
            }
            
    except Exception as e:
        logger.error(f"❌ Ошибка авторизации {username}: {str(e)}")
        return {
            'success': False,
            'username': username,
            'cookies': None,
            'error': str(e)
        }


def save_user_cookies(cookies: Dict[str, Any], username: str) -> bool:
    """
    Сохраняет куки пользователя в файл.
    
    Args:
        cookies: Словарь с куками
        username: Имя пользователя
        
    Returns:
        True если успешно сохранено
    """
    try:
        # Создаем директорию если не существует
        cookies_dir = Path("cookies")
        cookies_dir.mkdir(exist_ok=True)
        
        # Формируем путь к файлу
        file_path = cookies_dir / f"{username}_cookies.json"
        
        # Конвертируем в формат Playwright
        playwright_cookies = list(cookies.values())
        
        # Сохраняем в файл
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(playwright_cookies, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Куки сохранены: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения кук {username}: {str(e)}")
        return False


def _process_user(user_data: Tuple[int, Dict[str, str], int]) -> Dict[str, Any]:
    """
    Обрабатывает одного пользователя (для параллельной обработки).
    
    Args:
        user_data: (индекс, пользователь, всего_пользователей)
        
    Returns:
        Результат авторизации
    """
    index, user, total = user_data
    username = user.get('login', f'user_{index}')
    password = user.get('password', '')
    
    print(f"[{index}/{total}] Авторизация: {username}")
    
    # Авторизуем пользователя
    result = api_login(username, password)
    
    # Если успешно - сохраняем куки
    if result['success'] and result['cookies']:
        save_user_cookies(result['cookies'], username)
        print(f"   ✅ {username}: успешно")
    else:
        print(f"   ❌ {username}: {result['error']}")
    
    return result


def mass_api_auth(users: List[Dict[str, str]], threads: int = 5) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Массовая API авторизация пользователей.
    
    Args:
        users: Список пользователей с ключами 'login' и 'password'
        threads: Количество параллельных потоков
        
    Returns:
        (результаты, статистика)
    """
    logger.info(f"🚀 Начинаем массовую авторизацию {len(users)} пользователей")
    
    start_time = time.time()
    results = []
    
    # Подготавливаем данные для обработки
    user_tasks = [(i + 1, user, len(users)) for i, user in enumerate(users)]
    
    # Параллельная обработка
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(_process_user, user_tasks))
    
    # Считаем статистику
    elapsed_time = time.time() - start_time
    successful = sum(1 for r in results if r['success'])
    
    stats = {
        'total': len(users),
        'successful': successful,
        'failed': len(users) - successful,
        'success_rate': (successful / len(users)) * 100 if users else 0,
        'elapsed_time': elapsed_time,
        'threads': threads
    }
    
    # Выводим итоги
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ АВТОРИЗАЦИИ")
    print("="*50)
    print(f"Всего пользователей: {stats['total']}")
    print(f"Успешно: {stats['successful']}")
    print(f"Ошибок: {stats['failed']}")
    print(f"Процент успеха: {stats['success_rate']:.1f}%")
    print(f"Время выполнения: {stats['elapsed_time']:.2f} сек")
    print("="*50)
    
    logger.info(f"Массовая авторизация завершена: {successful}/{len(users)} успешно")
    
    return results, stats


# Простой пример использования
if __name__ == "__main__":
    print("Простая API авторизация")
    print("Использование:")
    print("from framework.utils.simple_api_auth import mass_api_auth")
    print("results, stats = mass_api_auth(users_list)")
