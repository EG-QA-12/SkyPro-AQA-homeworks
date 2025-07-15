#!/usr/bin/env python3
"""
Скрипт для анализа и консолидации документации проекта.

Этот скрипт:
1. Анализирует все README и документационные файлы
2. Выявляет дублирование контента
3. Предлагает план консолидации
4. Создает улучшенную структуру документации
"""

from pathlib import Path
from typing import Dict, List, Set, Tuple
import re
import hashlib
from collections import defaultdict


def find_documentation_files(root_path: Path) -> List[Path]:
    """Находит все документационные файлы в проекте."""
    doc_files = []
    exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules', 'allure-results'}
    
    patterns = ['README*', '*.md', '*.rst', '*.txt']
    
    for pattern in patterns:
        for doc_file in root_path.rglob(pattern):
            if doc_file.is_file() and not any(excluded in doc_file.parts for excluded in exclude_dirs):
                # Исключаем автогенерированные файлы
                if not any(x in doc_file.name.lower() for x in ['generated', 'auto', 'build', 'dist']):
                    doc_files.append(doc_file)
    
    return sorted(doc_files)


def analyze_document_content(file_path: Path) -> Dict[str, any]:
    """Анализирует содержимое документа."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except:
        content = ""
    
    # Удаляем markdown заголовки для анализа содержимого
    clean_content = re.sub(r'^#+\s*.*$', '', content, flags=re.MULTILINE)
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
    
    # Вычисляем хеш содержимого для поиска дублирования
    content_hash = hashlib.md5(clean_content.encode()).hexdigest()
    
    return {
        'path': file_path,
        'size': len(content),
        'lines': len(content.splitlines()),
        'clean_content': clean_content,
        'content_hash': content_hash,
        'is_empty': len(clean_content) < 50,
        'has_code_examples': bool(re.search(r'```|`[^`]*`', content)),
        'has_installation_info': bool(re.search(r'install|setup|requirements|dependencies', content, re.IGNORECASE)),
        'has_usage_examples': bool(re.search(r'usage|example|run|execute', content, re.IGNORECASE)),
        'is_main_readme': file_path.name.lower() == 'readme.md' and len(file_path.parts) <= 2,
        'contains_deprecated': bool(re.search(r'deprecated|устарел|legacy|old', content, re.IGNORECASE)),
    }


def find_duplicate_content(docs_analysis: List[Dict]) -> Dict[str, List[Path]]:
    """Находит документы с дублирующимся содержимым."""
    content_groups = defaultdict(list)
    
    for analysis in docs_analysis:
        if not analysis['is_empty']:
            content_groups[analysis['content_hash']].append(analysis['path'])
    
    # Возвращаем только группы с дублирующимся содержимым
    duplicates = {hash_val: paths for hash_val, paths in content_groups.items() if len(paths) > 1}
    
    return duplicates


def categorize_documents(docs_analysis: List[Dict]) -> Dict[str, List[Dict]]:
    """Категоризирует документы по типам."""
    categories = {
        'main_docs': [],       # Основные документы проекта
        'module_docs': [],     # Документация модулей
        'guide_docs': [],      # Руководства и гайды
        'deprecated_docs': [], # Устаревшие документы
        'empty_docs': [],      # Пустые или минимальные документы
        'config_docs': [],     # Документация конфигурации
    }
    
    for analysis in docs_analysis:
        path_str = str(analysis['path']).lower()
        
        if analysis['is_empty']:
            categories['empty_docs'].append(analysis)
        elif analysis['contains_deprecated']:
            categories['deprecated_docs'].append(analysis)
        elif analysis['is_main_readme']:
            categories['main_docs'].append(analysis)
        elif any(x in path_str for x in ['config', 'setup', 'install']):
            categories['config_docs'].append(analysis)
        elif any(x in path_str for x in ['guide', 'tutorial', 'how', 'example']):
            categories['guide_docs'].append(analysis)
        else:
            categories['module_docs'].append(analysis)
    
    return categories


def generate_consolidation_plan(root_path: Path, categories: Dict, duplicates: Dict) -> str:
    """Генерирует план консолидации документации."""
    plan = []
    plan.append("# ПЛАН КОНСОЛИДАЦИИ ДОКУМЕНТАЦИИ\n")
    
    # Статистика
    total_docs = sum(len(cat) for cat in categories.values())
    duplicate_count = sum(len(paths) for paths in duplicates.values()) - len(duplicates)
    
    plan.append(f"## 📊 Статистика")
    plan.append(f"- Всего документов: {total_docs}")
    plan.append(f"- Дублирующихся документов: {duplicate_count}")
    plan.append(f"- Пустых документов: {len(categories['empty_docs'])}")
    plan.append(f"- Устаревших документов: {len(categories['deprecated_docs'])}")
    plan.append("")
    
    # Дублирующиеся документы
    if duplicates:
        plan.append("## 🔄 Дублирующиеся документы")
        for i, (hash_val, paths) in enumerate(duplicates.items(), 1):
            plan.append(f"### Группа {i}")
            rel_paths = [str(p.relative_to(root_path)) for p in paths]
            for path in rel_paths:
                plan.append(f"- `{path}`")
            plan.append("**Рекомендация**: Оставить наиболее актуальный, остальные удалить")
            plan.append("")
    
    # Пустые документы
    if categories['empty_docs']:
        plan.append("## 🗑️ Пустые документы для удаления")
        for analysis in categories['empty_docs']:
            rel_path = analysis['path'].relative_to(root_path)
            plan.append(f"- `{rel_path}` ({analysis['lines']} строк)")
        plan.append("")
    
    # Устаревшие документы
    if categories['deprecated_docs']:
        plan.append("## ⚠️ Устаревшие документы")
        for analysis in categories['deprecated_docs']:
            rel_path = analysis['path'].relative_to(root_path)
            plan.append(f"- `{rel_path}` - требует обновления или удаления")
        plan.append("")
    
    # Рекомендации
    plan.append("## 💡 Рекомендации по структуре")
    plan.append("1. **Основная документация** - в корне проекта (README.md)")
    plan.append("2. **Техническая документация** - в папке docs/")
    plan.append("3. **Документация модулей** - рядом с кодом модуля")
    plan.append("4. **Руководства** - в docs/guides/")
    plan.append("5. **Устаревшие документы** - удалить или архивировать")
    
    return "\n".join(plan)


def main():
    """Основная функция анализа документации."""
    project_root = Path(__file__).resolve().parent.parent.parent
    print(f"📚 Анализ документации в: {project_root}")
    
    # Поиск документационных файлов
    doc_files = find_documentation_files(project_root)
    print(f"Найдено {len(doc_files)} документационных файлов")
    
    # Анализ содержимого
    print("\n📖 Анализ содержимого документов:")
    docs_analysis = []
    for doc_file in doc_files:
        analysis = analyze_document_content(doc_file)
        docs_analysis.append(analysis)
        
        rel_path = doc_file.relative_to(project_root)
        status = "📝" if analysis['has_code_examples'] else "📄"
        if analysis['is_empty']:
            status = "🗑️"
        elif analysis['contains_deprecated']:
            status = "⚠️"
        
        print(f"   {status} {rel_path} ({analysis['lines']} строк)")
    
    # Поиск дублирования
    duplicates = find_duplicate_content(docs_analysis)
    if duplicates:
        print(f"\n🔄 Найдено {len(duplicates)} групп дублирующихся документов")
    
    # Категоризация
    categories = categorize_documents(docs_analysis)
    
    # Создание плана консолидации
    plan_content = generate_consolidation_plan(project_root, categories, duplicates)
    plan_path = project_root / "docs_consolidation_plan.md"
    
    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(plan_content)
    
    print(f"\n✅ План консолидации сохранен в: {plan_path}")
    
    # Вывод краткой статистики
    print(f"\n📈 Краткая статистика:")
    for category, items in categories.items():
        if items:
            print(f"   • {category.replace('_', ' ').title()}: {len(items)}")
    
    if duplicates:
        print(f"   • Дублирующихся групп: {len(duplicates)}")


if __name__ == "__main__":
    main() 