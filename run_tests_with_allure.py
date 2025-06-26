#!/usr/bin/env python3
"""
Автоматизированный скрипт для запуска тестов с генерацией Allure отчетов.

Этот скрипт предоставляет:
- Запуск всех типов тестов с автоматической генерацией отчетов
- Очистку старых результатов
- Открытие отчетов в браузере
- Объединение отчетов всех проектов
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

# Импортируем конфигурацию Allure
sys.path.insert(0, str(Path(__file__).parent))
from allure_config import AllureConfig


class TestRunner:
    """Класс для запуска тестов с интеграцией Allure."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.projects = {
            'auth_project': self.base_dir / 'auth_project',
            'e2e_tests': self.base_dir / 'e2e_tests',
            'integration_tests': self.base_dir / 'integration_tests'
        }
    
    def run_project_tests(
        self, 
        project_name: str, 
        test_args: List[str] = None,
        generate_report: bool = True,
        open_browser: bool = False
    ) -> bool:
        """
        Запускает тесты для указанного проекта.
        
        Args:
            project_name: Имя проекта
            test_args: Дополнительные аргументы для pytest
            generate_report: Генерировать ли отчет после выполнения
            open_browser: Открывать ли отчет в браузере
            
        Returns:
            bool: True если тесты прошли успешно
        """
        if project_name not in self.projects:
            print(f"❌ Неизвестный проект: {project_name}")
            return False
        
        project_dir = self.projects[project_name]
        
        if not project_dir.exists():
            print(f"❌ Директория проекта не найдена: {project_dir}")
            return False
        
        print(f"🚀 Запуск тестов для проекта: {project_name}")
        print(f"📁 Директория: {project_dir}")
        
        # Формируем команду pytest
        cmd = ['python', '-m', 'pytest']
        
        # Добавляем путь к конфигурации pytest
        if project_name == 'auth_project':
            cmd.extend(['-c', str(project_dir / 'config' / 'pytest.ini')])
        else:
            cmd.extend(['-c', str(project_dir / 'pytest.ini')])
        
        # Указываем директорию для поиска тестов
        cmd.append(str(project_dir))
        
        # Добавляем дополнительные аргументы
        if test_args:
            cmd.extend(test_args)
        
        print(f"🔧 Команда: {' '.join(cmd)}")
        
        # Запускаем тесты
        start_time = time.time()
        result = subprocess.run(cmd, cwd=self.base_dir)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"⏱️ Время выполнения: {execution_time:.2f} секунд")
        
        success = result.returncode == 0
        if success:
            print(f"✅ Тесты проекта {project_name} завершены успешно")
        else:
            print(f"❌ Тесты проекта {project_name} завершились с ошибками (код: {result.returncode})")
        
        # Генерируем отчет если требуется
        if generate_report:
            print(f"📊 Генерация Allure отчета для {project_name}...")
            report_path = AllureConfig.generate_report(project_name, open_browser)
            if report_path:
                print(f"📋 Отчет сохранен в: {report_path}")
        
        return success
    
    def run_all_projects(
        self, 
        test_args: List[str] = None,
        generate_reports: bool = True,
        open_browser: bool = False,
        stop_on_first_failure: bool = False
    ) -> dict:
        """
        Запускает тесты для всех проектов.
        
        Args:
            test_args: Дополнительные аргументы для pytest
            generate_reports: Генерировать ли отчеты
            open_browser: Открывать ли отчеты в браузере
            stop_on_first_failure: Останавливаться ли при первой ошибке
            
        Returns:
            dict: Результаты выполнения для каждого проекта
        """
        print("🎯 Запуск всех тестовых проектов")
        print("=" * 50)
        
        results = {}
        total_start_time = time.time()
        
        for project_name in self.projects.keys():
            print(f"\n{'=' * 20} {project_name.upper()} {'=' * 20}")
            
            success = self.run_project_tests(
                project_name, 
                test_args, 
                generate_reports, 
                open_browser and project_name == list(self.projects.keys())[-1]  # Открываем только последний
            )
            
            results[project_name] = success
            
            if not success and stop_on_first_failure:
                print(f"🛑 Остановка выполнения из-за ошибки в {project_name}")
                break
        
        total_end_time = time.time()
        total_execution_time = total_end_time - total_start_time
        
        # Печатаем сводку результатов
        print("\n" + "=" * 50)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ")
        print("=" * 50)
        
        for project_name, success in results.items():
            status = "✅ УСПЕШНО" if success else "❌ ОШИБКА"
            print(f"{project_name:20} {status}")
        
        successful_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n🏁 Общий результат: {successful_count}/{total_count} проектов успешно")
        print(f"⏱️ Общее время выполнения: {total_execution_time:.2f} секунд")
        
        return results
    
    def clean_all(self):
        """Очищает все результаты и отчеты."""
        print("🧹 Очистка всех Allure результатов и отчетов...")
        AllureConfig.clean_results()
        AllureConfig.clean_reports()
        print("✨ Очистка завершена")
    
    def setup_all(self):
        """Настраивает все проекты для работы с Allure."""
        print("🔧 Настройка всех проектов для работы с Allure...")
        for project_name in self.projects.keys():
            AllureConfig.setup_project(project_name)
        print("✅ Настройка завершена")


def main():
    """Главная функция с парсингом аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Автоматизированный запуск тестов с Allure отчетами",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Запуск всех тестов с генерацией отчетов
  python run_tests_with_allure.py --all

  # Запуск только auth_project тестов
  python run_tests_with_allure.py --project auth_project

  # Запуск тестов с дополнительными аргументами pytest
  python run_tests_with_allure.py --all --pytest-args "-v -k test_login"

  # Очистка всех результатов
  python run_tests_with_allure.py --clean

  # Настройка всех проектов
  python run_tests_with_allure.py --setup

  # Запуск с открытием отчета в браузере
  python run_tests_with_allure.py --project e2e_tests --open-browser

  # Генерация отчета без запуска тестов
  python run_tests_with_allure.py --generate-only auth_project
        """
    )
    
    # Основные команды
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--all', 
        action='store_true',
        help='Запустить тесты для всех проектов'
    )
    group.add_argument(
        '--project', 
        choices=['auth_project', 'e2e_tests', 'integration_tests'],
        help='Запустить тесты для конкретного проекта'
    )
    group.add_argument(
        '--clean', 
        action='store_true',
        help='Очистить все Allure результаты и отчеты'
    )
    group.add_argument(
        '--setup', 
        action='store_true',
        help='Настроить все проекты для работы с Allure'
    )
    group.add_argument(
        '--generate-only',
        choices=['auth_project', 'e2e_tests', 'integration_tests'],
        help='Только сгенерировать отчет для проекта (без запуска тестов)'
    )
    
    # Дополнительные опции
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Не генерировать отчет после выполнения тестов'
    )
    parser.add_argument(
        '--open-browser',
        action='store_true',
        help='Открыть отчет в браузере после генерации'
    )
    parser.add_argument(
        '--stop-on-failure',
        action='store_true',
        help='Остановиться при первой ошибке (только для --all)'
    )
    parser.add_argument(
        '--pytest-args',
        type=str,
        help='Дополнительные аргументы для pytest (в кавычках)'
    )
    
    args = parser.parse_args()
    
    # Создаем экземпляр runner
    runner = TestRunner()
    
    # Парсим дополнительные аргументы pytest
    pytest_args = []
    if args.pytest_args:
        pytest_args = args.pytest_args.split()
    
    # Выполняем команды
    if args.clean:
        runner.clean_all()
    elif args.setup:
        runner.setup_all()
    elif args.generate_only:
        print(f"📊 Генерация отчета для {args.generate_only}...")
        AllureConfig.generate_report(args.generate_only, args.open_browser)
    elif args.all:
        results = runner.run_all_projects(
            test_args=pytest_args,
            generate_reports=not args.no_report,
            open_browser=args.open_browser,
            stop_on_first_failure=args.stop_on_failure
        )
        
        # Выходим с кодом ошибки если есть неуспешные тесты
        if not all(results.values()):
            sys.exit(1)
    elif args.project:
        success = runner.run_project_tests(
            args.project,
            test_args=pytest_args,
            generate_report=not args.no_report,
            open_browser=args.open_browser
        )
        
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
