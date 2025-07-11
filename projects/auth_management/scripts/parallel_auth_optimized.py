#!/usr/bin/env python3
"""
Оптимизированный скрипт для параллельной авторизации пользователей.

Ключевые улучшения:
- Использует ThreadPoolExecutor вместо subprocess'ов
- Интеграция с существующим UserManager и AuthService
- Детальный прогресс в реальном времени
- Оптимизированное управление ресурсами браузера
- Потокобезопасный вывод
"""
import argparse
import concurrent.futures
import csv
import json
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.logger import setup_logger
from src.user_manager import UserManager
from src.auth import AuthService


class ThreadSafeProgress:
    """Потокобезопасный прогресс-индикатор."""
    
    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.lock = threading.Lock()
        
    def update(self, username: str, success: bool, message: str = ""):
        """Обновляет прогресс с детальной информацией."""
        with self.lock:
            self.completed += 1
            status = "✅" if success else "❌"
            progress_percent = (self.completed / self.total) * 100
            
            print(f"[{self.completed:3d}/{self.total:3d}] {progress_percent:5.1f}% {status} {username:20s} {message}")


class OptimizedParallelAuthManager:
    """
    Оптимизированный менеджер параллельной авторизации.
    
    Использует:
    - ThreadPoolExecutor для управления потоками
    - Один экземпляр UserManager для всех операций
    - Отдельные экземпляры AuthService для каждого потока
    - Потокобезопасный прогресс-индикатор
    """
    
    def __init__(self, max_workers: int = 5, verbose: bool = True, db_path: Optional[str] = None):
        """
        Инициализирует оптимизированный менеджер авторизации.
        
        Args:
            max_workers: Максимальное количество потоков
            verbose: Выводить ли детальную информацию
            db_path: Путь к базе данных (опционально)
        """
        self.max_workers = max_workers
        self.verbose = verbose
        self.logger = setup_logger(__name__)
        
        # Инициализируем UserManager (потокобезопасный)
        self.user_manager = UserManager(db_path)
        
        # Статистика
        self.start_time = None
        self.end_time = None
        self.results = {
            'successful': [],
            'failed': [],
            'errors': []
        }
        
    def load_users_from_csv(self, csv_path: str) -> List[Dict[str, str]]:
        """
        Загружает пользователей из CSV файла.
        
        Args:
            csv_path: Путь к CSV файлу
            
        Returns:
            Список пользователей
        """
        users = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    username = row.get('username') or row.get('login')
                    password = row.get('password')
                    role = row.get('role', 'user')
                    
                    if username and password:
                        users.append({
                            'username': username,
                            'login': username,  # Для совместимости
                            'password': password,
                            'role': role
                        })
                    else:
                        self.logger.warning(f"Пропущена строка без логина/пароля: {row}")
                        
            self.logger.info(f"Загружено {len(users)} пользователей из {csv_path}")
            return users
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки пользователей: {e}")
            return []
    
    def authenticate_user(self, user_data: Dict[str, str], headless: bool, force_reauth: bool, 
                         progress: ThreadSafeProgress) -> Dict[str, Any]:
        """
        Авторизует одного пользователя в отдельном потоке.
        
        Args:
            user_data: Данные пользователя
            headless: Запускать браузер в headless режиме
            force_reauth: Принудительная переавторизация
            progress: Объект для отслеживания прогресса
            
        Returns:
            Результат авторизации
        """
        username = user_data['username']
        password = user_data['password']
        role = user_data['role']
        
        thread_id = threading.current_thread().ident
        start_time = time.time()
        
        try:
            # Добавляем пользователя если его нет
            if not self.user_manager.get_user(login=username):
                self.user_manager.add_user(username, password, role)
                if self.verbose:
                    progress.update(username, True, f"[T{thread_id}] Пользователь добавлен в БД")
            
            # Проверяем, нужна ли переавторизация
            user_db_data = self.user_manager.get_user(login=username)
            need_auth = force_reauth or not user_db_data.get('cookie') or not self.user_manager.is_cookie_valid(str(user_db_data['id']))
            
            if not need_auth:
                progress.update(username, True, f"[T{thread_id}] Уже авторизован (куки валидны)")
                return {
                    'username': username,
                    'success': True,
                    'action': 'skipped_valid_cookie',
                    'execution_time': time.time() - start_time,
                    'thread_id': thread_id
                }
            
            # Создаем AuthService для этого потока
            auth_service = AuthService(headless=headless)
            
            try:
                if force_reauth:
                    progress.update(username, True, f"[T{thread_id}] Принудительная переавторизация...")
                else:
                    progress.update(username, True, f"[T{thread_id}] Авторизация...")
                
                # Выполняем авторизацию
                auth_result = auth_service.authenticate(username, password)
                
                if auth_result and auth_result.get('success'):
                    # Сохраняем куки в базу данных
                    cookies = auth_result.get('cookies')
                    if cookies:
                        self.user_manager.save_user_cookie(str(user_db_data['id']), cookies)
                        progress.update(username, True, f"[T{thread_id}] ✅ Авторизован и куки сохранены")
                        
                        return {
                            'username': username,
                            'success': True,
                            'action': 'authenticated',
                            'execution_time': time.time() - start_time,
                            'thread_id': thread_id,
                            'cookies_count': len(cookies) if isinstance(cookies, list) else 1
                        }
                    else:
                        progress.update(username, False, f"[T{thread_id}] ❌ Авторизация прошла, но куки не получены")
                        return {
                            'username': username,
                            'success': False,
                            'action': 'no_cookies',
                            'error': 'Куки не получены после авторизации',
                            'execution_time': time.time() - start_time,
                            'thread_id': thread_id
                        }
                else:
                    error_msg = auth_result.get('error', 'Неизвестная ошибка') if auth_result else 'Авторизация не удалась'
                    progress.update(username, False, f"[T{thread_id}] ❌ {error_msg}")
                    return {
                        'username': username,
                        'success': False,
                        'action': 'auth_failed',
                        'error': error_msg,
                        'execution_time': time.time() - start_time,
                        'thread_id': thread_id
                    }
                    
            finally:
                # Обязательно закрываем AuthService
                try:
                    auth_service.close()
                except:
                    pass
                    
        except Exception as e:
            error_msg = f"Исключение при авторизации: {e}"
            progress.update(username, False, f"[T{thread_id}] 💥 {error_msg}")
            return {
                'username': username,
                'success': False,
                'action': 'exception',
                'error': error_msg,
                'execution_time': time.time() - start_time,
                'thread_id': thread_id
            }
    
    def run_parallel_auth(self, csv_path: str, headless: bool = True, 
                         force_reauth: bool = False) -> Dict[str, Any]:
        """
        Запускает оптимизированную параллельную авторизацию.
        
        Args:
            csv_path: Путь к CSV файлу с пользователями
            headless: Запускать браузер в headless режиме
            force_reauth: Принудительная переавторизация
            
        Returns:
            Детальные результаты выполнения
        """
        self.start_time = time.time()
        
        print("=" * 80)
        print("🚀 ОПТИМИЗИРОВАННАЯ ПАРАЛЛЕЛЬНАЯ АВТОРИЗАЦИЯ")
        print("=" * 80)
        print(f"📁 CSV файл: {csv_path}")
        print(f"🧵 Количество потоков: {self.max_workers}")
        print(f"🖥️  Headless режим: {headless}")
        print(f"🔄 Принудительная переавторизация: {force_reauth}")
        print("=" * 80)
        
        # Загружаем пользователей
        users = self.load_users_from_csv(csv_path)
        if not users:
            return {'error': 'Не удалось загрузить пользователей'}
        
        total_users = len(users)
        print(f"👥 Загружено пользователей: {total_users}")
        print(f"⏳ Ожидается время выполнения: ~{(total_users * 3) // self.max_workers}с")
        print("-" * 80)
        
        # Создаем прогресс-индикатор
        progress = ThreadSafeProgress(total_users)
        
        # Запускаем параллельную обработку
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Отправляем задачи
            future_to_user = {}
            for user in users:
                future = executor.submit(
                    self.authenticate_user,
                    user,
                    headless,
                    force_reauth,
                    progress
                )
                future_to_user[future] = user['username']
            
            # Собираем результаты
            for future in concurrent.futures.as_completed(future_to_user):
                username = future_to_user[future]
                try:
                    result = future.result()
                    if result['success']:
                        self.results['successful'].append(result)
                    else:
                        self.results['failed'].append(result)
                        
                except Exception as e:
                    error_result = {
                        'username': username,
                        'success': False,
                        'error': f"Ошибка получения результата: {e}",
                        'thread_id': None
                    }
                    self.results['errors'].append(error_result)
                    self.logger.error(f"Ошибка получения результата для {username}: {e}")
        
        self.end_time = time.time()
        
        # Генерируем итоговый отчет
        return self._generate_final_report()
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """
        Генерирует детальный итоговый отчет.
        
        Returns:
            Словарь с результатами
        """
        total_time = self.end_time - self.start_time
        total_users = len(self.results['successful']) + len(self.results['failed']) + len(self.results['errors'])
        
        # Подсчет статистики по действиям
        action_stats = {}
        for result in self.results['successful'] + self.results['failed']:
            action = result.get('action', 'unknown')
            action_stats[action] = action_stats.get(action, 0) + 1
        
        # Средние времена выполнения
        execution_times = [r.get('execution_time', 0) for r in self.results['successful'] + self.results['failed']]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            'summary': {
                'total_users': total_users,
                'successful': len(self.results['successful']),
                'failed': len(self.results['failed']),
                'errors': len(self.results['errors']),
                'success_rate': (len(self.results['successful']) / total_users * 100) if total_users > 0 else 0,
                'total_execution_time': total_time,
                'average_time_per_user': avg_time,
                'users_per_second': total_users / total_time if total_time > 0 else 0
            },
            'action_statistics': action_stats,
            'results': {
                'successful': self.results['successful'],
                'failed': self.results['failed'],
                'errors': self.results['errors']
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def print_final_report(self, report: Dict[str, Any]) -> None:
        """
        Выводит красиво отформатированный итоговый отчет.
        
        Args:
            report: Отчет о выполнении
        """
        print("\n" + "=" * 80)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ОПТИМИЗИРОВАННОЙ ПАРАЛЛЕЛЬНОЙ АВТОРИЗАЦИИ")
        print("=" * 80)
        
        summary = report['summary']
        print(f"👥 Всего пользователей: {summary['total_users']}")
        print(f"✅ Успешно: {summary['successful']} ({summary['success_rate']:.1f}%)")
        print(f"❌ Неудачно: {summary['failed']}")
        print(f"💥 Ошибки: {summary['errors']}")
        print(f"⏱️  Общее время: {summary['total_execution_time']:.2f}с")
        print(f"📈 Среднее время на пользователя: {summary['average_time_per_user']:.2f}с")
        print(f"🚀 Пользователей в секунду: {summary['users_per_second']:.2f}")
        
        if report['action_statistics']:
            print(f"\n📋 СТАТИСТИКА ПО ДЕЙСТВИЯМ:")
            for action, count in report['action_statistics'].items():
                print(f"   {action}: {count}")
        
        if summary['failed'] > 0 and self.verbose:
            print(f"\n❌ ДЕТАЛИ НЕУДАЧНЫХ АВТОРИЗАЦИЙ:")
            for result in report['results']['failed'][:10]:  # Показываем только первые 10
                print(f"   {result['username']}: {result.get('error', 'Неизвестная ошибка')}")
            if len(report['results']['failed']) > 10:
                print(f"   ... и еще {len(report['results']['failed']) - 10} пользователей")


def parse_arguments():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Оптимизированная параллельная авторизация пользователей из CSV файла",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s "D:/Bll_tests/secrets/bulk_users.csv" --threads 10 --headless
  %(prog)s "D:/Bll_tests/secrets/bulk_users.csv" --threads 3 --relogin
  %(prog)s "D:/Bll_tests/secrets/bulk_users.csv" --threads 5 --headless --relogin --quiet
        """
    )
    
    parser.add_argument(
        "csv_path",
        help="Путь к CSV файлу с пользователями (обязательные поля: login/username, password)"
    )
    
    parser.add_argument(
        "--threads",
        type=int,
        default=5,
        help="Количество потоков (по умолчанию: 5, рекомендуется: 3-10)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Запускать браузер в headless режиме (быстрее, но без визуального контроля)"
    )
    
    parser.add_argument(
        "--relogin",
        action="store_true",
        help="Принудительно переавторизовать всех пользователей (игнорировать существующие куки)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Тихий режим (минимальный вывод, только финальная статистика)"
    )
    
    parser.add_argument(
        "--db",
        dest="db_path",
        help="Путь к базе данных SQLite (опционально)"
    )
    
    return parser.parse_args()


def main():
    """Основная функция."""
    args = parse_arguments()
    
    # Проверяем существование CSV файла
    if not Path(args.csv_path).exists():
        print(f"❌ Файл не найден: {args.csv_path}")
        sys.exit(1)
    
    # Проверяем разумность количества потоков
    if args.threads < 1:
        print(f"❌ Количество потоков должно быть больше 0")
        sys.exit(1)
    elif args.threads > 20:
        print(f"⚠️  Предупреждение: большое количество потоков ({args.threads}) может перегрузить систему")
        response = input("Продолжить? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Создаем оптимизированный менеджер
    manager = OptimizedParallelAuthManager(
        max_workers=args.threads,
        verbose=not args.quiet,
        db_path=args.db_path
    )
    
    try:
        # Запускаем параллельную авторизацию
        report = manager.run_parallel_auth(
            csv_path=args.csv_path,
            headless=args.headless,
            force_reauth=args.relogin
        )
        
        # Проверяем на ошибки загрузки
        if 'error' in report:
            print(f"❌ Ошибка: {report['error']}")
            sys.exit(1)
        
        # Выводим отчет
        if not args.quiet:
            manager.print_final_report(report)
        
        # Сохраняем детальный отчет в JSON
        logs_dir = project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        report_file = logs_dir / f"optimized_auth_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Детальный отчет сохранен: {report_file}")
        
        # Определяем код выхода
        summary = report['summary']
        if summary['errors'] > 0:
            print(f"⚠️  Завершено с ошибками")
            sys.exit(2)
        elif summary['failed'] > 0:
            print(f"⚠️  Завершено с неудачными авторизациями")
            sys.exit(1)
        else:
            print(f"✅ Все пользователи успешно авторизованы!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print(f"\n❌ Выполнение прервано пользователем")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
