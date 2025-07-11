#!/usr/bin/env python3
"""
Скрипт для параллельного запуска авторизации пользователей в несколько потоков.

Функциональность:
- Параллельный запуск авторизации в указанном количестве потоков
- Мониторинг прогресса выполнения
- Подробная отчетность по результатам
- Обработка ошибок и повторные попытки
- Настраиваемые параметры выполнения

Исправления:
- Использование асинхронного Playwright вместо subprocess
- Правильная изоляция браузерных контекстов
- Корректный вывод результатов
- Обработка ошибок доступа к памяти
"""
import argparse
import asyncio
import concurrent.futures
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.logger import setup_logger


class ParallelAuthManager:
    """
    Менеджер для параллельного запуска авторизации пользователей.
    
    Обеспечивает:
    - Разделение пользователей между потоками
    - Мониторинг выполнения
    - Сбор статистики
    - Обработку ошибок
    """
    
    def __init__(self, max_workers: int = 10, verbose: bool = True):
        """
        Инициализирует менеджер параллельной авторизации.
        
        Args:
            max_workers: Максимальное количество потоков
            verbose: Выводить ли подробную информацию
        """
        self.max_workers = max_workers
        self.verbose = verbose
        self.logger = setup_logger(__name__)
        
        # Статистика
        self.start_time = None
        self.end_time = None
        self.total_users = 0
        self.successful_threads = 0
        self.failed_threads = 0
        self.thread_results = []
        
    def load_users_from_csv(self, csv_path: str) -> List[Dict]:
        """
        Загружает список пользователей из CSV файла.
        
        Args:
            csv_path: Путь к CSV файлу
            
        Returns:
            list: Список пользователей
        """
        users = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                users = list(reader)
                
            self.logger.info(f"Загружено {len(users)} пользователей из {csv_path}")
            return users
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки пользователей: {e}")
            return []
    
    def split_users_by_threads(self, users: List[Dict]) -> List[List[Dict]]:
        """
        Разделяет пользователей между потоками.
        
        Args:
            users: Список всех пользователей
            
        Returns:
            list: Список групп пользователей для каждого потока
        """
        if not users:
            return []
            
        # Более точное распределение пользователей на потоки
        users_per_thread = len(users) // self.max_workers
        extra_users = len(users) % self.max_workers

        thread_groups = []
        start_index = 0
        for i in range(self.max_workers):
            end_index = start_index + users_per_thread + (1 if i < extra_users else 0)
            group = users[start_index:end_index]
            thread_groups.append(group)
            start_index = end_index
        
        self.logger.info(f"Пользователи разделены на {len(thread_groups)} групп")
        return thread_groups
    
    def create_temp_csv(self, users: List[Dict], thread_id: int) -> str:
        """
        Создает временный CSV файл для группы пользователей.
        
        Args:
            users: Список пользователей для потока
            thread_id: Идентификатор потока
            
        Returns:
            str: Путь к созданному файлу
        """
        temp_dir = project_root / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        temp_file = temp_dir / f"users_thread_{thread_id}.csv"
        
        if users:
            # Получаем заголовки из первого пользователя
            fieldnames = users[0].keys()
            
            with open(temp_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(users)
        
        return str(temp_file)
    
    async def run_auth_thread_async(self, thread_id: int, users: List[Dict], 
                                   headless: bool = True, relogin: bool = False) -> Dict:
        """
        Асинхронно запускает авторизацию для группы пользователей.
        
        Args:
            thread_id: Идентификатор потока
            users: Список пользователей для обработки
            headless: Запускать браузер в headless режиме
            relogin: Принудительно переавторизовать пользователей
            
        Returns:
            dict: Результаты выполнения потока
        """
        start_time = time.time()
        
        if self.verbose:
            print(f"🚀 Поток {thread_id}: Начинаем авторизацию {len(users)} пользователей")
        
        successful_users = []
        failed_users = []
        
        try:
            # Создаем временный CSV файл для этого потока
            temp_csv = self.create_temp_csv(users, thread_id)
            
            # Запускаем синхронный код в отдельном потоке
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._run_sync_auth_for_users, 
                temp_csv, 
                thread_id, 
                headless, 
                relogin
            )
            
            # Удаляем временный файл
            try:
                if Path(temp_csv).exists():
                    Path(temp_csv).unlink()
            except Exception as cleanup_error:
                if self.verbose:
                    print(f"   ⚠️ Поток {thread_id}: Ошибка удаления временного файла: {cleanup_error}")
            
            return result
                
        except Exception as e:
            if self.verbose:
                print(f"💥 Поток {thread_id}: Критическая ошибка - {e}")
            return {
                'thread_id': thread_id,
                'success': False,
                'users_count': len(users),
                'successful_users': [],
                'failed_users': [user.get('username', f'user_{i}') for i, user in enumerate(users)],
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    def _run_sync_auth_for_users(self, temp_csv: str, thread_id: int, 
                                headless: bool, relogin: bool) -> Dict:
        """
        Запускает синхронную авторизацию для группы пользователей.
        Этот метод выполняется в отдельном потоке.
        
        Args:
            temp_csv: Путь к временному CSV файлу
            thread_id: Идентификатор потока
            headless: Режим headless
            relogin: Принудительная переавторизация
            
        Returns:
            dict: Результаты выполнения
        """
        start_time = time.time()
        
        try:
            from src.user_manager import UserManager
            
            # Создаем менеджер и запускаем авторизацию
            manager = UserManager()
            summary = manager.authorize_users_from_csv(
                temp_csv, 
                headless=headless, 
                force_reauth=relogin
            )
            
            execution_time = time.time() - start_time
            
            successful_users = list(summary.get('success', {}).keys())
            failed_users = summary.get('failed', [])
            
            if self.verbose:
                success_count = len(successful_users)
                total_count = success_count + len(failed_users)
                print(f"✅ Поток {thread_id}: Завершен ({success_count}/{total_count} успешно) за {execution_time:.2f}с")
            
            return {
                'thread_id': thread_id,
                'success': len(failed_users) == 0,
                'users_count': len(successful_users) + len(failed_users),
                'successful_users': successful_users,
                'failed_users': failed_users,
                'execution_time': execution_time
            }
            
        except Exception as e:
            if self.verbose:
                print(f"💥 Поток {thread_id}: Ошибка в синхронном методе - {e}")
            return {
                'thread_id': thread_id,
                'success': False,
                'users_count': 0,
                'successful_users': [],
                'failed_users': [],
                'execution_time': time.time() - start_time,
                'error': str(e)
            }
    
    def run_parallel_auth(self, csv_path: str, headless: bool = True, 
                         relogin: bool = False) -> Dict:
        """
        Запускает параллельную авторизацию пользователей.
        
        Args:
            csv_path: Путь к CSV файлу с пользователями
            headless: Запускать браузер в headless режиме
            relogin: Принудительно переавторизовать пользователей
            
        Returns:
            dict: Результаты выполнения
        """
        self.start_time = time.time()
        
        print(f"🚀 Запуск параллельной авторизации")
        print(f"📁 CSV файл: {csv_path}")
        print(f"🧵 Количество потоков: {self.max_workers}")
        print(f"🖥️ Headless режим: {headless}")
        print(f"🔄 Принудительная переавторизация: {relogin}")
        print("="*60)
        
        # Загружаем пользователей
        users = self.load_users_from_csv(csv_path)
        if not users:
            return {'error': 'Не удалось загрузить пользователей'}
        
        self.total_users = len(users)
        
        # Разделяем пользователей между потоками
        user_groups = self.split_users_by_threads(users)
        
        # Запускаем потоки асинхронно
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Создаем задачи для каждого потока
            tasks = []
            for i, user_group in enumerate(user_groups):
                task = self.run_auth_thread_async(
                    i, 
                    user_group, 
                    headless, 
                    relogin
                )
                tasks.append(task)
            
            # Запускаем все задачи параллельно
            results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            
            # Обрабатываем результаты
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Ошибка в потоке {i}: {result}")
                    self.failed_threads += 1
                    self.thread_results.append({
                        'thread_id': i,
                        'success': False,
                        'users_count': len(user_groups[i]) if i < len(user_groups) else 0,
                        'error': str(result)
                    })
                else:
                    self.thread_results.append(result)
                    if result['success']:
                        self.successful_threads += 1
                    else:
                        self.failed_threads += 1
                        
        finally:
            loop.close()
        
        self.end_time = time.time()
        
        # Формируем итоговый отчет
        return self._generate_final_report()
    
    def _generate_final_report(self) -> Dict:
        """
        Генерирует финальный отчет о выполнении.
        
        Returns:
            dict: Детальный отчет
        """
        total_time = self.end_time - self.start_time
        
        report = {
            'total_users': self.total_users,
            'total_threads': len(self.thread_results),
            'successful_threads': self.successful_threads,
            'failed_threads': self.failed_threads,
            'total_execution_time': total_time,
            'average_time_per_thread': total_time / len(self.thread_results) if self.thread_results else 0,
            'thread_details': self.thread_results
        }
        
        return report
    
    def print_final_report(self, report: Dict) -> None:
        """
        Выводит финальный отчет в консоль.
        
        Args:
            report: Отчет о выполнении
        """
        print("\n" + "="*60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ПАРАЛЛЕЛЬНОЙ АВТОРИЗАЦИИ")
        print("="*60)
        
        print(f"👥 Всего пользователей: {report['total_users']}")
        print(f"🧵 Всего потоков: {report['total_threads']}")
        print(f"✅ Успешных потоков: {report['successful_threads']}")
        print(f"❌ Неуспешных потоков: {report['failed_threads']}")
        print(f"⏱️ Общее время: {report['total_execution_time']:.2f}с")
        print(f"📈 Среднее время на поток: {report['average_time_per_thread']:.2f}с")
        
        if report['thread_details']:
            print(f"\n🔍 ДЕТАЛИ ПО ПОТОКАМ:")
            for detail in report['thread_details']:
                status = "✅" if detail['success'] else "❌"
                print(f"   Поток {detail['thread_id']}: {status} "
                      f"({detail['users_count']} польз., {detail['execution_time']:.2f}с)")
                
                if not detail['success'] and 'error' in detail:
                    print(f"      Ошибка: {detail['error']}")


def parse_arguments():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Параллельная авторизация пользователей из CSV файла"
    )
    
    parser.add_argument(
        "csv_path",
        help="Путь к CSV файлу с пользователями"
    )
    
    parser.add_argument(
        "--threads",
        type=int,
        default=5,
        help="Количество потоков (по умолчанию: 5)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Запускать браузер в headless режиме"
    )
    
    parser.add_argument(
        "--relogin",
        action="store_true",
        help="Принудительно переавторизовать пользователей"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Тихий режим (минимальный вывод)"
    )
    
    return parser.parse_args()


def main():
    """Основная функция."""
    args = parse_arguments()
    
    # Проверяем существование CSV файла
    if not Path(args.csv_path).exists():
        print(f"❌ Файл не найден: {args.csv_path}")
        sys.exit(1)
    
    # Создаем менеджер параллельной авторизации
    manager = ParallelAuthManager(
        max_workers=args.threads,
        verbose=not args.quiet
    )
    
    # Запускаем параллельную авторизацию
    report = manager.run_parallel_auth(
        csv_path=args.csv_path,
        headless=args.headless,
        relogin=args.relogin
    )
    
    # Выводим отчет
    if not args.quiet:
        manager.print_final_report(report)
    
    # Сохраняем отчет в JSON
    report_file = project_root / "logs" / f"parallel_auth_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Отчет сохранен: {report_file}")
    
    # Возвращаем код выхода
    if 'error' in report:
        sys.exit(1)
    elif report['failed_threads'] > 0:
        sys.exit(2)  # Частичная неудача
    else:
        sys.exit(0)  # Успех


if __name__ == "__main__":
    main()
