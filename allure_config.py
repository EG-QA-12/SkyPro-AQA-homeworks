#!/usr/bin/env python3
"""
Централизованная конфигурация Allure отчетности для всех тестовых проектов.

Этот модуль предоставляет:
- Стандартизированные настройки Allure
- Утилиты для управления отчетами
- Общие метаданные и категории
- Функции для автоматизации процесса отчетности
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime


class AllureConfig:
    """Конфигурация Allure отчетности для тестовых проектов."""
    
    # Базовые директории
    BASE_DIR = Path(__file__).parent
    
    # Директории результатов для каждого проекта
    RESULTS_DIRS = {
        'auth_project': BASE_DIR / 'auth_project' / 'allure-results',
        'e2e_tests': BASE_DIR / 'e2e_tests' / 'allure-results',
        'integration_tests': BASE_DIR / 'integration_tests' / 'allure-results',
    }
    
    # Директории отчетов для каждого проекта
    REPORTS_DIRS = {
        'auth_project': BASE_DIR / 'auth_project' / 'allure-reports',
        'e2e_tests': BASE_DIR / 'e2e_tests' / 'allure-reports',
        'integration_tests': BASE_DIR / 'integration_tests' / 'allure-reports',
    }
    
    # Общие настройки среды
    ENVIRONMENT = {
        'Platform': 'Windows',
        'Python.Version': '3.9+',
        'Test.Framework': 'pytest',
        'Browser': 'Chromium',
        'Test.Runner': 'pytest-playwright',
    }
    
    # Стандартные категории для всех проектов
    CATEGORIES = [
        {
            'name': 'Ignored tests',
            'messageRegex': '.*ignored.*',
            'traceRegex': '.*',
            'matchedStatuses': ['skipped']
        },
        {
            'name': 'Infrastructure defects',
            'messageRegex': '.*(connection|timeout|network).*',
            'traceRegex': '.*',
            'matchedStatuses': ['broken']
        },
        {
            'name': 'Outdated tests',
            'messageRegex': '.*obsolete.*',
            'traceRegex': '.*',
            'matchedStatuses': ['broken']
        },
        {
            'name': 'Product defects',
            'messageRegex': '.*',
            'traceRegex': '.*',
            'matchedStatuses': ['failed']
        },
        {
            'name': 'Test defects',
            'messageRegex': '.*',
            'traceRegex': '.*',
            'matchedStatuses': ['broken']
        }
    ]

    @classmethod
    def create_environment_properties(cls, project_name: str, additional_props: Optional[Dict[str, str]] = None) -> Path:
        """
        Создает файл environment.properties для указанного проекта.
        
        Args:
            project_name: Название проекта ('auth_project', 'e2e_tests', 'integration_tests')
            additional_props: Дополнительные свойства среды
            
        Returns:
            Path: Путь к созданному файлу environment.properties
        """
        if project_name not in cls.RESULTS_DIRS:
            raise ValueError(f"Unknown project: {project_name}")
        
        results_dir = cls.RESULTS_DIRS[project_name]
        results_dir.mkdir(parents=True, exist_ok=True)
        
        env_file = results_dir / 'environment.properties'
        
        # Объединяем базовые и дополнительные свойства
        env_props = cls.ENVIRONMENT.copy()
        if additional_props:
            env_props.update(additional_props)
        
        # Добавляем специфичные для проекта свойства
        env_props.update({
            'Project.Name': project_name,
            'Test.Execution.Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })
        
        # Записываем свойства в файл
        with open(env_file, 'w', encoding='utf-8') as f:
            for key, value in env_props.items():
                f.write(f'{key}={value}\n')
        
        return env_file

    @classmethod
    def create_categories_json(cls, project_name: str, additional_categories: Optional[List[Dict]] = None) -> Path:
        """
        Создает файл categories.json для указанного проекта.
        
        Args:
            project_name: Название проекта
            additional_categories: Дополнительные категории
            
        Returns:
            Path: Путь к созданному файлу categories.json
        """
        import json
        
        if project_name not in cls.RESULTS_DIRS:
            raise ValueError(f"Unknown project: {project_name}")
        
        results_dir = cls.RESULTS_DIRS[project_name]
        results_dir.mkdir(parents=True, exist_ok=True)
        
        categories_file = results_dir / 'categories.json'
        
        # Объединяем базовые и дополнительные категории
        categories = cls.CATEGORIES.copy()
        if additional_categories:
            categories.extend(additional_categories)
        
        # Записываем категории в файл
        with open(categories_file, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)
        
        return categories_file

    @classmethod
    def clean_results(cls, project_name: Optional[str] = None) -> None:
        """
        Очищает директории результатов Allure.
        
        Args:
            project_name: Название проекта для очистки. Если None, очищает все проекты.
        """
        if project_name:
            if project_name not in cls.RESULTS_DIRS:
                raise ValueError(f"Unknown project: {project_name}")
            projects = [project_name]
        else:
            projects = list(cls.RESULTS_DIRS.keys())
        
        for proj in projects:
            results_dir = cls.RESULTS_DIRS[proj]
            if results_dir.exists():
                shutil.rmtree(results_dir)
                print(f"✅ Очищена директория результатов для {proj}: {results_dir}")

    @classmethod
    def clean_reports(cls, project_name: Optional[str] = None) -> None:
        """
        Очищает директории отчетов Allure.
        
        Args:
            project_name: Название проекта для очистки. Если None, очищает все проекты.
        """
        if project_name:
            if project_name not in cls.REPORTS_DIRS:
                raise ValueError(f"Unknown project: {project_name}")
            projects = [project_name]
        else:
            projects = list(cls.REPORTS_DIRS.keys())
        
        for proj in projects:
            reports_dir = cls.REPORTS_DIRS[proj]
            if reports_dir.exists():
                shutil.rmtree(reports_dir)
                print(f"✅ Очищена директория отчетов для {proj}: {reports_dir}")

    @classmethod
    def generate_report(cls, project_name: str, open_browser: bool = True) -> Optional[Path]:
        """
        Генерирует HTML отчет Allure для указанного проекта.
        
        Args:
            project_name: Название проекта
            open_browser: Открыть отчет в браузере после генерации
            
        Returns:
            Path: Путь к сгенерированному отчету или None в случае ошибки
        """
        if project_name not in cls.RESULTS_DIRS:
            raise ValueError(f"Unknown project: {project_name}")
        
        results_dir = cls.RESULTS_DIRS[project_name]
        reports_dir = cls.REPORTS_DIRS[project_name]
        
        if not results_dir.exists() or not any(results_dir.iterdir()):
            print(f"❌ Нет результатов для генерации отчета в {results_dir}")
            return None
        
        # Создаем директорию отчетов
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Генерируем отчет
            cmd = ['allure', 'generate', str(results_dir), '-o', str(reports_dir), '--clean']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Отчет Allure сгенерирован для {project_name}: {reports_dir}")
                
                # Открываем отчет в браузере
                if open_browser:
                    cls.open_report(project_name)
                
                return reports_dir
            else:
                print(f"❌ Ошибка генерации отчета: {result.stderr}")
                return None
                
        except FileNotFoundError:
            print("❌ Allure CLI не найден. Установите Allure: https://docs.qameta.io/allure/#_installing_a_commandline")
            return None
        except Exception as e:
            print(f"❌ Неожиданная ошибка при генерации отчета: {e}")
            return None

    @classmethod
    def open_report(cls, project_name: str) -> bool:
        """
        Открывает сгенерированный отчет Allure в браузере.
        
        Args:
            project_name: Название проекта
            
        Returns:
            bool: True если отчет успешно открыт, False в противном случае
        """
        if project_name not in cls.REPORTS_DIRS:
            raise ValueError(f"Unknown project: {project_name}")
        
        reports_dir = cls.REPORTS_DIRS[project_name]
        index_file = reports_dir / 'index.html'
        
        if not index_file.exists():
            print(f"❌ Отчет не найден: {index_file}")
            return False
        
        try:
            # Открываем отчет в браузере по умолчанию
            import webbrowser
            webbrowser.open(f'file://{index_file.absolute()}')
            print(f"🌐 Отчет открыт в браузере: {index_file}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка открытия отчета: {e}")
            return False

    @classmethod
    def serve_report(cls, project_name: str, port: int = 8080) -> Optional[subprocess.Popen]:
        """
        Запускает локальный сервер для просмотра отчета Allure.
        
        Args:
            project_name: Название проекта
            port: Порт для сервера
            
        Returns:
            subprocess.Popen: Процесс сервера или None в случае ошибки
        """
        if project_name not in cls.REPORTS_DIRS:
            raise ValueError(f"Unknown project: {project_name}")
        
        reports_dir = cls.REPORTS_DIRS[project_name]
        
        if not reports_dir.exists():
            print(f"❌ Директория отчетов не найдена: {reports_dir}")
            return None
        
        try:
            cmd = ['allure', 'serve', str(cls.RESULTS_DIRS[project_name]), '--port', str(port)]
            process = subprocess.Popen(cmd)
            print(f"🚀 Сервер Allure запущен для {project_name} на порту {port}")
            print(f"🌐 Откройте http://localhost:{port} в браузере")
            return process
            
        except FileNotFoundError:
            print("❌ Allure CLI не найден.")
            return None
        except Exception as e:
            print(f"❌ Ошибка запуска сервера: {e}")
            return None

    @classmethod
    def setup_project(cls, project_name: str, additional_env: Optional[Dict[str, str]] = None) -> None:
        """
        Настраивает проект для работы с Allure (создает необходимые файлы).
        
        Args:
            project_name: Название проекта
            additional_env: Дополнительные переменные среды
        """
        print(f"🔧 Настройка Allure для проекта: {project_name}")
        
        # Создаем environment.properties
        env_file = cls.create_environment_properties(project_name, additional_env)
        print(f"✅ Создан файл среды: {env_file}")
        
        # Создаем categories.json
        cat_file = cls.create_categories_json(project_name)
        print(f"✅ Создан файл категорий: {cat_file}")
        
        print(f"🎉 Проект {project_name} готов для работы с Allure!")


# Вспомогательные функции для быстрого использования
def setup_all_projects() -> None:
    """Настраивает все проекты для работы с Allure."""
    for project in AllureConfig.RESULTS_DIRS.keys():
        AllureConfig.setup_project(project)

def clean_all() -> None:
    """Очищает все результаты и отчеты."""
    AllureConfig.clean_results()
    AllureConfig.clean_reports()

def generate_all_reports(open_browser: bool = False) -> None:
    """Генерирует отчеты для всех проектов."""
    for project in AllureConfig.RESULTS_DIRS.keys():
        AllureConfig.generate_report(project, open_browser)


if __name__ == "__main__":
    # Пример использования
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python allure_config.py <command> [project_name]")
        print("Команды:")
        print("  setup [project_name]     - Настроить проект для Allure")
        print("  clean [project_name]     - Очистить результаты и отчеты")
        print("  generate <project_name>  - Сгенерировать отчет")
        print("  serve <project_name>     - Запустить сервер отчетов")
        print("  open <project_name>      - Открыть отчет в браузере")
        sys.exit(1)
    
    command = sys.argv[1]
    project = sys.argv[2] if len(sys.argv) > 2 else None
    
    if command == "setup":
        if project:
            AllureConfig.setup_project(project)
        else:
            setup_all_projects()
    elif command == "clean":
        AllureConfig.clean_results(project)
        AllureConfig.clean_reports(project)
    elif command == "generate" and project:
        AllureConfig.generate_report(project, open_browser=True)
    elif command == "serve" and project:
        process = AllureConfig.serve_report(project)
        if process:
            try:
                process.wait()
            except KeyboardInterrupt:
                process.terminate()
    elif command == "open" and project:
        AllureConfig.open_report(project)
    else:
        print(f"❌ Неизвестная команда или отсутствует название проекта: {command}")
        sys.exit(1)
