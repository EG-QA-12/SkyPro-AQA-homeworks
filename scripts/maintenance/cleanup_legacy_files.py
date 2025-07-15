#!/usr/bin/env python3
"""
Скрипт для анализа и удаления устаревших файлов в проекте.

Этот скрипт:
1. Находит все .bat/.cmd файлы и анализирует их актуальность
2. Выявляет дублирующиеся README файлы
3. Ищет временные и устаревшие файлы
4. Предлагает план очистки с обоснованием
"""

from pathlib import Path
from typing import List, Dict, Set
import re
from datetime import datetime
import os


def find_batch_files(root_path: Path) -> List[Path]:
    """Находит все batch файлы в проекте."""
    batch_files = []
    exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}
    
    for pattern in ['*.bat', '*.cmd']:
        for batch_file in root_path.rglob(pattern):
            if not any(excluded in batch_file.parts for excluded in exclude_dirs):
                batch_files.append(batch_file)
    
    return batch_files


def analyze_batch_file(file_path: Path) -> Dict[str, any]:
    """Анализирует batch файл на предмет актуальности."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except:
        content = ""
    
    analysis = {
        'path': file_path,
        'size': file_path.stat().st_size,
        'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
        'has_python_calls': bool(re.search(r'python\s+', content, re.IGNORECASE)),
        'has_pytest_calls': bool(re.search(r'pytest\s+', content, re.IGNORECASE)),
        'references_removed_files': False,
        'is_duplicate': False,
        'status': 'unknown'
    }
    
    # Проверяем ссылки на несуществующие файлы
    python_files = re.findall(r'python\s+([^\s]+\.py)', content, re.IGNORECASE)
    for py_file in python_files:
        if not (file_path.parent / py_file).exists():
            analysis['references_removed_files'] = True
    
    # Определяем статус
    if analysis['references_removed_files']:
        analysis['status'] = 'broken'
    elif 'temp' in file_path.name.lower() or 'test' in file_path.name.lower():
        analysis['status'] = 'temporary'
    elif analysis['has_python_calls'] or analysis['has_pytest_calls']:
        analysis['status'] = 'active'
    else:
        analysis['status'] = 'legacy'
    
    return analysis


def find_readme_files(root_path: Path) -> List[Path]:
    """Находит все README файлы в проекте."""
    readme_files = []
    exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}
    
    for readme_file in root_path.rglob('README*'):
        if readme_file.is_file() and not any(excluded in readme_file.parts for excluded in exclude_dirs):
            readme_files.append(readme_file)
    
    return readme_files


def analyze_readme_content(file_path: Path) -> Dict[str, any]:
    """Анализирует содержимое README файла."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except:
        content = ""
    
    return {
        'path': file_path,
        'size': len(content),
        'lines': len(content.splitlines()),
        'has_code_examples': bool(re.search(r'```|`.*`', content)),
        'has_setup_instructions': bool(re.search(r'install|setup|установка|настройка', content, re.IGNORECASE)),
        'references_project_structure': bool(re.search(r'framework|tests|projects', content)),
        'is_empty_or_minimal': len(content.strip()) < 100,
        'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
    }


def main():
    """Основная функция анализа и очистки."""
    project_root = Path(__file__).resolve().parent.parent.parent
    print(f"🔍 Анализ устаревших файлов в: {project_root}")
    
    # Анализ batch файлов
    print("\n📁 Анализ batch файлов:")
    batch_files = find_batch_files(project_root)
    batch_analysis = {}
    
    for batch_file in batch_files:
        rel_path = batch_file.relative_to(project_root)
        analysis = analyze_batch_file(batch_file)
        batch_analysis[str(rel_path)] = analysis
        
        status_emoji = {'active': '✅', 'legacy': '⚠️', 'broken': '❌', 'temporary': '🗑️'}
        print(f"   {status_emoji.get(analysis['status'], '❓')} {rel_path} - {analysis['status']}")
        if analysis['references_removed_files']:
            print(f"      ⚠️ Ссылается на несуществующие файлы")
    
    # Анализ README файлов
    print("\n📚 Анализ README файлов:")
    readme_files = find_readme_files(project_root)
    readme_analysis = {}
    
    for readme_file in readme_files:
        rel_path = readme_file.relative_to(project_root)
        analysis = analyze_readme_content(readme_file)
        readme_analysis[str(rel_path)] = analysis
        
        status = "📝 актуальный" if analysis['has_code_examples'] or analysis['has_setup_instructions'] else "❓ проверить"
        if analysis['is_empty_or_minimal']:
            status = "🗑️ минимальный"
            
        print(f"   {status} - {rel_path} ({analysis['lines']} строк)")
    
    # Создание плана очистки
    plan_path = project_root / "legacy_cleanup_plan.md"
    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write("# ПЛАН ОЧИСТКИ УСТАРЕВШИХ ФАЙЛОВ\n\n")
        
        f.write("## 1. Batch файлы для удаления:\n")
        for path, analysis in batch_analysis.items():
            if analysis['status'] in ['broken', 'temporary']:
                f.write(f"- `{path}` - {analysis['status']}\n")
                if analysis['references_removed_files']:
                    f.write(f"  - Ссылается на несуществующие файлы\n")
        
        f.write("\n## 2. README файлы для консолидации:\n")
        minimal_readmes = [path for path, analysis in readme_analysis.items() 
                          if analysis['is_empty_or_minimal']]
        for path in minimal_readmes:
            f.write(f"- `{path}` - минимальное содержимое\n")
        
        f.write("\n## 3. Рекомендации:\n")
        f.write("- Удалить broken/temporary batch файлы\n")
        f.write("- Объединить информацию из минимальных README в основной\n")
        f.write("- Оставить только функциональные скрипты\n")
    
    print(f"\n✅ Анализ завершен! План сохранен в: {plan_path}")
    
    # Статистика
    broken_count = sum(1 for analysis in batch_analysis.values() if analysis['status'] == 'broken')
    temp_count = sum(1 for analysis in batch_analysis.values() if analysis['status'] == 'temporary')
    minimal_readme_count = sum(1 for analysis in readme_analysis.values() if analysis['is_empty_or_minimal'])
    
    print(f"\n📊 Статистика:")
    print(f"   • Broken batch файлов: {broken_count}")
    print(f"   • Temporary batch файлов: {temp_count}")
    print(f"   • Минимальных README: {minimal_readme_count}")
    print(f"   • Всего файлов для очистки: {broken_count + temp_count + minimal_readme_count}")


if __name__ == "__main__":
    main() 