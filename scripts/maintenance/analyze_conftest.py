#!/usr/bin/env python3
"""
Скрипт для анализа файлов conftest.py и выявления дублирования.

Анализирует содержимое всех conftest.py файлов в проекте и предлагает
оптимизацию структуры pytest конфигураций.
"""

from pathlib import Path
from typing import List, Dict, Set
import ast
import re


def find_conftest_files(root_path: Path) -> List[Path]:
    """Находит все файлы conftest.py в проекте."""
    conftest_files = []
    
    # Исключаем системные директории
    exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}
    
    for conftest_file in root_path.rglob('conftest.py'):
        # Проверяем, что файл не в исключаемых директориях
        if not any(excluded in conftest_file.parts for excluded in exclude_dirs):
            conftest_files.append(conftest_file)
    
    return sorted(conftest_files)


def analyze_conftest_content(file_path: Path) -> Dict:
    """Анализирует содержимое conftest.py файла."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        analysis = {
            'file_path': file_path,
            'functions': [],
            'fixtures': [],
            'imports': [],
            'pytest_options': [],
            'sys_path_manipulations': [],
            'lines_count': len(content.split('\n')),
            'has_docstring': bool(re.search(r'""".*?"""', content, re.DOTALL)),
        }
        
        # Ищем функции
        functions = re.findall(r'def\s+(\w+)\s*\(', content)
        analysis['functions'] = functions
        
        # Ищем фикстуры
        fixtures = re.findall(r'@pytest\.fixture[\s\S]*?def\s+(\w+)', content)
        analysis['fixtures'] = fixtures
        
        # Ищем импорты
        imports = re.findall(r'^(import\s+.+|from\s+.+import\s+.+)', content, re.MULTILINE)
        analysis['imports'] = imports
        
        # Ищем pytest опции
        if 'pytest_addoption' in content:
            analysis['pytest_options'].append('pytest_addoption')
        
        # Ищем манипуляции с sys.path
        if 'sys.path' in content:
            path_lines = [line.strip() for line in content.split('\n') if 'sys.path' in line]
            analysis['sys_path_manipulations'] = path_lines
        
        return analysis
        
    except Exception as e:
        print(f"❌ Ошибка при анализе {file_path}: {e}")
        return {'file_path': file_path, 'error': str(e)}


def find_duplicated_logic(analyses: List[Dict]) -> Dict:
    """Находит дублирующуюся логику между conftest файлами."""
    duplications = {
        'functions': {},
        'fixtures': {},
        'imports': {},
        'sys_path_logic': []
    }
    
    # Анализируем функции
    all_functions = {}
    for analysis in analyses:
        if 'functions' in analysis:
            for func in analysis['functions']:
                if func not in all_functions:
                    all_functions[func] = []
                all_functions[func].append(analysis['file_path'])
    
    duplications['functions'] = {func: files for func, files in all_functions.items() if len(files) > 1}
    
    # Анализируем фикстуры
    all_fixtures = {}
    for analysis in analyses:
        if 'fixtures' in analysis:
            for fixture in analysis['fixtures']:
                if fixture not in all_fixtures:
                    all_fixtures[fixture] = []
                all_fixtures[fixture].append(analysis['file_path'])
    
    duplications['fixtures'] = {fixture: files for fixture, files in all_fixtures.items() if len(files) > 1}
    
    # Анализируем sys.path манипуляции
    for analysis in analyses:
        if 'sys_path_manipulations' in analysis and analysis['sys_path_manipulations']:
            duplications['sys_path_logic'].append({
                'file': analysis['file_path'],
                'manipulations': analysis['sys_path_manipulations']
            })
    
    return duplications


def create_optimization_plan(analyses: List[Dict], duplications: Dict) -> List[str]:
    """Создает план оптимизации conftest файлов."""
    plan = []
    
    # Корневой conftest.py должен содержать общую логику
    root_conftest = Path("conftest.py")
    
    plan.append("# ПЛАН ОПТИМИЗАЦИИ CONFTEST.PY ФАЙЛОВ")
    plan.append("")
    
    # Анализируем sys.path логику
    if duplications['sys_path_logic']:
        plan.append("## 1. Консолидация sys.path логики")
        plan.append("Все манипуляции с sys.path должны быть в корневом conftest.py:")
        for item in duplications['sys_path_logic']:
            relative_path = item['file'].relative_to(Path.cwd())
            plan.append(f"   • {relative_path}: {len(item['manipulations'])} манипуляций")
        plan.append("")
    
    # Анализируем дублирующиеся функции
    if duplications['functions']:
        plan.append("## 2. Дублирующиеся функции")
        for func, files in duplications['functions'].items():
            plan.append(f"   • {func}:")
            for file_path in files:
                relative_path = file_path.relative_to(Path.cwd())
                plan.append(f"     - {relative_path}")
        plan.append("")
    
    # Анализируем дублирующиеся фикстуры
    if duplications['fixtures']:
        plan.append("## 3. Дублирующиеся фикстуры")
        for fixture, files in duplications['fixtures'].items():
            plan.append(f"   • {fixture}:")
            for file_path in files:
                relative_path = file_path.relative_to(Path.cwd())
                plan.append(f"     - {relative_path}")
        plan.append("")
    
    # Предложения по оптимизации
    plan.append("## 4. Рекомендации по оптимизации")
    
    # Файлы для удаления
    redundant_files = []
    for analysis in analyses:
        file_path = analysis['file_path']
        relative_path = file_path.relative_to(Path.cwd())
        
        # Пропускаем корневой conftest
        if str(relative_path) == "conftest.py":
            continue
            
        # Если файл содержит только sys.path и базовые импорты, он избыточен
        if ('functions' in analysis and len(analysis['functions']) <= 1 and
            'fixtures' in analysis and len(analysis['fixtures']) == 0 and
            'sys_path_manipulations' in analysis and analysis['sys_path_manipulations']):
            redundant_files.append(relative_path)
    
    if redundant_files:
        plan.append("### Файлы для удаления (содержат только sys.path):")
        for file_path in redundant_files:
            plan.append(f"   • {file_path}")
        plan.append("")
    
    # Файлы для объединения
    plan.append("### Действия по консолидации:")
    plan.append("1. Перенести всю sys.path логику в корневой conftest.py")
    plan.append("2. Оставить специфичные фикстуры в локальных conftest.py")
    plan.append("3. Удалить избыточные файлы")
    plan.append("4. Обновить импорты в тестах")
    
    return plan


def main():
    """Основная функция скрипта."""
    print("🔧 Анализ файлов conftest.py...")
    
    # Определяем корень проекта
    project_root = Path(__file__).resolve().parent.parent.parent
    print(f"📁 Корень проекта: {project_root}")
    
    # Находим все conftest.py файлы
    conftest_files = find_conftest_files(project_root)
    print(f"📄 Найдено {len(conftest_files)} файлов conftest.py:")
    
    analyses = []
    for file_path in conftest_files:
        relative_path = file_path.relative_to(project_root)
        print(f"   • {relative_path}")
        analysis = analyze_conftest_content(file_path)
        analyses.append(analysis)
    
    # Анализируем дублирование
    duplications = find_duplicated_logic(analyses)
    
    print(f"\n📊 Результаты анализа:")
    print(f"   • Файлов с sys.path логикой: {len(duplications['sys_path_logic'])}")
    print(f"   • Дублирующихся функций: {len(duplications['functions'])}")
    print(f"   • Дублирующихся фикстур: {len(duplications['fixtures'])}")
    
    # Создаем план оптимизации
    optimization_plan = create_optimization_plan(analyses, duplications)
    
    # Сохраняем план в файл
    plan_file = project_root / "conftest_optimization_plan.md"
    plan_file.write_text('\n'.join(optimization_plan), encoding='utf-8')
    
    print(f"\n✅ План оптимизации сохранен в: conftest_optimization_plan.md")
    print("\n📋 Краткий план:")
    for line in optimization_plan[:15]:  # Показываем первые 15 строк
        print(f"   {line}")
    
    print("\n✅ Анализ conftest.py завершен!")


if __name__ == "__main__":
    main()