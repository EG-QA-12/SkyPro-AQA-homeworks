# 🔄 РУКОВОДСТВО ПО МИГРАЦИИ

## 📋 ОБЗОР

Пошаговое руководство по миграции с устаревших подходов на новую систему авторизации и фреймворк автотестов.

## 🎯 ЦЕЛИ МИГРАЦИИ

### 1. Упрощение авторизации
- **Было**: 4 разных системы авторизации, дублирующий код
- **Стало**: Единая система авторизации с автоматическим кэшированием

### 2. Улучшение поддержки
- **Было**: Дублирующиеся тесты, разрозненные компоненты
- **Стало**: Модульная архитектура, четкое разделение ответственности

### 3. Повышение надежности
- **Было**: Ручное управление куками, сложная обработка ошибок
- **Стало**: Автоматическая авторизация, интеллектуальное кэширование

## 🚀 ПОШАГОВАЯ МИГРАЦИЯ

### Этап 1: Подготовка

#### 1.1. Резервное копирование
```bash
# Создаем резервную копию текущего состояния
git add .
git commit -m "Резервная копия перед миграцией"
git tag backup/pre-migration
```

#### 1.2. Проверка текущего состояния
```python
# scripts/maintenance/check_current_state.py
import os
from framework.utils.auth_utils import get_session_cookie as old_get_cookie
from framework.utils.auth_cookie_provider import AuthCookieProvider

def check_current_state():
    """Проверка текущего состояния авторизации."""
    
    print("🔍 Проверка текущего состояния...")
    
    # Проверяем старые методы
    roles = ["admin", "moderator", "user"]
    
    for role in roles:
        print(f"\nПроверка роли: {role}")
        
        # Старый метод
        old_cookie = old_get_cookie(role)
        print(f"  Старый метод: {'✅' if old_cookie else '❌'}")
        
        # Провайдер кук
        provider = AuthCookieProvider()
        provider_cookie = provider.get_auth_cookie(role)
        print(f"  Провайдер: {'✅' if provider_cookie else '❌'}")
    
    print("\n✅ Проверка завершена!")

if __name__ == "__main__":
    check_current_state()
```

#### 1.3. Настройка новой системы
```bash
# Убедитесь что переменные окружения настроены
echo "SESSION_COOKIE_ADMIN=ваша_админская_кука" >> .env
echo "SESSION_COOKIE_MODERATOR=ваша_кука_модератора" >> .env
echo "SESSION_COOKIE_USER=ваша_пользовательская_кука" >> .env
```

### Этап 2: Миграция тестов

#### 2.1. Миграция API тестов

**Было (старый подход):**
```python
# tests/integration/test_old_api.py
import pytest
import requests
from framework.utils.auth_utils import get_session_cookie

def test_old_question_creation():
    """Старый подход к созданию вопроса."""
    
    # Ручная настройка сессии
    session_cookie = get_session_cookie("admin")
    session = requests.Session()
    session.cookies.set("test_joint_session", session_cookie)
    
    # Ручная обработка CSRF
    csrf_token = get_csrf_token()  # Отдельная функция
    
    # Отправка запроса
    response = session.post(
        "https://expert.bll.by/questions",
        data={"p": "Тестовый вопрос"},
        headers={"X-CSRF-TOKEN": csrf_token}
    )
    
    assert response.status_code == 200
```

**Стало (новый подход):**
```python
# tests/integration/test_new_api.py
import pytest
from framework.test_bases.api_test_base import APITestBase

class TestQuestionCreation(APITestBase):
    """Новый подход к созданию вопроса."""
    
    @pytest.mark.api
    @pytest.mark.question
    def test_new_question_creation(self):
        """Новый подход к созданию вопроса."""
        
        # Автоматическая авторизация через базовый класс
        # self.admin_client уже авторизован
        
        # Простой вызов метода
        result = self.admin_client.create_test_question("Тестовый вопрос")
        
        # Метод возвращает bool, обработка ошибок внутри
        assert result is True
```

#### 2.2. Миграция UI тестов

**Было (старый подход):**
```python
# tests/integration/test_old_ui.py
import pytest
from playwright.sync_api import sync_playwright
from framework.utils.auth_cookie_provider import get_auth_cookies

@pytest.fixture(scope="session")
def browser():
    """Старый браузер фикстура."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    """Старая страница фикстура."""
    context = browser.new_context()
    # Ручное добавление кук
    context.add_cookies(get_auth_cookies(role="admin"))
    page = context.new_page()
    yield page
    page.close()
    context.close()

def test_old_burger_menu(page):
    """Старый тест бургер-меню."""
    
    # Ручная навигация
    page.goto("https://bll.by/")
    
    # Ручное открытие меню
    burger_button = page.locator("a.menu-btn.menu-btn_new")
    burger_button.wait_for(state="visible")
    burger_button.click()
    
    # Ручная проверка ссылок
    links = page.locator("a.menu_item_link").all()
    assert len(links) > 0
```

**Стало (новый подход):**
```python
# tests/integration/test_new_ui.py
import pytest
from framework.test_bases.ui_test_base import UITestBase

class TestBurgerMenu(UITestBase):
    """Новый тест бургер-меню."""
    
    @pytest.mark.ui
    @pytest.mark.burger_menu
    def test_new_burger_menu(self, page):
        """Новый тест бургер-меню."""
        
        # Автоматическая авторизация через базовый класс
        # page уже авторизована
        
        # Использование встроенных методов
        self.open_burger_menu(page)
        links = self.get_burger_menu_links(page)
        
        assert len(links) > 0
        
        # Использование удобных методов
        for link in links[:3]:
            self.click_burger_menu_link(page, link)
            assert self.verify_page_loaded(page)
```

### Этап 3: Миграция авторизации

#### 3.1. Замена импортов

**Поиск и замена:**
```bash
# Найти все старые импорты
grep -r "from framework.utils.auth_" . --include="*.py"

# Заменить импорты
find . -name "*.py" -exec sed -i 's/from framework.utils.auth_utils import get_session_cookie/from framework.auth import get_session_cookie/g' {} +
find . -name "*.py" -exec sed -i 's/from framework.utils.auth_cookie_provider import AuthCookieProvider/from framework.auth import AuthManager/g' {} +
```

#### 3.2. Обновление вызовов

**Было:**
```python
from framework.utils.auth_utils import get_session_cookie
from framework.utils.auth_cookie_provider import AuthCookieProvider

# Старый способ
cookie = get_session_cookie("admin")

# Старый провайдер
provider = AuthCookieProvider()
cookie = provider.get_auth_cookie("admin")
```

**Стало:**
```python
from framework.auth import get_session_cookie, AuthManager

# Новый способ (обратная совместимость)
cookie = get_session_cookie("admin")

# Новый менеджер
manager = AuthManager()
cookie = manager.get_session_cookie("admin")
```

### Этап 4: Тестирование миграции

#### 4.1. Запуск тестов
```bash
# Запуск мигрированных тестов
python -m pytest tests/integration/test_new_api.py -v
python -m pytest tests/integration/test_new_ui.py -v

# Параллельный запуск
python -m pytest tests/integration/ -n 4 -v --tb=short
```

#### 4.2. Сравнение результатов
```python
# scripts/compare_migration_results.py
import subprocess
import json

def run_tests_and_compare():
    """Запуск тестов до и после миграции."""
    
    print("🔍 Сравнение результатов миграции...")
    
    # Запуск старых тестов (если есть)
    old_result = subprocess.run([
        "python", "-m", "pytest", 
        "tests/integration/test_old_*", 
        "--json-report", "--json-report-file=old_report.json"
    ], capture_output=True, text=True)
    
    # Запуск новых тестов
    new_result = subprocess.run([
        "python", "-m", "pytest", 
        "tests/integration/test_new_*", 
        "--json-report", "--json-report-file=new_report.json"
    ], capture_output=True, text=True)
    
    # Сравнение результатов
    compare_reports("old_report.json", "new_report.json")

def compare_reports(old_file, new_file):
    """Сравнение отчетов тестов."""
    
    with open(old_file) as f:
        old_data = json.load(f)
    
    with open(new_file) as f:
        new_data = json.load(f)
    
    print("📊 Сравнение результатов:")
    print(f"  Старые тесты: {old_data.get('summary', {}).get('passed', 0)} прошли")
    print(f"  Новые тесты: {new_data.get('summary', {}).get('passed', 0)} прошли")
    
    # Сравнение времени выполнения
    old_duration = old_data.get('duration', 0)
    new_duration = new_data.get('duration', 0)
    
    print(f"  Старое время: {old_duration:.2f} сек")
    print(f"  Новое время: {new_duration:.2f} сек")
    print(f"  Разница: {old_duration - new_duration:.2f} сек ({((old_duration - new_duration) / old_duration * 100):.1f}% быстрее)")

if __name__ == "__main__":
    run_tests_and_compare()
```

## 📋 ПОДРОБНЫЕ ПРИМЕРЫ МИГРАЦИИ

### Пример 1: Миграция теста авторизации

**Было:**
```python
# tests/auth/test_old_auth.py
import pytest
import requests
from framework.utils.auth_utils import get_session_cookie

def test_admin_access():
    """Тест доступа администратора."""
    
    # Ручная настройка сессии
    cookie = get_session_cookie("admin")
    if not cookie:
        pytest.fail("Не удалось получить куку администратора")
    
    session = requests.Session()
    session.cookies.set("test_joint_session", cookie)
    
    # Ручной запрос
    response = session.get("https://expert.bll.by/admin/posts")
    
    assert response.status_code == 200
    assert "Панель модерации" in response.text
```

**Стало:**
```python
# tests/auth/test_new_auth.py
import pytest
from framework.test_bases.api_test_base import APITestBase

class TestAdminAccess(APITestBase):
    """Тест доступа администратора."""
    
    @pytest.mark.auth
    @pytest.mark.admin
    def test_admin_access(self):
        """Тест доступа администратора."""
        
        # Автоматическая авторизация
        # self.admin_client уже авторизован
        
        # Простой вызов
        response = self.admin_client.get_moderation_panel()
        
        # Проверки
        assert response.status_code == 200
        assert response.json().get("success") is True
```

### Пример 2: Миграция UI теста

**Было:**
```python
# tests/ui/test_old_burger.py
import pytest
from playwright.sync_api import sync_playwright
from framework.utils.auth_cookie_provider import get_auth_cookies

def test_burger_menu_links():
    """Тест ссылок бургер-меню."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        
        # Ручное добавление кук
        context.add_cookies(get_auth_cookies("admin"))
        page = context.new_page()
        
        # Ручная навигация
        page.goto("https://bll.by/")
        page.locator("a.menu-btn.menu-btn_new").click()
        
        # Ручная проверка
        links = page.locator("a.menu_item_link").all()
        assert len(links) > 0
        
        browser.close()
```

**Стало:**
```python
# tests/ui/test_new_burger.py
import pytest
from framework.test_bases.ui_test_base import UITestBase

class TestBurgerMenuLinks(UITestBase):
    """Тест ссылок бургер-меню."""
    
    @pytest.mark.ui
    @pytest.mark.burger_menu
    def test_burger_menu_links(self, page):
        """Тест ссылок бургер-меню."""
        
        # Автоматическая авторизация
        # page уже авторизована
        
        # Использование встроенных методов
        self.open_burger_menu(page)
        links = self.get_burger_menu_links(page)
        
        assert len(links) > 0
```

## 🛠️ ИНСТРУМЕНТЫ МИГРАЦИИ

### 1. Скрипт автоматической миграции
```python
# scripts/migration/auto_migrate.py
#!/usr/bin/env python3
"""
Скрипт автоматической миграции старых тестов.
"""

import os
import re
from pathlib import Path

class AutoMigrator:
    """Автоматический мигратор."""
    
    def __init__(self):
        self.import_patterns = {
            r'from framework\.utils\.auth_utils import get_session_cookie': 'from framework.auth import get_session_cookie',
            r'from framework\.utils\.auth_cookie_provider import AuthCookieProvider': 'from framework.auth import AuthManager',
            r'from framework\.utils\.smart_auth_manager import SmartAuthManager': 'from framework.auth import AuthManager',
        }
        
        self.usage_patterns = {
            r'get_session_cookie\(': 'get_session_cookie(',
            r'AuthCookieProvider\(\)': 'AuthManager()',
            r'SmartAuthManager\(\)': 'AuthManager()',
        }
    
    def migrate_file(self, file_path: Path) -> bool:
        """Миграция одного файла."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Заменяем импорты
            for old_import, new_import in self.import_patterns.items():
                content = re.sub(old_import, new_import, content)
            
            # Заменяем использования
            for old_usage, new_usage in self.usage_patterns.items():
                content = re.sub(old_usage, new_usage, content)
            
            # Если были изменения, сохраняем
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Ошибка миграции файла {file_path}: {e}")
            return False
    
    def migrate_directory(self, directory: Path) -> int:
        """Миграция директории."""
        
        migrated_count = 0
        
        for py_file in directory.rglob("*.py"):
            if self.migrate_file(py_file):
                print(f"✅ Мигрирован файл: {py_file}")
                migrated_count += 1
        
        return migrated_count

def main():
    """Основная функция."""
    
    migrator = AutoMigrator()
    
    # Мигрируем тесты
    tests_dir = Path("tests")
    if tests_dir.exists():
        count = migrator.migrate_directory(tests_dir)
        print(f"✅ Мигрировано {count} файлов в директории tests/")
    
    # Мигрируем скрипты
    scripts_dir = Path("scripts")
    if scripts_dir.exists():
        count = migrator.migrate_directory(scripts_dir)
        print(f"✅ Мигрировано {count} файлов в директории scripts/")

if __name__ == "__main__":
    main()
```

**Использование:**
```bash
# Автоматическая миграция
python scripts/migration/auto_migrate.py
```

### 2. Проверка совместимости
```python
# scripts/migration/compatibility_check.py
#!/usr/bin/env python3
"""
Проверка совместимости после миграции.
"""

import subprocess
import sys

def check_compatibility():
    """Проверка совместимости."""
    
    print("🔍 Проверка совместимости после миграции...")
    
    # Запуск тестов
    result = subprocess.run([
        "python", "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "-x"  # Остановка при первой ошибке
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Все тесты прошли успешно!")
        print(f"Вывод: {result.stdout[-500:] if result.stdout else 'Пусто'}")
        return True
    else:
        print("❌ Некоторые тесты не прошли:")
        print(f"Код ошибки: {result.returncode}")
        print(f"Stderr: {result.stderr[-500:] if result.stderr else 'Пусто'}")
        return False

def check_imports():
    """Проверка импортов."""
    
    print("🔍 Проверка импортов...")
    
    result = subprocess.run([
        "python", "-c", "import framework.auth; print('✅ Импорты работают')"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Все импорты работают корректно")
        return True
    else:
        print("❌ Ошибки импортов:")
        print(result.stderr)
        return False

def main():
    """Основная функция."""
    
    success = True
    
    # Проверяем импорты
    if not check_imports():
        success = False
    
    # Проверяем тесты
    if not check_compatibility():
        success = False
    
    if success:
        print("\n🎉 Миграция завершена успешно!")
        return 0
    else:
        print("\n❌ Миграция завершена с ошибками!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Использование:**
```bash
# Проверка совместимости
python scripts/migration/compatibility_check.py
```

## 📊 МОНИТОРИНГ МИГРАЦИИ

### 1. Отслеживание прогресса
```python
# scripts/migration/progress_tracker.py
#!/usr/bin/env python3
"""
Отслеживание прогресса миграции.
"""

import json
from pathlib import Path

class MigrationProgress:
    """Прогресс миграции."""
    
    def __init__(self, progress_file: str = "migration_progress.json"):
        self.progress_file = Path(progress_file)
        self.progress = self.load_progress()
    
    def load_progress(self) -> dict:
        """Загрузка прогресса."""
        if self.progress_file.exists():
            with open(self.progress_file) as f:
                return json.load(f)
        return {
            "total_files": 0,
            "migrated_files": 0,
            "failed_files": 0,
            "remaining_files": [],
            "completed_steps": []
        }
    
    def save_progress(self):
        """Сохранение прогресса."""
        with open(self.progress_file, "w") as f:
            json.dump(self.progress, f, indent=2)
    
    def add_completed_step(self, step: str):
        """Добавление завершенного шага."""
        if step not in self.progress["completed_steps"]:
            self.progress["completed_steps"].append(step)
            self.save_progress()
    
    def update_file_stats(self, total: int, migrated: int, failed: int, remaining: list):
        """Обновление статистики файлов."""
        self.progress["total_files"] = total
        self.progress["migrated_files"] = migrated
        self.progress["failed_files"] = failed
        self.progress["remaining_files"] = remaining
        self.save_progress()
    
    def print_report(self):
        """Вывод отчета."""
        print("📊 Отчет о прогрессе миграции:")
        print("=" * 40)
        
        for step in self.progress["completed_steps"]:
            print(f"✅ {step}")
        
        print(f"\n📈 Статистика файлов:")
        print(f"   Всего файлов: {self.progress['total_files']}")
        print(f"   Мигрировано: {self.progress['migrated_files']}")
        print(f"   Ошибки: {self.progress['failed_files']}")
        print(f"   Осталось: {len(self.progress['remaining_files'])}")
        
        if self.progress["remaining_files"]:
            print(f"\n📝 Оставшиеся файлы:")
            for file in self.progress["remaining_files"][:10]:
                print(f"   - {file}")
            if len(self.progress["remaining_files"]) > 10:
                print(f"   ... и еще {len(self.progress['remaining_files']) - 10} файлов")

def main():
    """Основная функция."""
    progress = MigrationProgress()
    progress.print_report()

if __name__ == "__main__":
    main()
```

### 2. Отчет о миграции
```python
# scripts/migration/migration_report.py
#!/usr/bin/env python3
"""
Генерация отчета о миграции.
"""

import json
from datetime import datetime
from pathlib import Path

class MigrationReport:
    """Отчет о миграции."""
    
    def __init__(self):
        self.report = {
            "generated_at": datetime.now().isoformat(),
            "migration_summary": {},
            "file_changes": [],
            "performance_improvements": {},
            "issues_found": [],
            "recommendations": []
        }
    
    def add_summary(self, total_files: int, migrated_files: int, failed_files: int):
        """Добавление сводки."""
        self.report["migration_summary"] = {
            "total_files": total_files,
            "migrated_files": migrated_files,
            "failed_files": failed_files,
            "success_rate": (migrated_files / total_files * 100) if total_files > 0 else 0,
            "completion_date": datetime.now().isoformat()
        }
    
    def add_file_change(self, old_file: str, new_file: str, status: str, notes: str = ""):
        """Добавление изменения файла."""
        self.report["file_changes"].append({
            "old_file": old_file,
            "new_file": new_file,
            "status": status,  # migrated, failed, skipped
            "notes": notes,
            "changed_at": datetime.now().isoformat()
        })
    
    def add_performance_improvement(self, metric: str, old_value: float, new_value: float):
        """Добавление улучшения производительности."""
        improvement = ((old_value - new_value) / old_value * 100) if old_value > 0 else 0
        
        self.report["performance_improvements"][metric] = {
            "old_value": old_value,
            "new_value": new_value,
            "improvement_percent": improvement,
            "measured_at": datetime.now().isoformat()
        }
    
    def add_issue(self, issue_type: str, description: str, severity: str):
        """Добавление проблемы."""
        self.report["issues_found"].append({
            "type": issue_type,
            "description": description,
            "severity": severity,  # critical, high, medium, low
            "reported_at": datetime.now().isoformat()
        })
    
    def add_recommendation(self, recommendation: str, priority: str):
        """Добавление рекомендации."""
        self.report["recommendations"].append({
            "recommendation": recommendation,
            "priority": priority,  # high, medium, low
            "added_at": datetime.now().isoformat()
        })
    
    def generate_html_report(self, output_file: str = "migration_report.html"):
        """Генерация HTML отчета."""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Отчет о миграции</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .success {{ color: green; }}
        .warning {{ color: orange; }}
        .error {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Отчет о миграции</h1>
        <p>Сгенерирован: {self.report['generated_at']}</p>
    </div>
    
    <div class="section">
        <h2>📋 Сводка миграции</h2>
        <p><strong>Всего файлов:</strong> {self.report['migration_summary'].get('total_files', 0)}</p>
        <p class="success"><strong>Мигрировано:</strong> {self.report['migration_summary'].get('migrated_files', 0)}</p>
        <p class="error"><strong>Ошибки:</strong> {self.report['migration_summary'].get('failed_files', 0)}</p>
        <p><strong>Процент успеха:</strong> {self.report['migration_summary'].get('success_rate', 0):.1f}%</p>
    </div>
    
    <div class="section">
        <h2>📈 Улучшения производительности</h2>
        <ul>
        """
        
        for metric, data in self.report["performance_improvements"].items():
            html_content += f"""
            <li><strong>{metric}:</strong> {data['old_value']} → {data['new_value']} ({data['improvement_percent']:.1f}% улучшение)</li>
            """
        
        html_content += """
        </ul>
    </div>
    
    <div class="section">
        <h2>📝 Рекомендации</h2>
        <ul>
        """
        
        for rec in self.report["recommendations"]:
            priority_class = "error" if rec["priority"] == "high" else "warning" if rec["priority"] == "medium" else "success"
            html_content += f"""
            <li class="{priority_class}"><strong>[{rec['priority'].upper()}]</strong> {rec['recommendation']}</li>
            """
        
        html_content += """
        </ul>
    </div>
</body>
</html>
        """
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"✅ HTML отчет сохранен в {output_file}")
    
    def save_json_report(self, output_file: str = "migration_report.json"):
        """Сохранение JSON отчета."""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON отчет сохранен в {output_file}")

def main():
    """Основная функция."""
    
    report = MigrationReport()
    
    # Пример заполнения отчета
    report.add_summary(total_files=50, migrated_files=45, failed_files=5)
    
    report.add_performance_improvement("время_выполнения", 45.0, 25.0)
    report.add_performance_improvement("количество_запросов", 150, 80)
    
    report.add_recommendation("Проверить оставшиеся 5 файлов", "high")
    report.add_recommendation("Обновить документацию", "medium")
    
    # Генерация отчетов
    report.save_json_report()
    report.generate_html_report()

if __name__ == "__main__":
    main()
```

## 🎯 ЛУЧШИЕ ПРАКТИКИ МИГРАЦИИ

### 1. Постепенная миграция
```python
# Не мигрируйте всё сразу!
# ✅ Хорошо - постепенная миграция
class TestGradualMigration(APITestBase):
    def test_new_approach(self):
        """Новый подход с автоматической авторизацией."""
        result = self.admin_client.create_test_question("Новый вопрос")
        assert result is True

# ❌ Плохо - массовая миграция
# Мигрируйте по одному файлу за раз
```

### 2. Обратная совместимость
```python
# framework/auth/__init__.py
from .auth_manager import AuthManager, get_session_cookie, get_auth_cookies
from .cookie_provider import CookieProvider

# Обратная совместимость с старыми импортами
# Старые импорты продолжают работать
def get_session_cookie(role: str = "admin") -> str:
    """Обратная совместимость."""
    return get_session_cookie(role)  # Новый метод
```

### 3. Тестирование на каждом этапе
```bash
# ✅ Хорошо - тестирование после каждой миграции
python -m pytest tests/integration/test_migrated_file.py -v

# Запуск конкретного теста
python -m pytest tests/integration/test_migrated_file.py::TestClass::test_method -v -s

# Параллельный запуск
python -m pytest tests/integration/test_migrated_file.py -n 4 -v
```

## 🔧 РЕШЕНИЕ ЧАСТЫХ ПРОБЛЕМ

### Проблема 1: "ImportError: No module named 'framework.utils.auth_utils'"
**Решение:**
```python
# Замените старый импорт
# Было:
from framework.utils.auth_utils import get_session_cookie

# Стало:
from framework.auth import get_session_cookie
```

### Проблема 2: "AttributeError: 'NoneType' object has no attribute 'strip'"
**Решение:**
```python
# Проверьте валидность кук
from framework.auth import get_session_cookie, validate_cookie

cookie = get_session_cookie("admin")
if cookie and validate_cookie(cookie):
    # Кука валидна
    pass
else:
    # Кука невалидна, нужно обновить
    from framework.auth import AuthManager
    manager = AuthManager()
    cookie = manager.get_session_cookie("admin", force_refresh=True)
```

### Проблема 3: "Session cookie not found"
**Решение:**
```python
# Проверьте переменные окружения
import os

# Убедитесь что куки установлены
admin_cookie = os.getenv("SESSION_COOKIE_ADMIN")
if not admin_cookie:
    print("❌ Кука администратора не найдена в переменных окружения")
    print("🔧 Установите: SESSION_COOKIE_ADMIN=ваша_кука")

# Или используйте файлы кук
# cookies/admin_session.txt - текстовый файл с кукой
# cookies/admin_cookies.json - JSON файл Playwright формата
```

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

### Связанные документы
- [Начало работы](../GETTING_STARTED.md) - установка и настройка
- [Архитектура](../ARCHITECTURE.md) - понимание новой структуры
- [Система авторизации](../COMPONENTS/AUTH_SYSTEM.md) - подробное описание
- [Написание тестов](../TESTING/WRITING_TESTS.md) - новые подходы
- [Лучшие практики](../TESTING/BEST_PRACTICES.md) - рекомендации

### Полезные ссылки
- [Pytest документация](https://docs.pytest.org/)
- [Playwright документация](https://playwright.dev/python/docs/intro)
- [Allure документация](https://docs.qameta.io/allure/)

## 🤝 ПОДДЕРЖКА

При возникновении проблем с миграцией:
1. Проверьте [часто задаваемые вопросы](../REFERENCES/FAQ.md)
2. Изучите [примеры](../REFERENCES/EXAMPLES.md)
3. Создайте issue в репозитории
4. Обратитесь к Lead SDET Architect

**Удачи в миграции! 🚀**
