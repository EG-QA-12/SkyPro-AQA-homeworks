#!/usr/bin/env python3
"""
Основной скрипт для запуска всех видов тестов в проекте.

Использование:
    python run_tests.py [опции]
    
Примеры:
    python run_tests.py --unit                # Только unit-тесты
    python run_tests.py --integration         # Только интеграционные тесты
    python run_tests.py --e2e                 # Только e2e-тесты
    python run_tests.py --visual              # Только визуальные тесты
    python run_tests.py --all                 # Все тесты
    python run_tests.py --quick               # Быстрый тест системы
"""

import argparse
import subprocess
import sys
from pathlib import Path
import os

# Устанавливаем рабочую директорию
project_root = Path(__file__).parent
os.chdir(project_root)

def run_unit_tests():
    """Запуск unit-тестов."""
    print("🧪 Запуск unit-тестов...")
    cmd = [sys.executable, "-m", "pytest", "tests/unit/", "-v"]
    return subprocess.run(cmd).returncode

def run_integration_tests():
    """Запуск интеграционных тестов."""
    print("🔗 Запуск интеграционных тестов...")
    cmd = [sys.executable, "-m", "pytest", "tests/integration/", "-v"]
    return subprocess.run(cmd).returncode

def run_e2e_tests():
    """Запуск end-to-end тестов."""
    print("🌐 Запуск e2e-тестов...")
    cmd = [sys.executable, "-m", "pytest", "tests/e2e/", "-v"]
    return subprocess.run(cmd).returncode

def run_admin_test():
    """Запуск теста главной страницы под админом."""
    print("👑 Запуск теста главной страницы под админом...")
    cmd = [sys.executable, "tests/e2e/general/test_main_page_admin.py"]
    return subprocess.run(cmd).returncode

def run_visual_tests():
    """Запуск визуальных тестов."""
    print("👁️ Запуск визуальных тестов...")
    cmd = [sys.executable, "tests/visual/test_cookie_auth_visual.py"]
    return subprocess.run(cmd).returncode

def run_quick_test():
    """Запуск быстрого теста системы."""
    print("⚡ Запуск быстрого теста системы...")
    cmd = [sys.executable, "tests/unit/test_auth_quick.py"]
    return subprocess.run(cmd).returncode

def run_cookie_test():
    """Запуск теста авторизации через куки."""
    print("🍪 Запуск теста авторизации через куки...")
    cmd = [sys.executable, "tests/integration/test_cookie_auth.py"]
    return subprocess.run(cmd).returncode

def run_reports():
    """Генерация отчетов."""
    print("📊 Генерация отчетов...")
    cmd = [sys.executable, "reports/cookie_auth_report.py"]
    return subprocess.run(cmd).returncode

def run_all_tests():
    """Запуск всех тестов."""
    print("🚀 Запуск всех тестов...")
    
    results = []
    
    # Unit тесты
    print("\n" + "="*60)
    results.append(("Unit Tests", run_unit_tests()))
    
    # Интеграционные тесты
    print("\n" + "="*60)
    results.append(("Integration Tests", run_integration_tests()))
    
    # E2E тесты
    print("\n" + "="*60)
    results.append(("E2E Tests", run_e2e_tests()))
    
    # Отчеты
    print("\n" + "="*60)
    results.append(("Reports", run_reports()))
    
    # Итоговый отчет
    print("\n" + "="*60)
    print("📋 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    
    failed_tests = []
    for test_name, return_code in results:
        status = "✅ ПРОШЕЛ" if return_code == 0 else "❌ ПРОВАЛЕН"
        print(f"   {test_name}: {status}")
        if return_code != 0:
            failed_tests.append(test_name)
    
    if failed_tests:
        print(f"\n❌ Провалено тестов: {len(failed_tests)} из {len(results)}")
        print(f"Провалены: {', '.join(failed_tests)}")
        return 1
    else:
        print(f"\n🎉 Все тесты прошли успешно! ({len(results)}/{len(results)})")
        return 0

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description="Запуск тестов для auth_project")
    
    parser.add_argument("--unit", action="store_true", help="Запустить unit-тесты")
    parser.add_argument("--integration", action="store_true", help="Запустить интеграционные тесты")
    parser.add_argument("--e2e", action="store_true", help="Запустить e2e-тесты")
    parser.add_argument("--visual", action="store_true", help="Запустить визуальные тесты")
    parser.add_argument("--quick", action="store_true", help="Запустить быстрый тест")
    parser.add_argument("--cookie", action="store_true", help="Запустить тест авторизации через куки")
    parser.add_argument("--reports", action="store_true", help="Сгенерировать отчеты")
    parser.add_argument("--all", action="store_true", help="Запустить все тесты")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        # Если не указано никаких флагов, показываем help
        parser.print_help()
        return 0
    
    return_code = 0
    
    if args.quick:
        return_code = run_quick_test()
    elif args.unit:
        return_code = run_unit_tests()
    elif args.integration:
        return_code = run_integration_tests()
    elif args.e2e:
        return_code = run_e2e_tests()
    elif args.visual:
        return_code = run_visual_tests()
    elif args.cookie:
        return_code = run_cookie_test()
    elif args.reports:
        return_code = run_reports()
    elif args.all:
        return_code = run_all_tests()
    
    return return_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
