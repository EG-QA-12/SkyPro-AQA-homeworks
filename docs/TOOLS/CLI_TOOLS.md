# 🛠️ CLI ИНСТРУМЕНТЫ

## 📋 ОБЗОР

Командная строка и утилиты для работы с фреймворком автотестов.

## 🚀 ОСНОВНЫЕ СКРИПТЫ

### 1. Запуск тестов

#### Быстрый запуск (`scripts/run_tests_quick.bat`)
```batch
@echo off
REM Быстрый запуск тестов (~15 секунд)
python -m pytest tests/integration/test_auth_quick.py -v --tb=short
```

**Использование:**
```bash
# Windows
scripts\run_tests_quick.bat

# Linux/macOS
./scripts/run_tests_quick.bat
```

#### Параллельный запуск (`scripts/run_tests_parallel.bat`)
```batch
@echo off
REM Параллельный запуск тестов (~20 секунд)
python -m pytest tests/integration/ -n 10 -v --tb=short
```

**Использование:**
```bash
# Windows
scripts\run_tests_parallel.bat

# Linux/macOS
./scripts/run_tests_parallel.bat
```

#### Запуск с Allure (`scripts/run_tests_allure.bat`)
```batch
@echo off
REM Запуск тестов с генерацией Allure отчета
python -m pytest tests/integration/ --alluredir=allure-results -v --tb=short
allure serve allure-results
```

**Использование:**
```bash
# Windows
scripts\run_tests_allure.bat

# Linux/macOS
./scripts/run_tests_allure.bat
```

### 2. Скрипты авторизации

#### Тестирование кук (`scripts/run_auth_tests.py`)
```python
#!/usr/bin/env python3
"""
Скрипт для тестирования авторизации и кук.
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

def run_auth_tests():
    """Запуск тестов авторизации."""
    print("🚀 Запуск тестов авторизации...")
    
    # Запускаем тесты авторизации
    exit_code = pytest.main([
        "tests/auth/",
        "-v",
        "--tb=short",
        "-m", "auth"
    ])
    
    return exit_code

if __name__ == "__main__":
    sys.exit(run_auth_tests())
```

**Использование:**
```bash
# Запуск тестов авторизации
python scripts/run_auth_tests.py

# Запуск с конкретными маркерами
python scripts/run_auth_tests.py -m "api and auth"
```

#### Быстрый тест SSO (`scripts/run_sso_tests_fast.bat`)
```batch
@echo off
REM Быстрый тест SSO авторизации
python -m pytest tests/integration/sso/ -v --tb=short -n 4
```

**Использование:**
```bash
# Windows
scripts\run_sso_tests_fast.bat

# Linux/macOS
./scripts/run_sso_tests_fast.bat
```

### 3. Скрипты сбора данных

#### Сбор ссылок бургер-меню (`scripts/collect_burger_links.py`)
```python
#!/usr/bin/env python3
"""
Скрипт для сбора ссылок из бургер-меню.
"""

import csv
import asyncio
from playwright.async_api import async_playwright

async def collect_burger_menu_links():
    """Сбор ссылок из бургер-меню."""
    
    print("🔍 Начинаем сбор ссылок из бургер-меню...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Переходим на главную страницу
        await page.goto("https://bll.by/", wait_until="networkidle")
        
        # Открываем бургер-меню
        burger_button = page.locator("a.menu-btn.menu-btn_new")
        await burger_button.wait_for(state="visible", timeout=5000)
        await burger_button.click()
        
        # Ждем загрузки меню
        menu = page.locator(".burger-menu-content")
        await menu.wait_for(state="visible", timeout=3000)
        
        # Собираем ссылки
        links = await page.locator("a.menu_item_link").all()
        
        # Сохраняем в CSV
        with open("scripts/data/burger_menu_links.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["link_text", "href"])
            
            for link in links:
                text = await link.text_content()
                href = await link.get_attribute("href")
                writer.writerow([text.strip(), href])
        
        await browser.close()
        
        print(f"✅ Собрано {len(links)} ссылок из бургер-меню")

if __name__ == "__main__":
    asyncio.run(collect_burger_menu_links())
```

**Использование:**
```bash
# Сбор ссылок бургер-меню
python scripts/collect_burger_links.py

# Результат сохраняется в scripts/data/burger_menu_links.csv
```

#### Сбор заголовков H1 (`scripts/collect_burger_menu_h1_titles.py`)
```python
#!/usr/bin/env python3
"""
Скрипт для сбора заголовков H1 со страниц бургер-меню.
"""

import csv
import asyncio
from playwright.async_api import async_playwright

async def collect_h1_titles():
    """Сбор заголовков H1 со страниц бургер-меню."""
    
    print("🔍 Начинаем сбор заголовков H1...")
    
    # Читаем ссылки из CSV
    links = []
    with open("scripts/data/burger_menu_links.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        links = [(row["link_text"], row["href"]) for row in reader]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Сохраняем результаты
        results = []
        
        for link_text, href in links[:10]:  # Проверяем первые 10 ссылок
            try:
                page = await browser.new_page()
                
                # Добавляем параметр сессии для headless режима
                url = f"https://bll.by{href}?allow-session=2" if href.startswith("/") else f"{href}?allow-session=2"
                await page.goto(url, wait_until="networkidle", timeout=10000)
                
                # Ищем заголовок H1
                h1_elements = await page.locator("h1").all()
                h1_text = ""
                if h1_elements:
                    h1_text = await h1_elements[0].text_content()
                
                results.append({
                    "link_text": link_text,
                    "href": href,
                    "h1_title": h1_text.strip() if h1_text else "",
                    "found": bool(h1_text)
                })
                
                await page.close()
                
            except Exception as e:
                results.append({
                    "link_text": link_text,
                    "href": href,
                    "h1_title": f"Ошибка: {str(e)}",
                    "found": False
                })
        
        await browser.close()
        
        # Сохраняем результаты в CSV
        with open("scripts/data/burger_menu_h1_titles.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["link_text", "href", "h1_title", "found"])
            
            for result in results:
                writer.writerow([
                    result["link_text"],
                    result["href"],
                    result["h1_title"],
                    result["found"]
                ])
        
        print(f"✅ Обработано {len(results)} ссылок")

if __name__ == "__main__":
    asyncio.run(collect_h1_titles())
```

**Использование:**
```bash
# Сбор заголовков H1
python scripts/collect_burger_menu_h1_titles.py

# Результат сохраняется в scripts/data/burger_menu_h1_titles.csv
```

## 🔧 ИНСТРУМЕНТЫ ДИАГНОСТИКИ

### 1. Проверка качества кук (`scripts/cookie_quality_check.py`)
```python
#!/usr/bin/env python3
"""
Скрипт для проверки качества и валидности кук.
"""

import os
import json
from pathlib import Path
from framework.auth import AuthManager, validate_cookie

def check_cookie_quality():
    """Проверка качества кук."""
    
    print("🔍 Проверка качества кук...")
    
    # Проверяем куки для всех ролей
    roles = ["admin", "moderator", "user"]
    manager = AuthManager()
    
    results = []
    
    for role in roles:
        print(f"\nПроверка куки для роли: {role}")
        
        # Получаем куку
        cookie = manager.get_session_cookie(role)
        
        if cookie:
            # Валидация куки
            is_valid = validate_cookie(cookie)
            length = len(cookie)
            
            results.append({
                "role": role,
                "cookie_present": True,
                "is_valid": is_valid,
                "length": length,
                "quality": "Хорошая" if is_valid and length > 50 else "Плохая"
            })
            
            print(f"  ✅ Кука присутствует: {is_valid}")
            print(f"  📏 Длина куки: {length}")
            print(f"  🎯 Качество: {'Хорошая' if is_valid and length > 50 else 'Плохая'}")
        else:
            results.append({
                "role": role,
                "cookie_present": False,
                "is_valid": False,
                "length": 0,
                "quality": "Отсутствует"
            })
            print(f"  ❌ Кука отсутствует")
    
    # Сохраняем результаты
    with open("scripts/data/cookie_quality_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Проверка завершена. Результаты сохранены в scripts/data/cookie_quality_report.json")

if __name__ == "__main__":
    check_cookie_quality()
```

**Использование:**
```bash
# Проверка качества кук
python scripts/cookie_quality_check.py

# Результат сохраняется в scripts/data/cookie_quality_report.json
```

### 2. Диагностика бургер-меню (`scripts/diagnose_burger_menu.py`)
```python
#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с бургер-меню.
"""

import asyncio
from playwright.async_api import async_playwright

async def diagnose_burger_menu():
    """Диагностика бургер-меню."""
    
    print("🔍 Диагностика бургер-меню...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # 1. Переход на главную страницу
            print("1. Переход на главную страницу...")
            await page.goto("https://bll.by/", wait_until="networkidle")
            
            # 2. Проверка наличия кнопки бургер-меню
            print("2. Проверка наличия кнопки бургер-меню...")
            burger_button = page.locator("a.menu-btn.menu-btn_new")
            
            try:
                await burger_button.wait_for(state="visible", timeout=5000)
                print("   ✅ Кнопка бургер-меню найдена")
            except:
                print("   ❌ Кнопка бургер-меню не найдена")
                return
            
            # 3. Клик по кнопке бургер-меню
            print("3. Клик по кнопке бургер-меню...")
            await burger_button.click()
            
            # 4. Проверка открытия меню
            print("4. Проверка открытия меню...")
            menu = page.locator(".burger-menu-content")
            
            try:
                await menu.wait_for(state="visible", timeout=3000)
                print("   ✅ Меню открылось")
            except:
                print("   ❌ Меню не открылось")
                return
            
            # 5. Проверка наличия ссылок
            print("5. Проверка наличия ссылок...")
            links = await page.locator("a.menu_item_link").all()
            print(f"   📎 Найдено {len(links)} ссылок")
            
            # 6. Проверка кликабельности ссылок
            print("6. Проверка кликабельности ссылок...")
            clickable_count = 0
            
            for i, link in enumerate(links[:5]):  # Проверяем первые 5 ссылок
                try:
                    await link.wait_for(state="visible", timeout=1000)
                    await link.hover(timeout=1000)
                    clickable_count += 1
                except:
                    pass
            
            print(f"   👆 Кликабельны {clickable_count} из {min(5, len(links))} ссылок")
            
        finally:
            await browser.close()
        
        print("\n✅ Диагностика завершена!")

if __name__ == "__main__":
    asyncio.run(diagnose_burger_menu())
```

**Использование:**
```bash
# Диагностика бургер-меню
python scripts/diagnose_burger_menu.py
```

## 🛠️ ИНСТРУМЕНТЫ ОБСЛУЖИВАНИЯ

### 1. Тестер кук (`scripts/maintenance/cookie_tester.py`)
```python
#!/usr/bin/env python3
"""
Инструмент для тестирования и проверки кук.
"""

import argparse
import json
from pathlib import Path
from framework.auth import AuthManager, get_session_cookie, get_auth_cookies

class CookieTester:
    """Тестер кук."""
    
    def __init__(self):
        self.manager = AuthManager()
    
    def test_single_role(self, role: str) -> dict:
        """Тестирование куки для одной роли."""
        
        print(f"🔍 Тестирование куки для роли: {role}")
        
        # Получаем куку через менеджер
        manager_cookie = self.manager.get_session_cookie(role)
        
        # Получаем куку через удобную функцию
        simple_cookie = get_session_cookie(role)
        
        # Получаем куки для Playwright
        playwright_cookies = get_auth_cookies(role)
        
        result = {
            "role": role,
            "manager_cookie": manager_cookie,
            "simple_cookie": simple_cookie,
            "playwright_cookies": playwright_cookies,
            "manager_cookie_length": len(manager_cookie) if manager_cookie else 0,
            "simple_cookie_length": len(simple_cookie) if simple_cookie else 0,
            "playwright_cookies_count": len(playwright_cookies),
            "all_methods_match": manager_cookie == simple_cookie if manager_cookie and simple_cookie else False
        }
        
        # Выводим результаты
        print(f"  📊 Менеджер: {'✅' if manager_cookie else '❌'} ({len(manager_cookie) if manager_cookie else 0} символов)")
        print(f"  📊 Простая функция: {'✅' if simple_cookie else '❌'} ({len(simple_cookie) if simple_cookie else 0} символов)")
        print(f"  📊 Playwright: {'✅' if playwright_cookies else '❌'} ({len(playwright_cookies)} кук)")
        print(f"  🎯 Все методы совпадают: {'✅' if manager_cookie == simple_cookie else '❌'}")
        
        return result
    
    def test_all_roles(self, roles: list) -> list:
        """Тестирование кук для всех ролей."""
        
        print("🔍 Тестирование кук для всех ролей...")
        print("=" * 50)
        
        results = []
        
        for role in roles:
            result = self.test_single_role(role)
            results.append(result)
            print("-" * 30)
        
        # Общий отчет
        print("\n📊 Общий отчет:")
        valid_cookies = sum(1 for r in results if r["manager_cookie"])
        total_roles = len(results)
        
        print(f"  ✅ Валидные куки: {valid_cookies}/{total_roles}")
        print(f"  📈 Процент успеха: {valid_cookies/total_roles*100:.1f}%")
        
        return results
    
    def save_results(self, results: list, filename: str = "cookie_test_results.json"):
        """Сохранение результатов в файл."""
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Результаты сохранены в {filename}")

def main():
    """Основная функция."""
    
    parser = argparse.ArgumentParser(description="Тестер кук")
    parser.add_argument("--roles", nargs="+", default=["admin", "moderator", "user"],
                        help="Роли для тестирования")
    parser.add_argument("--output", default="cookie_test_results.json",
                        help="Файл для сохранения результатов")
    
    args = parser.parse_args()
    
    tester = CookieTester()
    results = tester.test_all_roles(args.roles)
    tester.save_results(results, args.output)

if __name__ == "__main__":
    main()
```

**Использование:**
```bash
# Тестирование всех ролей
python scripts/maintenance/cookie_tester.py

# Тестирование конкретных ролей
python scripts/maintenance/cookie_tester.py --roles admin moderator

# Сохранение в другой файл
python scripts/maintenance/cookie_tester.py --output my_results.json
```

### 2. Инспектор базы данных (`scripts/maintenance/db_inspector.py`)
```python
#!/usr/bin/env python3
"""
Инструмент для инспекции базы данных тестов.
"""

import sqlite3
import json
from pathlib import Path
from framework.utils.db_helpers import DatabaseHelper

class DatabaseInspector:
    """Инспектор базы данных."""
    
    def __init__(self, db_path: str = "test_results.db"):
        self.db_path = db_path
        self.helper = DatabaseHelper(db_path)
    
    def inspect_tables(self):
        """Инспекция таблиц базы данных."""
        
        print("🔍 Инспекция таблиц базы данных...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Получаем список таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"📋 Найдено таблиц: {len(tables)}")
            
            for table_name, in tables:
                print(f"\nТаблица: {table_name}")
                print("-" * 30)
                
                # Получаем структуру таблицы
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                print("Структура:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")
                
                # Получаем количество записей
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"  Записей: {count}")
                
                # Показываем первые 3 записи
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                    rows = cursor.fetchall()
                    print("  Примеры записей:")
                    for i, row in enumerate(rows):
                        print(f"    {i+1}. {dict(zip([col[1] for col in columns], row))}")
        
        finally:
            conn.close()
    
    def export_table(self, table_name: str, output_file: str):
        """Экспорт таблицы в JSON."""
        
        print(f"📤 Экспорт таблицы {table_name} в {output_file}...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Получаем структуру таблицы
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Получаем все записи
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            # Преобразуем в JSON
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
            
            # Сохраняем в файл
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Экспортировано {len(data)} записей")
        
        finally:
            conn.close()
    
    def run_queries(self, queries: list):
        """Выполнение произвольных SQL запросов."""
        
        print("🔍 Выполнение SQL запросов...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for i, query in enumerate(queries):
                print(f"\nЗапрос {i+1}: {query}")
                print("-" * 40)
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if rows:
                    # Получаем имена колонок
                    column_names = [description[0] for description in cursor.description]
                    print("Результаты:")
                    
                    # Выводим заголовки
                    print(" | ".join(column_names))
                    print("-" * (len(" | ".join(column_names))))
                    
                    # Выводим данные
                    for row in rows[:10]:  # Показываем первые 10 строк
                        print(" | ".join(str(cell) for cell in row))
                    
                    if len(rows) > 10:
                        print(f"... и еще {len(rows) - 10} записей")
                else:
                    print("Нет результатов")
        
        finally:
            conn.close()

def main():
    """Основная функция."""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Инспектор базы данных")
    parser.add_argument("--inspect", action="store_true", help="Инспекция таблиц")
    parser.add_argument("--export-table", help="Экспорт таблицы в JSON")
    parser.add_argument("--export-file", default="export.json", help="Файл для экспорта")
    parser.add_argument("--query", nargs="+", help="SQL запросы для выполнения")
    
    args = parser.parse_args()
    
    inspector = DatabaseInspector()
    
    if args.inspect:
        inspector.inspect_tables()
    
    if args.export_table:
        inspector.export_table(args.export_table, args.export_file)
    
    if args.query:
        inspector.run_queries(args.query)

if __name__ == "__main__":
    main()
```

**Использование:**
```bash
# Инспекция таблиц
python scripts/maintenance/db_inspector.py --inspect

# Экспорт таблицы
python scripts/maintenance/db_inspector.py --export-table test_results --export-file results.json

# Выполнение SQL запроса
python scripts/maintenance/db_inspector.py --query "SELECT COUNT(*) FROM test_results" "SELECT * FROM test_results LIMIT 5"
```

## 🎯 ГЕНЕРАТОРЫ ДАННЫХ

### 1. Гибкая авторизация (`scripts/maintenance/flexible_auth.py`)
```python
#!/usr/bin/env python3
"""
Гибкий инструмент авторизации с поддержкой различных сценариев.
"""

import argparse
import json
from framework.auth import AuthManager, get_session_cookie

class FlexibleAuth:
    """Гибкая авторизация."""
    
    def __init__(self):
        self.manager = AuthManager()
    
    def authenticate_with_scenario(self, scenario: str, role: str = "admin") -> dict:
        """Авторизация с определенным сценарием."""
        
        scenarios = {
            "quick": self.quick_auth,
            "thorough": self.thorough_auth,
            "force_refresh": self.force_refresh_auth,
            "cache_only": self.cache_only_auth
        }
        
        if scenario not in scenarios:
            raise ValueError(f"Неизвестный сценарий: {scenario}")
        
        return scenarios[scenario](role)
    
    def quick_auth(self, role: str) -> dict:
        """Быстрая авторизация (использует кэш)."""
        
        print(f"⚡ Быстрая авторизация для роли: {role}")
        
        cookie = self.manager.get_session_cookie(role, force_refresh=False)
        
        return {
            "role": role,
            "cookie": cookie,
            "method": "quick",
            "success": cookie is not None,
            "cookie_length": len(cookie) if cookie else 0
        }
    
    def thorough_auth(self, role: str) -> dict:
        """Тщательная авторизация (принудительное обновление)."""
        
        print(f"🔬 Тщательная авторизация для роли: {role}")
        
        cookie = self.manager.get_session_cookie(role, force_refresh=True)
        
        return {
            "role": role,
            "cookie": cookie,
            "method": "thorough",
            "success": cookie is not None,
            "cookie_length": len(cookie) if cookie else 0
        }
    
    def force_refresh_auth(self, role: str) -> dict:
        """Авторизация с принудительным обновлением."""
        
        print(f"🔄 Авторизация с принудительным обновлением для роли: {role}")
        
        # Очищаем кэш для роли
        self.manager.clear_cache(role)
        
        # Получаем новую куку
        cookie = self.manager.get_session_cookie(role)
        
        return {
            "role": role,
            "cookie": cookie,
            "method": "force_refresh",
            "success": cookie is not None,
            "cookie_length": len(cookie) if cookie else 0,
            "cache_cleared": True
        }
    
    def cache_only_auth(self, role: str) -> dict:
        """Авторизация только из кэша (без API-логина)."""
        
        print(f"💾 Авторизация только из кэша для роли: {role}")
        
        # Проверяем только кэш
        if self.manager._is_cache_valid(role):
            cookie = self.manager._cache[role]["cookie"]
        else:
            cookie = None
        
        return {
            "role": role,
            "cookie": cookie,
            "method": "cache_only",
            "success": cookie is not None,
            "cookie_length": len(cookie) if cookie else 0,
            "used_api_login": False
        }
    
    def compare_auth_methods(self, role: str = "admin") -> dict:
        """Сравнение всех методов авторизации."""
        
        print(f"⚖️ Сравнение всех методов авторизации для роли: {role}")
        print("=" * 60)
        
        methods = ["quick", "thorough", "force_refresh", "cache_only"]
        results = {}
        
        for method in methods:
            try:
                result = self.authenticate_with_scenario(method, role)
                results[method] = result
                
                status = "✅" if result["success"] else "❌"
                print(f"{status} {method:15} | {'Есть кука' if result['success'] else 'Нет куки':10} | {result['cookie_length']:4} символов")
                
            except Exception as e:
                print(f"❌ {method:15} | Ошибка: {str(e)[:30]}")
                results[method] = {
                    "role": role,
                    "method": method,
                    "success": False,
                    "error": str(e)
                }
        
        return results

def main():
    """Основная функция."""
    
    parser = argparse.ArgumentParser(description="Гибкая авторизация")
    parser.add_argument("--scenario", choices=["quick", "thorough", "force_refresh", "cache_only", "compare"],
                        default="quick", help="Сценарий авторизации")
    parser.add_argument("--role", default="admin", help="Роль для авторизации")
    parser.add_argument("--output", help="Файл для сохранения результатов")
    
    args = parser.parse_args()
    
    auth = FlexibleAuth()
    
    if args.scenario == "compare":
        results = auth.compare_auth_methods(args.role)
    else:
        results = auth.authenticate_with_scenario(args.scenario, args.role)
    
    # Выводим результаты
    print("\n📊 Результаты:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Сохраняем в файл если указан
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Результаты сохранены в {args.output}")

if __name__ == "__main__":
    main()
```

**Использование:**
```bash
# Быстрая авторизация
python scripts/maintenance/flexible_auth.py --scenario quick --role admin

# Тщательная авторизация
python scripts/maintenance/flexible_auth.py --scenario thorough --role moderator

# Принудительное обновление
python scripts/maintenance/flexible_auth.py --scenario force_refresh --role user

# Только из кэша
python scripts/maintenance/flexible_auth.py --scenario cache_only --role admin

# Сравнение всех методов
python scripts/maintenance/flexible_auth.py --scenario compare --role admin --output auth_comparison.json
```

## 📊 УТИЛИТЫ ДЛЯ ТЕСТИРОВАНИЯ

### 1. Запуск GUI тестов (`scripts/maintenance/run_gui_tests.py`)
```python
#!/usr/bin/env python3
"""
Утилита для запуска GUI тестов с различными конфигурациями.
"""

import argparse
import subprocess
import sys
from pathlib import Path

class GUITestRunner:
    """Запускатель GUI тестов."""
    
    def __init__(self):
        self.base_cmd = ["python", "-m", "pytest"]
    
    def run_with_browser(self, browser: str, headless: bool = True, **kwargs):
        """Запуск тестов с определенным браузером."""
        
        cmd = self.base_cmd.copy()
        
        # Добавляем параметры браузера
        cmd.extend([
            f"--browser={browser}",
            f"--headless={str(headless).lower()}"
        ])
        
        # Добавляем дополнительные параметры
        if kwargs.get("workers"):
            cmd.extend(["-n", str(kwargs["workers"])])
        
        if kwargs.get("markers"):
            cmd.extend(["-m", kwargs["markers"]])
        
        if kwargs.get("verbose"):
            cmd.append("-v")
        
        # Добавляем директорию тестов
        test_dir = kwargs.get("test_dir", "tests/integration/")
        cmd.append(test_dir)
        
        print(f"🚀 Запуск GUI тестов с параметрами:")
        print(f"   Браузер: {browser}")
        print(f"   Headless: {headless}")
        print(f"   Команда: {' '.join(cmd)}")
        print("-" * 50)
        
        # Запускаем тесты
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"📊 Результаты:")
        print(f"   Код возврата: {result.returncode}")
        print(f"   Stdout: {result.stdout[-500:] if result.stdout else 'Пусто'}")
        if result.stderr:
            print(f"   Stderr: {result.stderr[-500:]}")
        
        return result.returncode
    
    def run_cross_browser(self, browsers: list = None, **kwargs):
        """Кросс-браузерное тестирование."""
        
        if browsers is None:
            browsers = ["chromium", "firefox", "webkit"]
        
        print(f"🌐 Кросс-браузерное тестирование: {', '.join(browsers)}")
        print("=" * 60)
        
        results = {}
        
        for browser in browsers:
            print(f"\n🔍 Тестирование в {browser}...")
            print("-" * 30)
            
            return_code = self.run_with_browser(browser, **kwargs)
            results[browser] = return_code
            
            status = "✅" if return_code == 0 else "❌"
            print(f"{status} {browser}: {'Успех' if return_code == 0 else 'Ошибка'}")
        
        # Общий отчет
        print(f"\n📊 Общий отчет:")
        success_count = sum(1 for code in results.values() if code == 0)
        total_count = len(results)
        
        print(f"   Успешно: {success_count}/{total_count}")
        print(f"   Процент успеха: {success_count/total_count*100:.1f}%")
        
        for browser, code in results.items():
            status = "✅" if code == 0 else "❌"
            print(f"   {status} {browser}: {'Успех' if code == 0 else 'Ошибка'}")
        
        return results
    
    def run_with_video_recording(self, **kwargs):
        """Запуск тестов с записью видео."""
        
        cmd = self.base_cmd.copy()
        
        # Добавляем параметры для записи видео
        cmd.extend([
            "--video=on",
            "--video-dir=videos/",
            "--screenshot=on",
            "--screenshot-dir=screenshots/"
        ])
        
        # Добавляем дополнительные параметры
        if kwargs.get("workers"):
            cmd.extend(["-n", str(kwargs["workers"])])
        
        if kwargs.get("markers"):
            cmd.extend(["-m", kwargs["markers"]])
        
        if kwargs.get("verbose"):
            cmd.append("-v")
        
        test_dir = kwargs.get("test_dir", "tests/integration/")
        cmd.append(test_dir)
        
        print(f"📹 Запуск тестов с записью видео...")
        print(f"   Команда: {' '.join(cmd)}")
        
        # Создаем директории для видео и скриншотов
        Path("videos").mkdir(exist_ok=True)
        Path("screenshots").mkdir(exist_ok=True)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"📊 Результаты:")
        print(f"   Код возврата: {result.returncode}")
        print(f"   Видео сохранены в директории videos/")
        print(f"   Скриншоты сохранены в директории screenshots/")
        
        return result.returncode

def main():
    """Основная функция."""
    
    parser = argparse.ArgumentParser(description="Запускатель GUI тестов")
    parser.add_argument("--browser", choices=["chromium", "firefox", "webkit"],
                        help="Браузер для тестирования")
    parser.add_argument("--headless", action="store_true", default=True,
                        help="Запуск в headless режиме")
    parser.add_argument("--gui", action="store_false", dest="headless",
                        help="Запуск с GUI (не headless)")
    parser.add_argument("--cross-browser", action="store_true",
                        help="Кросс-браузерное тестирование")
    parser.add_argument("--browsers", nargs="+", default=["chromium", "firefox", "webkit"],
                        help="Браузеры для кросс-браузерного тестирования")
    parser.add_argument("--video", action="store_true",
                        help="Запись видео тестов")
    parser.add_argument("--workers", type=int, help="Количество параллельных процессов")
    parser.add_argument("--markers", help="Маркеры для фильтрации тестов")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    parser.add_argument("--test-dir", default="tests/integration/", help="Директория с тестами")
    
    args = parser.parse_args()
    
    runner = GUITestRunner()
    
    if args.cross_browser:
        runner.run_cross_browser(args.browsers, workers=args.workers,
                                markers=args.markers, verbose=args.verbose,
                                test_dir=args.test_dir)
    elif args.video:
        runner.run_with_video_recording(workers=args.workers,
                                      markers=args.markers, verbose=args.verbose,
                                      test_dir=args.test_dir)
    elif args.browser:
        runner.run_with_browser(args.browser, headless=args.headless,
                              workers=args.workers, markers=args.markers,
                              verbose=args.verbose, test_dir=args.test_dir)
    else:
        print("⚠️  Укажите параметры запуска. Используйте --help для справки.")

if __name__ == "__main__":
    main()
```

**Использование:**
```bash
# Запуск в Chromium
python scripts/maintenance/run_gui_tests.py --browser chromium --gui

# Кросс-браузерное тестирование
python scripts/maintenance/run_gui_tests.py --cross-browser --browsers chromium firefox

# Запуск с записью видео
python scripts/maintenance/run_gui_tests.py --video --workers 4

# Запуск с фильтрацией по маркерам
python scripts/maintenance/run_gui_tests.py --browser chromium --markers "ui and burger_menu"
```

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

### Связанные документы
- [Начало работы](../GETTING_STARTED.md) - установка и настройка
- [Архитектура](../ARCHITECTURE.md) - понимание структуры
- [Система авторизации](../COMPONENTS/AUTH_SYSTEM.md) - работа с куками
- [Написание тестов](../TESTING/WRITING_TESTS.md) - создание тестов

### Полезные ссылки
- [Playwright CLI](https://playwright.dev/python/docs/cli)
- [Pytest CLI](https://docs.pytest.org/en/stable/usage.html)
- [Allure CLI](https://docs.qameta.io/allure/#_commandline)

При возникновении вопросов по инструментам:
1. Изучите [примеры](../REFERENCES/EXAMPLES.md)
2. Создайте issue в репозитории
3. Обратитесь к Lead SDET Architect
