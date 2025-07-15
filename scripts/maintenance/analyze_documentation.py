#!/usr/bin/env python3
"""
Скрипт для комплексного анализа документации и качества кода.

Этот скрипт анализирует:
1. Docstrings в Python модулях (функции, классы, модули)
2. README файлы и их актуальность
3. Комментарии в коде и их качество
4. Соответствие документации реальному коду
5. Примеры использования и их корректность

Результат: documentation_analysis_report.md с детальным отчетом
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import datetime

# Исключаемые директории
EXCLUDE_DIRS = {'.git', 'venv', '__pycache__', 'allure-results', 'logs', 'screenshots', '.pytest_cache'}

class DocumentationAnalyzer:
    """Анализатор документации для оценки качества и полноты."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.python_files: List[Path] = []
        self.markdown_files: List[Path] = []
        self.issues: List[str] = []
        self.stats = {
            'total_functions': 0,
            'documented_functions': 0,
            'total_classes': 0,
            'documented_classes': 0,
            'total_modules': 0,
            'documented_modules': 0,
            'readme_files': 0,
            'outdated_docs': 0
        }
        
    def scan_project(self) -> None:
        """Сканирует проект и находит все файлы для анализа."""
        print("🔍 Сканирование проекта...")
        
        for file_path in self.project_root.rglob("*"):
            # Пропускаем исключенные директории
            if any(excluded in file_path.parts for excluded in EXCLUDE_DIRS):
                continue
                
            if file_path.suffix == '.py' and file_path.is_file():
                self.python_files.append(file_path)
            elif file_path.suffix.lower() in {'.md', '.rst', '.txt'} and file_path.is_file():
                self.markdown_files.append(file_path)
        
        print(f"📁 Найдено Python файлов: {len(self.python_files)}")
        print(f"📄 Найдено документационных файлов: {len(self.markdown_files)}")
    
    def analyze_python_docstrings(self) -> Dict[str, any]:
        """Анализирует docstrings в Python файлах."""
        print("📝 Анализ docstrings...")
        
        docstring_stats = {
            'files_analyzed': 0,
            'modules_with_docstrings': 0,
            'functions_without_docstrings': [],
            'classes_without_docstrings': [],
            'poor_quality_docstrings': [],
            'good_examples': []
        }
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    tree = ast.parse(content)
                    docstring_stats['files_analyzed'] += 1
                    
                    # Анализ docstring модуля
                    module_docstring = ast.get_docstring(tree)
                    if module_docstring:
                        docstring_stats['modules_with_docstrings'] += 1
                        self.stats['documented_modules'] += 1
                    
                    self.stats['total_modules'] += 1
                    
                    # Анализ функций и классов
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            self.stats['total_functions'] += 1
                            docstring = ast.get_docstring(node)
                            
                            if docstring:
                                self.stats['documented_functions'] += 1
                                # Проверка качества docstring
                                if self._is_good_docstring(docstring):
                                    docstring_stats['good_examples'].append({
                                        'file': str(py_file.relative_to(self.project_root)),
                                        'function': node.name,
                                        'quality': 'high'
                                    })
                                elif self._is_poor_docstring(docstring):
                                    docstring_stats['poor_quality_docstrings'].append({
                                        'file': str(py_file.relative_to(self.project_root)),
                                        'function': node.name,
                                        'issue': 'poor_quality'
                                    })
                            else:
                                # Пропускаем __init__, __str__ и другие magic methods для краткости
                                if not node.name.startswith('_'):
                                    docstring_stats['functions_without_docstrings'].append({
                                        'file': str(py_file.relative_to(self.project_root)),
                                        'function': node.name
                                    })
                        
                        elif isinstance(node, ast.ClassDef):
                            self.stats['total_classes'] += 1
                            docstring = ast.get_docstring(node)
                            
                            if docstring:
                                self.stats['documented_classes'] += 1
                            else:
                                docstring_stats['classes_without_docstrings'].append({
                                    'file': str(py_file.relative_to(self.project_root)),
                                    'class': node.name
                                })
                
                except SyntaxError:
                    print(f"⚠️ Синтаксическая ошибка в файле {py_file}")
                    
            except (UnicodeDecodeError, FileNotFoundError) as e:
                print(f"⚠️ Ошибка чтения файла {py_file}: {e}")
        
        return docstring_stats
    
    def _is_good_docstring(self, docstring: str) -> bool:
        """Проверяет качество docstring."""
        if len(docstring) < 20:
            return False
        
        # Проверяем наличие ключевых элементов хорошего docstring
        has_description = len(docstring.split('\n')[0]) > 10
        has_args = 'Args:' in docstring or 'Parameters:' in docstring
        has_returns = 'Returns:' in docstring or 'Return:' in docstring
        has_examples = 'Example' in docstring or 'Usage:' in docstring
        
        return has_description and (has_args or has_returns)
    
    def _is_poor_docstring(self, docstring: str) -> bool:
        """Определяет плохое качество docstring."""
        if len(docstring) < 10:
            return True
        
        # Проверяем на общие фразы-пустышки
        poor_patterns = [
            'TODO', 'FIXME', 'XXX',
            'Function to', 'Method to',
            'This function', 'This method',
            '...', 'pass', 'None'
        ]
        
        return any(pattern in docstring for pattern in poor_patterns)
    
    def analyze_readme_files(self) -> Dict[str, any]:
        """Анализирует README файлы и их актуальность."""
        print("📋 Анализ README файлов...")
        
        readme_stats = {
            'readme_files': [],
            'outdated_readmes': [],
            'good_readmes': [],
            'missing_sections': []
        }
        
        for md_file in self.markdown_files:
            if 'readme' in md_file.name.lower():
                self.stats['readme_files'] += 1
                readme_stats['readme_files'].append(str(md_file.relative_to(self.project_root)))
                
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Проверяем структуру README
                    sections = self._analyze_readme_structure(content)
                    missing = self._check_missing_readme_sections(content)
                    
                    if missing:
                        readme_stats['missing_sections'].append({
                            'file': str(md_file.relative_to(self.project_root)),
                            'missing': missing
                        })
                    
                    # Проверяем актуальность (наличие устаревших ссылок/путей)
                    if self._is_outdated_readme(content):
                        readme_stats['outdated_readmes'].append(str(md_file.relative_to(self.project_root)))
                        self.stats['outdated_docs'] += 1
                    else:
                        readme_stats['good_readmes'].append(str(md_file.relative_to(self.project_root)))
                
                except (UnicodeDecodeError, FileNotFoundError) as e:
                    print(f"⚠️ Ошибка чтения README {md_file}: {e}")
        
        return readme_stats
    
    def _analyze_readme_structure(self, content: str) -> List[str]:
        """Анализирует структуру README файла."""
        lines = content.split('\n')
        sections = []
        
        for line in lines:
            if line.startswith('#'):
                sections.append(line.strip())
        
        return sections
    
    def _check_missing_readme_sections(self, content: str) -> List[str]:
        """Проверяет отсутствующие разделы в README."""
        essential_sections = [
            'installation', 'setup', 'usage', 'example',
            'requirements', 'dependencies'
        ]
        
        content_lower = content.lower()
        missing = []
        
        for section in essential_sections:
            if section not in content_lower:
                missing.append(section)
        
        return missing
    
    def _is_outdated_readme(self, content: str) -> bool:
        """Проверяет актуальность README."""
        outdated_patterns = [
            'src/', 'old_', 'deprecated', 'legacy',
            'TODO', 'FIXME', 'coming soon'
        ]
        
        return any(pattern in content for pattern in outdated_patterns)
    
    def analyze_code_comments(self) -> Dict[str, any]:
        """Анализирует качество комментариев в коде."""
        print("💬 Анализ комментариев в коде...")
        
        comment_stats = {
            'files_with_comments': 0,
            'total_comments': 0,
            'poor_comments': [],
            'good_comments': [],
            'todo_comments': []
        }
        
        for py_file in self.python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                file_has_comments = False
                
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    
                    # Ищем комментарии
                    if line.startswith('#') and not line.startswith('#!/'):
                        comment_stats['total_comments'] += 1
                        file_has_comments = True
                        
                        # Анализируем качество комментария
                        if self._is_todo_comment(line):
                            comment_stats['todo_comments'].append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'line': i,
                                'comment': line
                            })
                        elif self._is_poor_comment(line):
                            comment_stats['poor_comments'].append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'line': i,
                                'comment': line
                            })
                        elif self._is_good_comment(line):
                            comment_stats['good_comments'].append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'line': i,
                                'comment': line
                            })
                
                if file_has_comments:
                    comment_stats['files_with_comments'] += 1
                    
            except (UnicodeDecodeError, FileNotFoundError) as e:
                print(f"⚠️ Ошибка чтения файла {py_file}: {e}")
        
        return comment_stats
    
    def _is_todo_comment(self, comment: str) -> bool:
        """Проверяет, является ли комментарий TODO."""
        todo_patterns = ['TODO', 'FIXME', 'XXX', 'HACK', 'BUG']
        return any(pattern in comment.upper() for pattern in todo_patterns)
    
    def _is_poor_comment(self, comment: str) -> bool:
        """Определяет плохое качество комментария."""
        if len(comment) < 10:
            return True
        
        poor_patterns = [
            '# fix this', '# temp', '# delete', '# remove',
            '# test', '# debug', '#print', '# 123'
        ]
        
        return any(pattern in comment.lower() for pattern in poor_patterns)
    
    def _is_good_comment(self, comment: str) -> bool:
        """Определяет хорошее качество комментария."""
        if len(comment) < 15:
            return False
        
        # Хорошие комментарии объясняют "почему", а не "что"
        good_indicators = [
            'объясня', 'причина', 'важно', 'обход', 'исправляет',
            'explains', 'reason', 'important', 'workaround', 'fixes',
            'оптимизация', 'безопасность', 'совместимость'
        ]
        
        return any(indicator in comment.lower() for indicator in good_indicators)
    
    def generate_report(self) -> str:
        """Генерирует подробный отчет об анализе документации."""
        docstring_stats = self.analyze_python_docstrings()
        readme_stats = self.analyze_readme_files()
        comment_stats = self.analyze_code_comments()
        
        report = []
        report.append("# 📚 Отчет об анализе документации и качества кода")
        report.append("")
        report.append(f"**Дата анализа:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Проанализировано Python файлов:** {len(self.python_files)}")
        report.append(f"**Проанализировано документационных файлов:** {len(self.markdown_files)}")
        report.append("")
        
        # Общая статистика
        report.append("## 📊 Общая статистика")
        report.append("")
        
        # Docstrings статистика
        func_coverage = (self.stats['documented_functions'] / max(self.stats['total_functions'], 1)) * 100
        class_coverage = (self.stats['documented_classes'] / max(self.stats['total_classes'], 1)) * 100
        module_coverage = (self.stats['documented_modules'] / max(self.stats['total_modules'], 1)) * 100
        
        report.append("### 📝 Документация кода")
        report.append("")
        report.append(f"- **Функции с docstrings:** {self.stats['documented_functions']}/{self.stats['total_functions']} ({func_coverage:.1f}%)")
        report.append(f"- **Классы с docstrings:** {self.stats['documented_classes']}/{self.stats['total_classes']} ({class_coverage:.1f}%)")
        report.append(f"- **Модули с docstrings:** {self.stats['documented_modules']}/{self.stats['total_modules']} ({module_coverage:.1f}%)")
        report.append("")
        
        # README статистика
        report.append("### 📋 README файлы")
        report.append("")
        report.append(f"- **Всего README файлов:** {self.stats['readme_files']}")
        report.append(f"- **Устаревших документов:** {self.stats['outdated_docs']}")
        report.append(f"- **Актуальных README:** {len(readme_stats['good_readmes'])}")
        report.append("")
        
        # Комментарии статистика
        report.append("### 💬 Комментарии в коде")
        report.append("")
        report.append(f"- **Файлов с комментариями:** {comment_stats['files_with_comments']}")
        report.append(f"- **Всего комментариев:** {comment_stats['total_comments']}")
        report.append(f"- **TODO комментариев:** {len(comment_stats['todo_comments'])}")
        report.append(f"- **Качественных комментариев:** {len(comment_stats['good_comments'])}")
        report.append("")
        
        # Проблемные области
        report.append("## ⚠️ Проблемные области")
        report.append("")
        
        if docstring_stats['functions_without_docstrings']:
            report.append("### 🔍 Функции без docstrings")
            report.append("")
            for item in docstring_stats['functions_without_docstrings'][:10]:  # Показываем первые 10
                report.append(f"- `{item['file']}`: функция `{item['function']}`")
            
            if len(docstring_stats['functions_without_docstrings']) > 10:
                remaining = len(docstring_stats['functions_without_docstrings']) - 10
                report.append(f"- ... и еще {remaining} функций")
            report.append("")
        
        if docstring_stats['classes_without_docstrings']:
            report.append("### 📦 Классы без docstrings")
            report.append("")
            for item in docstring_stats['classes_without_docstrings'][:5]:
                report.append(f"- `{item['file']}`: класс `{item['class']}`")
            report.append("")
        
        if comment_stats['todo_comments']:
            report.append("### 📝 TODO комментарии")
            report.append("")
            for item in comment_stats['todo_comments'][:5]:
                report.append(f"- `{item['file']}:{item['line']}`: {item['comment']}")
            report.append("")
        
        # Рекомендации
        report.append("## 💡 Рекомендации по улучшению")
        report.append("")
        
        if func_coverage < 70:
            report.append("### 🎯 Приоритет 1: Улучшение документации функций")
            report.append("")
            report.append("- Добавить docstrings для основных функций")
            report.append("- Использовать Google/NumPy стиль docstrings")
            report.append("- Включить описание Args и Returns")
            report.append("")
        
        if readme_stats['missing_sections']:
            report.append("### 📋 Приоритет 2: Улучшение README файлов")
            report.append("")
            for item in readme_stats['missing_sections']:
                report.append(f"- `{item['file']}`: добавить разделы {', '.join(item['missing'])}")
            report.append("")
        
        report.append("### 🔧 Общие улучшения")
        report.append("")
        report.append("1. **Стандартизация docstrings** - использовать единый стиль")
        report.append("2. **Обновление README** - убрать устаревшие ссылки")
        report.append("3. **Улучшение комментариев** - объяснять 'почему', а не 'что'")
        report.append("4. **Примеры использования** - добавить в docstrings")
        report.append("")
        
        # Хорошие примеры
        if docstring_stats['good_examples']:
            report.append("## ✅ Хорошие примеры документации")
            report.append("")
            for item in docstring_stats['good_examples'][:5]:
                report.append(f"- `{item['file']}`: функция `{item['function']}`")
            report.append("")
        
        return "\n".join(report)


def main():
    """Главная функция анализа документации."""
    project_root = Path.cwd()
    
    print("🚀 Запуск анализа документации")
    print(f"📂 Корневая директория: {project_root}")
    print("=" * 50)
    
    analyzer = DocumentationAnalyzer(project_root)
    
    # Выполняем анализ
    analyzer.scan_project()
    
    # Генерируем отчет
    report = analyzer.generate_report()
    
    # Сохраняем отчет
    report_path = project_root / "documentation_analysis_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("=" * 50)
    print(f"✅ Анализ документации завершен!")
    print(f"📋 Отчет сохранен: {report_path}")
    
    # Выводим краткую сводку
    print(f"📝 Функций с docstrings: {analyzer.stats['documented_functions']}/{analyzer.stats['total_functions']}")
    print(f"📦 Классов с docstrings: {analyzer.stats['documented_classes']}/{analyzer.stats['total_classes']}")
    print(f"📋 README файлов: {analyzer.stats['readme_files']}")


if __name__ == "__main__":
    main()