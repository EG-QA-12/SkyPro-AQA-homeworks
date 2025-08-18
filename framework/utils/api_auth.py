"""
Модуль для API авторизации пользователей через HTTP запросы.

Предоставляет функции для быстрой массовой авторизации без использования браузера,
обходя антибот защиту и обеспечивая максимальную производительность.
Поддерживает параллельную обработку для еще большей скорости.
"""
from __future__ import annotations

import requests
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .cookie_constants import COOKIE_NAME
from .auth_utils import save_cookie

# Настройка логирования
logger = logging.getLogger(__name__)

# Блокировка для thread-safe операций
_file_lock = threading.Lock()
_print_lock = threading.Lock()


@dataclass
class AuthResult:
    """Результат API авторизации."""
    success: bool
    username: str
    cookies: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    response_status: Optional[int] = None
    session_token: Optional[str] = None


def thread_safe_print(*args, **kwargs):
    """Thread-safe версия print для параллельного выполнения."""
    with _print_lock:
        print(*args, **kwargs)


class APIAuthManager:
    """
    Менеджер для API авторизации пользователей.
    
    Обеспечивает быструю и надежную авторизацию через HTTP запросы,
    минуя проблемы браузерной автоматизации и антибот защиты.
    Поддерживает параллельную обработку для максимальной производительности.
    """
    
    def __init__(self, base_url: str = "https://ca.bll.by"):
        """
        Инициализация API менеджера.
        
        Args:
            base_url: Базовый URL сайта для авторизации
        """
        self.base_url = base_url.rstrip('/')
        self.login_endpoint = f"{self.base_url}/login"
        
        # Настройка таймаутов
        self.timeout = 30
        
        logger.info(f"Инициализирован APIAuthManager для {self.base_url}")
    
    def _create_session(self) -> requests.Session:
        """
        Создает новую сессию с настроенными заголовками.
        
        Каждый поток должен иметь свою сессию для thread safety.
        """
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': self.base_url,
            'Referer': f"{self.base_url}/login"
        })
        return session
    
    def login_user(self, username: str, password: str, user_index: int = 0, total_users: int = 1) -> AuthResult:
        """
        Авторизация одного пользователя через API.
        
        Args:
            username: Логин пользователя
            password: Пароль пользователя
            user_index: Индекс пользователя для отображения прогресса
            total_users: Общее количество пользователей
            
        Returns:
            AuthResult: Результат авторизации с куками и статусом
        """
        session = self._create_session()
        
        try:
            logger.info(f"Начинаем API авторизацию для пользователя: {username}")
            
            # Подготовка данных для POST запроса
            login_data = {
                'lgn': username,
                'password': password,
                'remember': '1'
            }
            
            # Выполнение POST запроса
            logger.debug(f"Отправляем POST запрос к {self.login_endpoint}")
            response = session.post(
                self.login_endpoint,
                data=login_data,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            logger.debug(f"Получен ответ: статус {response.status_code}")
            
            # Проверка успешности авторизации
            if response.status_code == 200:
                # Извлекаем куки из ответа
                session_cookies = self._extract_cookies(response)
                
                if session_cookies is not None and COOKIE_NAME in session_cookies:
                    session_token = session_cookies[COOKIE_NAME]['value']
                    logger.info(f"✅ API авторизация успешна для {username}")
                    
                    return AuthResult(
                        success=True,
                        username=username,
                        cookies=session_cookies,
                        response_status=response.status_code,
                        session_token=session_token
                    )
                else:
                    logger.warning(f"❌ Кука {COOKIE_NAME} не найдена в ответе для {username}")
                    return AuthResult(
                        success=False,
                        username=username,
                        error_message=f"Кука {COOKIE_NAME} не найдена в ответе",
                        response_status=response.status_code
                    )
            else:
                logger.error(f"❌ API авторизация неудачна для {username}: статус {response.status_code}")
                return AuthResult(
                    success=False,
                    username=username,
                    error_message=f"HTTP статус {response.status_code}",
                    response_status=response.status_code
                )
                
        except requests.exceptions.Timeout:
            error_msg = f"Таймаут при авторизации {username}"
            logger.error(f"❌ {error_msg}")
            return AuthResult(
                success=False,
                username=username,
                error_message=error_msg
            )
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка сети при авторизации {username}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return AuthResult(
                success=False,
                username=username,
                error_message=error_msg
            )
            
        except Exception as e:
            error_msg = f"Неожиданная ошибка при авторизации {username}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return AuthResult(
                success=False,
                username=username,
                error_message=error_msg
            )
        finally:
            session.close()
    
    def _extract_cookies(self, response: requests.Response) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Извлекает куки из HTTP ответа.
        """
        try:
            cookies_dict = {}
            
            for cookie in response.cookies:
                cookie_data = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain or '.bll.by',
                    'path': cookie.path or '/',
                    'secure': cookie.secure,
                    'httpOnly': getattr(cookie, 'httpOnly', False),
                    'sameSite': 'Lax'
                }
                
                # Добавляем expires если есть
                if hasattr(cookie, 'expires') and cookie.expires:
                    cookie_data['expires'] = cookie.expires
                
                cookies_dict[cookie.name] = cookie_data
                logger.debug(f"Извлечена кука: {cookie.name}")
            
            return cookies_dict if cookies_dict else None
            
        except Exception as e:
            logger.error(f"Ошибка при извлечении кук: {str(e)}")
            return None
    
    def _process_single_user(self, user_data: Tuple[int, Dict[str, str], int, bool, bool]) -> AuthResult:
        """
        Обрабатывает одного пользователя в отдельном потоке.
        
        Args:
            user_data: Кортеж (индекс, данные_пользователя, общее_количество, сохранять_файлы, обновлять_БД)
            
        Returns:
            AuthResult: Результат авторизации
        """
        i, user, total_users, save_to_files, update_database = user_data
        username = user.get('login', user.get('name', f'user_{i}'))
        password = user.get('password', '')
        
        thread_safe_print(f"📡 [{i}/{total_users}] API авторизация: {username}")
        
        # Выполняем авторизацию
        auth_result = self.login_user(username, password, i, total_users)
        
        if auth_result.success:
            thread_safe_print(f"   ✅ {username}: Успешно авторизован через API")
            
            # Сохраняем куки в файл (thread-safe)
            if save_to_files and auth_result.cookies:
                try:
                    cookie_file = f"cookies/{username}_cookies.json"
                    with _file_lock:
                        self._save_cookies_to_file(auth_result.cookies, cookie_file)
                    thread_safe_print(f"   💾 {username}: Куки сохранены в файл: {cookie_file}")
                except Exception as e:
                    logger.error(f"Ошибка сохранения кук для {username}: {str(e)}")
            
            # Обновляем базу данных (thread-safe)
            if update_database and auth_result.session_token:
                try:
                    with _file_lock:
                        # Для API режима пропускаем обновление БД (нужны дополнительные параметры)
                        pass
                    thread_safe_print(f"   ℹ️  {username}: БД обновление пропущено (API режим)")
                except Exception as e:
                    logger.error(f"Ошибка обновления БД для {username}: {str(e)}")
                    
        else:
            thread_safe_print(f"   ❌ {username}: Ошибка - {auth_result.error_message}")
        
        return auth_result
    
    def mass_authorize_users(self, users: List[Dict[str, str]], save_to_files: bool = True, 
                           update_database: bool = True, max_workers: int = 5) -> Tuple[List[AuthResult], Dict[str, Any]]:
        """
        Массовая авторизация списка пользователей через API с параллельной обработкой.
        
        Args:
            users: Список пользователей с ключами 'login', 'password', 'name'
            save_to_files: Сохранять ли куки в файлы
            update_database: Обновлять ли информацию в базе данных
            max_workers: Максимальное количество потоков (по умолчанию 5)
            
        Returns:
            Tuple[List[AuthResult], Dict[str, Any]]: Результаты авторизации и статистика
        """
        logger.info(f"🚀 Начинаем параллельную API авторизацию {len(users)} пользователей в {max_workers} потоков")
        
        results = []
        start_time = time.time()
        
        # Подготавливаем данные для параллельной обработки
        user_tasks = [
            (i + 1, user, len(users), save_to_files, update_database)
            for i, user in enumerate(users)
        ]
        
        # Выполняем параллельную обработку
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Отправляем все задачи
            future_to_user = {
                executor.submit(self._process_single_user, user_data): user_data[1]
                for user_data in user_tasks
            }
            
            # Собираем результаты по мере завершения
            for future in as_completed(future_to_user):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    user = future_to_user[future]
                    username = user.get('login', user.get('name', 'unknown'))
                    logger.error(f"Ошибка обработки пользователя {username}: {str(e)}")
                    results.append(AuthResult(
                        success=False,
                        username=username,
                        error_message=f"Ошибка потока: {str(e)}"
                    ))
        
        elapsed_time = time.time() - start_time
        
        # Подсчет статистики
        successful_auths = sum(1 for r in results if r.success)
        failed_auths = len(results) - successful_auths
        
        # Статистика выполнения
        stats = {
            'total_users': len(users),
            'successful': successful_auths,
            'failed': failed_auths,
            'success_rate': (successful_auths / len(users)) * 100 if users else 0,
            'elapsed_time': elapsed_time,
            'avg_time_per_user': elapsed_time / len(users) if users else 0,
            'threads_used': max_workers,
            'throughput': len(users) / elapsed_time if elapsed_time > 0 else 0
        }
        
        # Вывод итоговой статистики
        thread_safe_print("\n" + "="*80)
        thread_safe_print("📊 СТАТИСТИКА ПАРАЛЛЕЛЬНОЙ API АВТОРИЗАЦИИ")
        thread_safe_print("="*80)
        thread_safe_print(f"👥 Всего пользователей: {stats['total_users']}")
        thread_safe_print(f"✅ Успешно авторизовано: {stats['successful']}")
        thread_safe_print(f"❌ Неудачных авторизаций: {stats['failed']}")
        thread_safe_print(f"📈 Процент успеха: {stats['success_rate']:.1f}%")
        thread_safe_print(f"⏱️  Общее время: {stats['elapsed_time']:.2f} сек")
        thread_safe_print(f"⚡ Среднее время на пользователя: {stats['avg_time_per_user']:.2f} сек")
        thread_safe_print(f"🔄 Потоков использовано: {stats['threads_used']}")
        thread_safe_print(f"🚀 Пропускная способность: {stats['throughput']:.2f} пользователей/сек")
        thread_safe_print("="*80)
        
        logger.info(f"Параллельная авторизация завершена: {successful_auths}/{len(users)} успешно")
        
        return results, stats
    
    def _save_cookies_to_file(self, cookies: Dict[str, Dict[str, Any]], file_path: str) -> None:
        """
        Сохраняет куки в файл в формате совместимом с Playwright.
        
        ВАЖНО: Дополнительная фильтрация для сохранения только авторизационной куки.
        
        Args:
            cookies: Словарь с куками
            file_path: Путь к файлу для сохранения
        """
        try:
            # Дополнительная фильтрация больше не нужна здесь, т.к. _extract_cookies
            # теперь возвращает все куки. Сохраняем все, что получили.
            playwright_cookies = list(cookies.values())
            
            # Создаем директорию если не существует
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Сохраняем в JSON файл
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(playwright_cookies, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Сохранено {len(playwright_cookies)} авторизационных кук в {file_path}")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения кук в файл {file_path}: {str(e)}")
            raise
    
    def close(self) -> None:
        """Закрывает сессию и освобождает ресурсы."""
        logger.info("API сессии закрыты")


def api_mass_auth(users: List[Dict[str, str]], save_files: bool = True, 
                  update_db: bool = True, threads: int = 5) -> Tuple[List[AuthResult], Dict[str, Any]]:
    """
    Функция-обертка для быстрой параллельной массовой API авторизации.
    
    Args:
        users: Список пользователей для авторизации
        save_files: Сохранять ли куки в файлы
        update_db: Обновлять ли базу данных
        threads: Количество параллельных потоков (по умолчанию 5)
        
    Returns:
        Результаты авторизации и статистика
    """
    auth_manager = APIAuthManager()
    try:
        return auth_manager.mass_authorize_users(users, save_files, update_db, threads)
    finally:
        auth_manager.close()


if __name__ == "__main__":
    print("Модуль параллельной API авторизации для быстрой массовой авторизации пользователей")
    print("Использование:")
    print("from framework.utils.api_auth import api_mass_auth")
    print("results, stats = api_mass_auth(users_list, threads=5)") 