#!/usr/bin/env python3
"""
Скрипт для анализа и консолидации избыточных файлов requirements.txt

Этот скрипт:
1. Находит все файлы requirements.txt в проекте
2. Анализирует их содержимое и выявляет дублирования
3. Создает единый консолидированный requirements.txt
4. Удаляет избыточные файлы после подтверждения
"""

from pathlib import Path
from typing import Dict, List, Set, Tuple
import re


def find_requirements_files(root_path: Path) -> List[Path]:
    """Находит все файлы requirements*.txt в проекте."""
    requirements_files = []
    
    # Исключаем системные директории
    exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules', 'allure-results'}
    
    for req_file in root_path.rglob('requirements*.txt'):
        # Проверяем, что файл не в исключаемых директориях
        if not any(excluded in req_file.parts for excluded in exclude_dirs):
            requirements_files.append(req_file)
    
    return sorted(requirements_files)


def parse_requirements_file(file_path: Path) -> Dict[str, str]:
    """Парсит файл requirements.txt и возвращает словарь {package: version}."""
    packages = {}
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Пропускаем комментарии и пустые строки
            if not line or line.startswith('#'):
                continue
            
            # Извлекаем имя пакета и версию
            # Поддерживаем форматы: package>=1.0.0, package==1.0.0, package
            match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+.*)?$', line)
            if match:
                package_name = match.group(1).lower()
                version_spec = match.group(2) if match.group(2) else ''
                packages[package_name] = version_spec
                
    except Exception as e:
        print(f"❌ Ошибка при чтении {file_path}: {e}")
    
    return packages


def analyze_requirements(files: List[Path]) -> Tuple[Dict[str, Dict[str, str]], Set[str]]:
    """Анализирует файлы requirements и возвращает пакеты и дублирования."""
    all_packages = {}  # {package: {file_path: version_spec}}
    duplicates = set()
    
    for file_path in files:
        packages = parse_requirements_file(file_path)
        file_str = str(file_path.relative_to(file_path.parts[0]))
        
        for package, version in packages.items():
            if package not in all_packages:
                all_packages[package] = {}
            
            all_packages[package][file_str] = version
            
            # Если пакет встречается в нескольких файлах, это дублирование
            if len(all_packages[package]) > 1:
                duplicates.add(package)
    
    return all_packages, duplicates


def create_consolidated_requirements(all_packages: Dict[str, Dict[str, str]]) -> str:
    """Создает консолидированный requirements.txt с наилучшими версиями."""
    consolidated = []
    
    # Группируем пакеты по категориям
    categories = {
        'Тестовый фреймворк': ['pytest', 'pytest-html', 'pytest-xdist', 'pytest-playwright', 'pytest-asyncio'],
        'Playwright для E2E тестирования': ['playwright'],
        'Allure отчетность': ['allure-pytest', 'allure-python-commons'],
        'HTTP клиенты для API тестирования': ['requests', 'urllib3'],
        'Работа с данными и валидация': ['pydantic', 'pydantic-settings', 'pydantic-core'],
        'Конфигурация и секреты': ['python-dotenv'],
        'Утилиты': ['colorama', 'python-slugify', 'typing-extensions', 'pygments'],
        'Безопасность': ['bcrypt'],
        'Development зависимости': ['black', 'ruff', 'mypy', 'pre-commit']
    }
    
    # Создаем заголовок
    consolidated.append("# Основные зависимости фреймворка автоматизации тестирования")
    consolidated.append("# Консолидированный файл - единый источник зависимостей")
    consolidated.append("")
    
    # Добавляем пакеты по категориям
    for category, category_packages in categories.items():
        added_packages = []
        
        for package in category_packages:
            if package in all_packages:
                # Выбираем самую строгую версию (с наибольшими требованиями)
                versions = all_packages[package]
                best_version = choose_best_version(versions)
                added_packages.append(f"{package}{best_version}")
        
        if added_packages:
            consolidated.append(f"# {category}")
            consolidated.extend(added_packages)
            consolidated.append("")
    
    # Добавляем остальные пакеты
    other_packages = []
    used_packages = set()
    for category_packages in categories.values():
        used_packages.update(category_packages)
    
    for package in sorted(all_packages.keys()):
        if package not in used_packages:
            versions = all_packages[package]
            best_version = choose_best_version(versions)
            other_packages.append(f"{package}{best_version}")
    
    if other_packages:
        consolidated.append("# Дополнительные зависимости")
        consolidated.extend(other_packages)
    
    return '\n'.join(consolidated)


def choose_best_version(versions: Dict[str, str]) -> str:
    """Выбирает наилучшую версию из доступных."""
    if not versions:
        return ''
    
    # Приоритет: >= > == > без версии
    version_specs = list(versions.values())
    
    # Убираем пустые версии
    non_empty = [v for v in version_specs if v]
    if not non_empty:
        return ''
    
    # Предпочитаем >= версии
    ge_versions = [v for v in non_empty if v.startswith('>=')]
    if ge_versions:
        # Берем максимальную версию
        return max(ge_versions, key=lambda x: x.split('>=')[1] if '>=' in x else '0')
    
    # Иначе берем первую доступную
    return non_empty[0]


def main():
    """Основная функция скрипта."""
    print("🔧 Анализ и консолидация файлов requirements.txt...")
    
    # Определяем корень проекта
    project_root = Path(__file__).resolve().parent.parent.parent
    print(f"📁 Корень проекта: {project_root}")
    
    # Находим все файлы requirements
    requirements_files = find_requirements_files(project_root)
    print(f"📄 Найдено {len(requirements_files)} файлов requirements:")
    for file_path in requirements_files:
        relative_path = file_path.relative_to(project_root)
        print(f"   • {relative_path}")
    
    if len(requirements_files) <= 1:
        print("ℹ️ Консолидация не требуется - найден только один файл requirements")
        return
    
    # Анализируем содержимое
    all_packages, duplicates = analyze_requirements(requirements_files)
    
    print(f"\n📊 Результаты анализа:")
    print(f"   • Уникальных пакетов: {len(all_packages)}")
    print(f"   • Дублирующихся пакетов: {len(duplicates)}")
    
    if duplicates:
        print(f"\n🔄 Дублирующиеся пакеты:")
        for package in sorted(duplicates):
            print(f"   • {package}:")
            for file_path, version in all_packages[package].items():
                print(f"     - {file_path}: {version or '(без версии)'}")
    
    # Создаем консолидированный requirements.txt
    consolidated_content = create_consolidated_requirements(all_packages)
    
    # Сохраняем в корень проекта
    main_requirements = project_root / "requirements.txt"
    main_requirements.write_text(consolidated_content, encoding='utf-8')
    print(f"\n✅ Создан консолидированный requirements.txt")
    
    # Выводим список файлов для удаления
    files_to_remove = [f for f in requirements_files if f != main_requirements]
    if files_to_remove:
        print(f"\n📋 Рекомендуется удалить избыточные файлы:")
        for file_path in files_to_remove:
            relative_path = file_path.relative_to(project_root)
            print(f"   • {relative_path}")
        
        print(f"\n💡 Команды для удаления:")
        for file_path in files_to_remove:
            relative_path = file_path.relative_to(project_root)
            print(f"   rm \"{relative_path}\"")
    
    print("\n✅ Консолидация requirements.txt завершена!")


if __name__ == "__main__":
    main() 