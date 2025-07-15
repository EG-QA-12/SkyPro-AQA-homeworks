#!/usr/bin/env python3
"""
Скрипт для анализа структуры импортов и выявления циклических зависимостей.

Этот скрипт:
1. Сканирует все Python файлы в проекте
2. Извлекает все импорты и строит граф зависимостей
3. Выявляет циклические зависимости
4. Создает отчет с рекомендациями по оптимизации

Результат: imports_analysis_report.md с детальным анализом
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import re

# Исключаемые директории
EXCLUDE_DIRS = {'.git', 'venv', '__pycache__', 'allure-results', 'logs', 'screenshots', '.pytest_cache'}

class ImportAnalyzer:
    """Анализатор импортов для выявления зависимостей и циклов."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.file_imports: Dict[str, Set[str]] = defaultdict(set)
        self.module_graph: Dict[str, Set[str]] = defaultdict(set)
        self.python_files: List[Path] = []
        
    def scan_project(self) -> None:
        """Сканирует проект и находит все Python файлы."""
        print("🔍 Сканирование проекта...")
        
        for py_file in self.project_root.rglob("*.py"):
            # Пропускаем исключенные директории
            if any(excluded in py_file.parts for excluded in EXCLUDE_DIRS):
                continue
            self.python_files.append(py_file)
        
        print(f"📁 Найдено {len(self.python_files)} Python файлов")
    
    def extract_imports(self, file_path: Path) -> Set[str]:
        """Извлекает все импорты из Python файла."""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсинг AST для надежного извлечения импортов
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module)
            except SyntaxError:
                # Если AST не работает, используем регулярные выражения
                self._extract_imports_regex(content, imports)
                
        except (UnicodeDecodeError, FileNotFoundError) as e:
            print(f"⚠️ Ошибка чтения файла {file_path}: {e}")
        
        return imports
    
    def _extract_imports_regex(self, content: str, imports: Set[str]) -> None:
        """Извлекает импорты с помощью регулярных выражений."""
        # from module import ...
        from_imports = re.findall(r'^\s*from\s+([\w\.]+)\s+import', content, re.MULTILINE)
        imports.update(from_imports)
        
        # import module
        import_statements = re.findall(r'^\s*import\s+([\w\.]+)', content, re.MULTILINE)
        imports.update(import_statements)
    
    def get_module_name(self, file_path: Path) -> str:
        """Преобразует путь к файлу в имя модуля."""
        try:
            relative_path = file_path.relative_to(self.project_root)
            
            # Убираем .py расширение
            if relative_path.name == "__init__.py":
                module_path = relative_path.parent
            else:
                module_path = relative_path.with_suffix('')
            
            # Преобразуем путь в module notation
            return str(module_path).replace('/', '.').replace('\\', '.')
        except ValueError:
            return str(file_path)
    
    def build_dependency_graph(self) -> None:
        """Строит граф зависимостей между модулями."""
        print("🔗 Построение графа зависимостей...")
        
        for py_file in self.python_files:
            module_name = self.get_module_name(py_file)
            imports = self.extract_imports(py_file)
            
            # Фильтруем только внутренние импорты проекта
            project_imports = set()
            for imp in imports:
                if self._is_project_import(imp):
                    project_imports.add(imp)
            
            self.file_imports[module_name] = project_imports
            self.module_graph[module_name] = project_imports
    
    def _is_project_import(self, import_name: str) -> bool:
        """Проверяет, является ли импорт внутренним для проекта."""
        project_modules = {
            'framework', 'tests', 'projects', 'scripts', 'config'
        }
        
        return any(import_name.startswith(module) for module in project_modules)
    
    def find_cycles(self) -> List[List[str]]:
        """Находит циклические зависимости в графе."""
        print("🔄 Поиск циклических зависимостей...")
        
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Найден цикл
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.module_graph.get(node, set()):
                if neighbor in self.module_graph:  # Только если модуль существует
                    dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        # Запускаем DFS для всех узлов
        for node in self.module_graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def generate_report(self) -> str:
        """Генерирует подробный отчет об анализе импортов."""
        cycles = self.find_cycles()
        
        report = []
        report.append("# 📊 Отчет об анализе структуры импортов")
        report.append("")
        report.append(f"**Дата анализа:** {Path.cwd()}")
        report.append(f"**Проанализировано файлов:** {len(self.python_files)}")
        report.append(f"**Модулей в графе:** {len(self.module_graph)}")
        report.append(f"**Найдено циклов:** {len(cycles)}")
        report.append("")
        
        # Общая статистика
        report.append("## 📈 Общая статистика")
        report.append("")
        
        total_imports = sum(len(imports) for imports in self.file_imports.values())
        report.append(f"- **Всего импортов:** {total_imports}")
        
        modules_with_imports = len([m for m in self.file_imports.values() if m])
        report.append(f"- **Модулей с импортами:** {modules_with_imports}")
        
        # Топ модулей по количеству импортов
        report.append("")
        report.append("### 🔝 Топ модулей по количеству зависимостей")
        report.append("")
        
        sorted_modules = sorted(
            self.file_imports.items(), 
            key=lambda x: len(x[1]), 
            reverse=True
        )[:10]
        
        for module, imports in sorted_modules:
            report.append(f"- **{module}**: {len(imports)} импортов")
        
        # Циклические зависимости
        if cycles:
            report.append("")
            report.append("## 🔄 Циклические зависимости")
            report.append("")
            report.append("⚠️ **КРИТИЧЕСКИЕ ПРОБЛЕМЫ:** Обнаружены циклические зависимости!")
            report.append("")
            
            for i, cycle in enumerate(cycles, 1):
                report.append(f"### Цикл {i}")
                report.append("")
                cycle_str = " → ".join(cycle)
                report.append(f"```")
                report.append(cycle_str)
                report.append("```")
                report.append("")
                
                # Рекомендации по устранению
                report.append("**Рекомендации по устранению:**")
                self._add_cycle_recommendations(report, cycle)
                report.append("")
        
        # Структура зависимостей
        report.append("## 🏗️ Анализ структуры")
        report.append("")
        
        framework_deps = self._analyze_framework_deps()
        if framework_deps:
            report.append("### Framework зависимости")
            report.append("")
            for module, deps in framework_deps.items():
                report.append(f"- **{module}**: {', '.join(deps)}")
            report.append("")
        
        # Рекомендации по оптимизации
        report.append("## 💡 Рекомендации по оптимизации")
        report.append("")
        
        if cycles:
            report.append("### 🎯 Приоритет 1: Устранение циклических зависимостей")
            report.append("")
            report.append("1. **Создать общие интерфейсы** - вынести общие типы и интерфейсы")
            report.append("2. **Инверсия зависимостей** - использовать dependency injection")
            report.append("3. **Разделить модули** - выделить независимые компоненты")
            report.append("")
        
        report.append("### 🔧 Общие улучшения")
        report.append("")
        report.append("1. **Ленивые импорты** - импорт внутри функций для тяжелых зависимостей")
        report.append("2. **Условные импорты** - try/except для опциональных зависимостей")
        report.append("3. **Модульная архитектура** - четкое разделение слоев приложения")
        report.append("")
        
        return "\n".join(report)
    
    def _add_cycle_recommendations(self, report: List[str], cycle: List[str]) -> None:
        """Добавляет рекомендации по устранению конкретного цикла."""
        report.append("")
        
        # Анализируем тип цикла
        if any('db_helpers' in module for module in cycle):
            report.append("- **Проблема**: Циклический импорт в database модулях")
            report.append("- **Решение**: Перенести общие типы в отдельный модуль")
            report.append("- **Действие**: Создать `framework/types/` для общих типов БД")
        
        if any('auth' in module for module in cycle):
            report.append("- **Проблема**: Циклический импорт в auth модулях")
            report.append("- **Решение**: Использовать ленивые импорты или инверсию зависимостей")
            report.append("- **Действие**: Перенести импорты внутрь функций")
    
    def _analyze_framework_deps(self) -> Dict[str, List[str]]:
        """Анализирует зависимости framework модулей."""
        framework_deps = {}
        
        for module, imports in self.file_imports.items():
            if module.startswith('framework'):
                framework_imports = [imp for imp in imports if imp.startswith('framework')]
                if framework_imports:
                    framework_deps[module] = framework_imports
        
        return framework_deps


def main():
    """Главная функция анализа."""
    project_root = Path.cwd()
    
    print("🚀 Запуск анализа структуры импортов")
    print(f"📂 Корневая директория: {project_root}")
    print("=" * 50)
    
    analyzer = ImportAnalyzer(project_root)
    
    # Выполняем анализ
    analyzer.scan_project()
    analyzer.build_dependency_graph()
    
    # Генерируем отчет
    report = analyzer.generate_report()
    
    # Сохраняем отчет
    report_path = project_root / "imports_analysis_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("=" * 50)
    print(f"✅ Анализ завершен!")
    print(f"📋 Отчет сохранен: {report_path}")
    
    # Выводим краткую сводку
    cycles = analyzer.find_cycles()
    if cycles:
        print(f"⚠️ Обнаружено циклических зависимостей: {len(cycles)}")
        print("🔧 Требуется рефакторинг для устранения циклов")
    else:
        print("✅ Циклических зависимостей не обнаружено")


if __name__ == "__main__":
    main() 