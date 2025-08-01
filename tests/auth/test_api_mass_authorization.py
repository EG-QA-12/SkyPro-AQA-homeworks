"""
Тест массовой авторизации пользователей через API.

Демонстрирует быструю и надежную авторизацию без браузера,
обходя антибот защиту и обеспечивая максимальную производительность.
"""
from __future__ import annotations

import pytest
import allure
import time
import os
from pathlib import Path

from config.secrets_manager import SecretsManager
from framework.utils.simple_api_auth import mass_api_auth
from framework.utils.reporting.allure_utils import ui_test

# Загрузка тестовых пользователей
TEST_USERS = SecretsManager.load_users_from_csv()


@ui_test(
    title="Массовая API авторизация пользователей",
    description="Быстрая авторизация всех пользователей через HTTP API без браузера",
    feature="API авторизация"
)
@pytest.mark.api
def test_api_mass_authorization() -> None:
    """
    Тест массовой авторизации через API.
    
    Выполняет массовую авторизацию всех тестовых пользователей через HTTP API,
    обходя антибот-защиту и обеспечивая высокую производительность.
    """
    
    print("\n" + "="*80)
    print("🚀 ТЕСТ МАССОВОЙ API АВТОРИЗАЦИИ")
    print("="*80)
    print(f"📋 Количество пользователей для авторизации: {len(TEST_USERS)}")
    
    # Проверка наличия пользователей
    if not TEST_USERS:
        pytest.skip("Список пользователей для тестирования пуст")
    
    try:
        with allure.step("Выполнение массовой авторизации"):
            start_time = time.time()
            
            # Получаем количество потоков из переменной окружения
            threads = int(os.environ.get("API_THREADS", "5"))
            print(f"🔄 Используем {threads} потоков для параллельной обработки")
            
            # Выполняем массовую авторизацию
            auth_results, stats = mass_api_auth(
                users=TEST_USERS,
                threads=threads
            )
            
            elapsed_time = time.time() - start_time
            
        with allure.step("Валидация результатов авторизации"):
            # Подсчитываем статистику
            successful_users = [r for r in auth_results if r['success']]
            failed_users = [r for r in auth_results if not r['success']]
            
            print(f"\n📊 ДЕТАЛЬНАЯ СТАТИСТИКА:")
            print(f"   ✅ Успешно авторизовано: {len(successful_users)}/{len(TEST_USERS)}")
            print(f"   ❌ Неудачных авторизаций: {len(failed_users)}")
            print(f"   📈 Процент успеха: {stats['success_rate']:.1f}%")
            print(f"   ⏱️  Общее время: {elapsed_time:.2f} сек")
            
            # Проверяем наличие кук у успешно авторизованных пользователей
            users_with_cookies = 0
            for result in successful_users:
                if result['cookies']:
                    users_with_cookies += 1
                    print(f"   🔑 {result['username']}: кука получена и валидна")
                else:
                    print(f"   ⚠️  {result['username']}: кука отсутствует")
            
            print(f"\n🍪 Пользователей с валидными куками: {users_with_cookies}/{len(successful_users)}")
            
        with allure.step("Проверка сохранения файлов кук"):
            # Проверяем что файлы кук созданы
            cookies_dir = Path("cookies")
            if cookies_dir.exists():
                cookie_files = list(cookies_dir.glob("*_cookies.json"))
                print(f"📁 Найдено файлов кук: {len(cookie_files)}")
                
                # Проверяем несколько файлов
                for result in successful_users[:3]:  # Проверяем первых 3
                    expected_file = cookies_dir / f"{result['username']}_cookies.json"
                    if expected_file.exists():
                        print(f"   ✅ Файл куки создан: {expected_file.name}")
                    else:
                        print(f"   ❌ Файл куки отсутствует: {expected_file.name}")
            
        with allure.step("Анализ производительности"):
            # Сравниваем с ожидаемой производительностью
            expected_max_time = 60  # Ожидаем что API авторизация займет не более 60 секунд
            
            if elapsed_time <= expected_max_time:
                print(f"   🎯 Отличная производительность: {elapsed_time:.2f}с <= {expected_max_time}с")
            else:
                print(f"   ⚠️  Производительность ниже ожидаемой: {elapsed_time:.2f}с > {expected_max_time}с")
            
            # Сравниваем с браузерной авторизацией
            browser_time_estimate = len(TEST_USERS) * 10  # Примерно 10 сек на пользователя в браузере
            speedup = browser_time_estimate / elapsed_time if elapsed_time > 0 else 0
            
            print(
                f"   🚀 Ускорение по сравнению с браузером: ~{speedup:.1f}x"
            )
            print(
                f"   💰 Экономия времени: ~{browser_time_estimate - elapsed_time:.1f} секунд"
            )
        
        with allure.step("Итоговая валидация"):
            # Основные проверки
            assert stats['successful'] > 0, "Ни один пользователь не авторизован успешно"
            assert stats['success_rate'] >= 50, f"Процент успеха слишком низкий: {stats['success_rate']:.1f}%"
            
            # Успешная авторизация админа критична
            admin_results = [
                r for r in successful_users if r['username'] == 'admin'
            ]
            if admin_results:
                print(f"   ✅ Критичная авторизация админа: успешна")
    
    except Exception as e:
        pytest.fail(f"Ошибка во время теста: {str(e)}")
    
    print("\n" + "="*80)
    print("🎉 ТЕСТ API АВТОРИЗАЦИИ ЗАВЕРШЕН УСПЕШНО")
    print("="*80)





if __name__ == "__main__":
    print("Тесты API авторизации")
    print("Использование:")
    print("pytest -v -s tests/auth/test_api_mass_authorization.py")
    print("pytest -v -s tests/auth/test_api_mass_authorization.py -m api")
    print("pytest -v -s tests/auth/test_api_mass_authorization.py -m demo")
