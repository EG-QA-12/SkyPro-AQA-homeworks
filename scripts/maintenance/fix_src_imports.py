#!/usr/bin/env python3
"""
Скрипт для исправления устаревших импортов 'from src.' в проекте auth_management.

Этот скрипт заменяет импорты вида:
- from projects.auth_management.config import config → from projects.auth_management.config import config
- from projects.auth_management.user_manager import UserManager → from projects.auth_management.user_manager import UserManager
- etc.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def create_import_mappings() -> Dict[str, str]:
    """Создает маппинг для замены импортов из src на правильные пути."""
    return {
        # Основные модули auth_management
        r"from src\.config import": "from projects.auth_management.config import",
        r"from src\.database import": "from projects.auth_management.database import", 
        r"from src\.user_manager import": "from projects.auth_management.user_manager import",
        r"from src\.auth import": "from projects.auth_management.auth import",
        r"from src\.logger import": "from projects.auth_management.logger import",
        r"from src\.auth_gui import": "from projects.auth_management.auth_gui import",
        r"from src\.auth_playwright import": "from projects.auth_management.auth_playwright import",
        r"from src\.cookies import": "from projects.auth_management.cookies import",
        
        # GUI модули
        r"from src\.gui\.utils\.gui_helpers import": "from projects.auth_management.gui.utils.gui_helpers import",
        r"from src\.gui\.utils\.auth_operations import": "from projects.auth_management.gui.utils.auth_operations import",
        
        # Импорт config модуля
        r"from src\.config import config": "from projects.auth_management.config import config",
    }


def find_python_files(root_path: Path) -> List[Path]:
    """Находит все Python файлы в проекте, исключая системные директории."""
    exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}
    
    python_files = []
    for py_file in root_path.rglob('*.py'):
        # Проверяем, что файл не в исключаемых директориях
        if not any(excluded in py_file.parts for excluded in exclude_dirs):
            python_files.append(py_file)
    
    return python_files


def fix_imports_in_file(file_path: Path, mappings: Dict[str, str]) -> bool:
    """Исправляет импорты в конкретном файле. Возвращает True если были изменения."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Применяем все замены
        for old_pattern, new_import in mappings.items():
            content = re.sub(old_pattern, new_import, content)
        
        # Если были изменения, сохраняем файл
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при обработке {file_path}: {e}")
        return False
    
    return False


def main():
    """Основная функция скрипта."""
    print("🔧 Запуск исправления импортов 'from src.' в проекте...")
    
    # Определяем корень проекта
    project_root = Path(__file__).resolve().parent.parent.parent
    print(f"📁 Корень проекта: {project_root}")
    
    # Получаем маппинг замен
    import_mappings = create_import_mappings()
    
    # Находим все Python файлы
    python_files = find_python_files(project_root)
    print(f"📄 Найдено {len(python_files)} Python файлов")
    
    # Обрабатываем файлы
    fixed_files = []
    for py_file in python_files:
        if fix_imports_in_file(py_file, import_mappings):
            relative_path = py_file.relative_to(project_root)
            fixed_files.append(relative_path)
            print(f"✅ Исправлены импорты в: {relative_path}")
    
    # Выводим результаты
    print(f"\n📊 Результаты:")
    print(f"   • Обработано файлов: {len(python_files)}")
    print(f"   • Исправлено файлов: {len(fixed_files)}")
    
    if fixed_files:
        print(f"\n📋 Список исправленных файлов:")
        for file_path in fixed_files:
            print(f"   • {file_path}")
    else:
        print("ℹ️ Файлы с проблемными импортами не найдены или уже исправлены")
    
    print("✅ Исправление импортов завершено!")


if __name__ == "__main__":
    main() 