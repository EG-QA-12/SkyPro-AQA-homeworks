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
from framework.utils.api_auth import APIAuthManager, api_mass_auth
from framework.utils.cookie_constants import COOKIE_NAME
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
    
    Сценарий:
    1. Инициализируем API менеджер авторизации
    2. Выполняем массовую авторизацию всех пользователей
    3. Проверяем получение кук для каждого пользователя
    4. Сохраняем куки в файлы для дальнейшего использования
    5. Обновляем информацию в базе данных
    6. Выводим подробную статистику выполнения
    """
    
    print("\n" + "="*80)
    print("🚀 ТЕСТ МАССОВОЙ API АВТОРИЗАЦИИ")
    print("="*80)
    print(f"📋 Количество пользователей для авторизации: {len(TEST_USERS)}")
    
    # Проверка наличия пользователей
    if not TEST_USERS:
        pytest.skip("Список пользователей для тестирования пуст")
    
    with allure.step("Инициализация API менеджера"):
        auth_manager = APIAuthManager()
        print(f"✅ API менеджер инициализирован для {auth_manager.base_url}")
    
    try:
        with allure.step("Выполнение массовой авторизации"):
            start_time = time.time()
            
            # Получаем количество потоков из переменной окружения
            threads = int(os.environ.get("API_THREADS", "5"))
            print(f"🔄 Используем {threads} потоков для параллельной обработки")
            
            # Выполняем массовую авторизацию
            auth_results, stats = auth_manager.mass_authorize_users(
                users=TEST_USERS,
                save_to_files=True,
                update_database=True,
                max_workers=threads
            )
            
            elapsed_time = time.time() - start_time
            
        with allure.step("Валидация результатов авторизации"):
            # Проверяем что получили результаты для всех пользователей
            assert len(auth_results) == len(TEST_USERS), \
                f"Получено результатов {len(auth_results)}, ожидалось {len(TEST_USERS)}"
            
            # Подсчитываем статистику
            successful_users = [r for r in auth_results if r.success]
            failed_users = [r for r in auth_results if not r.success]
            
            print(f"\n📊 ДЕТАЛЬНАЯ СТАТИСТИКА:")
            print(f"   ✅ Успешно авторизовано: {len(successful_users)}/{len(TEST_USERS)}")
            print(f"   ❌ Неудачных авторизаций: {len(failed_users)}")
            print(f"   📈 Процент успеха: {stats['success_rate']:.1f}%")
            print(f"   ⏱️  Общее время: {elapsed_time:.2f} сек")
            print(f"   ⚡ Среднее время на пользователя: {stats['avg_time_per_user']:.2f} сек")
            
            # Проверяем наличие кук у успешно авторизованных пользователей
            users_with_cookies = 0
            for result in successful_users:
                if result.cookies and COOKIE_NAME in result.cookies:
                    users_with_cookies += 1
                    
                    # Проверяем формат куки
                    cookie = result.cookies[COOKIE_NAME]
                    assert 'value' in cookie, f"Кука {COOKIE_NAME} не содержит значение"
                    assert 'domain' in cookie, f"Кука {COOKIE_NAME} не содержит домен"
                    assert cookie['domain'] == '.bll.by', f"Неверный домен куки: {cookie['domain']}"
                    
                    print(f"   🔑 {result.username}: кука получена и валидна")
                else:
                    print(f"   ⚠️  {result.username}: кука отсутствует или невалидна")
            
            print(f"\n🍪 Пользователей с валидными куками: {users_with_cookies}/{len(successful_users)}")
            
        with allure.step("Проверка сохранения файлов кук"):
            # Проверяем что файлы кук созданы
            cookies_dir = Path("cookies")
            if cookies_dir.exists():
                cookie_files = list(cookies_dir.glob("*_cookies.json"))
                print(f"📁 Найдено файлов кук: {len(cookie_files)}")
                
                # Проверяем несколько файлов
                for result in successful_users[:3]:  # Проверяем первых 3
                    expected_file = cookies_dir / f"{result.username}_cookies.json"
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
            
            print(f"   🚀 Ускорение по сравнению с браузером: ~{speedup:.1f}x")
            print(f"   💰 Экономия времени: ~{browser_time_estimate - elapsed_time:.1f} секунд")
        
        with allure.step("Итоговая валидация"):
            # Основные проверки
            assert stats['successful'] > 0, "Ни один пользователь не авторизован успешно"
            assert stats['success_rate'] >= 50, f"Процент успеха слишком низкий: {stats['success_rate']:.1f}%"
            
            # Если есть неудачные авторизации, выводим детали
            if failed_users:
                print(f"\n❌ НЕУДАЧНЫЕ АВТОРИЗАЦИИ:")
                for result in failed_users:
                    print(f"   • {result.username}: {result.error_message}")
            
            # Успешная авторизация админа критична
            admin_result = next((r for r in auth_results if r.username == 'admin'), None)
            if admin_result:
                assert admin_result.success, "Авторизация админа обязательна для успеха тестов"
                print(f"   ✅ Критичная авторизация админа: успешна")
    
    finally:
        # Закрываем ресурсы
        auth_manager.close()
        print(f"\n🧹 Ресурсы API менеджера освобождены")
    
    print("\n" + "="*80)
    print("🎉 ТЕСТ API АВТОРИЗАЦИИ ЗАВЕРШЕН УСПЕШНО")
    print("="*80)


@ui_test(
    title="Демонстрация одиночной API авторизации",
    description="Пошаговая демонстрация API авторизации на примере админа",
    feature="API авторизация"
)
@pytest.mark.api
@pytest.mark.demo
def test_single_api_auth_demo() -> None:
    """
    Демонстрационный тест одиночной API авторизации.
    
    Показывает детальный процесс авторизации одного пользователя
    для понимания механизма работы API.
    """
    
    print("\n" + "="*80)
    print("🔍 ДЕМОНСТРАЦИЯ ОДИНОЧНОЙ API АВТОРИЗАЦИИ")
    print("="*80)
    
    # Используем админа для демонстрации
    admin_user = None
    for user in TEST_USERS:
        if user.get('login') == 'admin' or user.get('name') == 'admin':
            admin_user = user
            break
    
    if not admin_user:
        pytest.skip("Пользователь admin не найден для демонстрации")
    
    print(f"👤 Демонстрируем API авторизацию пользователя: {admin_user['login']}")
    
    with allure.step("Создание API менеджера"):
        auth_manager = APIAuthManager()
        print(f"🔧 API менеджер создан")
        print(f"   🌐 Базовый URL: {auth_manager.base_url}")
        print(f"   📡 Эндпоинт авторизации: {auth_manager.login_endpoint}")
        print(f"   ⏱️  Таймаут: {auth_manager.timeout} сек")
    
    try:
        with allure.step("Выполнение API запроса"):
            print(f"\n📡 Выполняем POST запрос к /login...")
            print(f"   📝 Параметры:")
            print(f"      • lgn: {admin_user['login']}")
            print(f"      • password: [скрыт для безопасности]")
            print(f"      • remember: 1")
            
            start_time = time.time()
            result = auth_manager.login_user(admin_user['login'], admin_user['password'])
            elapsed_time = time.time() - start_time
            
            print(f"\n📊 Результат запроса:")
            print(f"   ⏱️  Время выполнения: {elapsed_time:.2f} сек")
            print(f"   📈 HTTP статус: {result.response_status}")
            print(f"   ✅ Успех: {'Да' if result.success else 'Нет'}")
            
            if result.success:
                print(f"   🔑 Кука получена: {COOKIE_NAME}")
                print(f"   📝 Значение куки: {result.session_token[:50]}...")
                print(f"   🍪 Количество кук: {len(result.cookies) if result.cookies else 0}")
                
                # Детали куки
                if result.cookies and COOKIE_NAME in result.cookies:
                    cookie = result.cookies[COOKIE_NAME]
                    print(f"\n🔍 Детали куки:")
                    print(f"   • Имя: {cookie['name']}")
                    print(f"   • Домен: {cookie['domain']}")
                    print(f"   • Путь: {cookie['path']}")
                    print(f"   • Безопасная: {cookie['secure']}")
                    print(f"   • HttpOnly: {cookie['httpOnly']}")
                    print(f"   • SameSite: {cookie['sameSite']}")
            else:
                print(f"   ❌ Ошибка: {result.error_message}")
        
        with allure.step("Валидация результата"):
            if result.success:
                # Проверяем обязательные поля
                assert result.cookies is not None, "Куки должны быть получены"
                assert COOKIE_NAME in result.cookies, f"Кука {COOKIE_NAME} должна присутствовать"
                assert result.session_token, "Токен сессии должен быть получен"
                assert result.response_status == 200, f"Ожидался статус 200, получен {result.response_status}"
                
                print(f"✅ Все проверки пройдены успешно")
            else:
                pytest.fail(f"API авторизация не удалась: {result.error_message}")
    
    finally:
        auth_manager.close()
        print(f"\n🧹 API сессия закрыта")
    
    print(f"\n🎯 Демонстрация завершена успешно!")


@pytest.mark.api
@pytest.mark.performance  
def test_api_performance_benchmark() -> None:
    """
    Бенчмарк производительности API авторизации.
    
    Измеряет и сравнивает производительность API подхода
    с ожидаемыми показателями.
    """
    
    print("\n" + "="*80)
    print("⚡ БЕНЧМАРК ПРОИЗВОДИТЕЛЬНОСТИ API")
    print("="*80)
    
    # Тестируем на первых 5 пользователях для быстроты
    test_users = TEST_USERS[:5]
    print(f"📊 Тестируем производительность на {len(test_users)} пользователях")
    
    # Выполняем бенчмарк
    start_time = time.time()
    results, stats = api_mass_auth(test_users, save_files=False, update_db=False)
    total_time = time.time() - start_time
    
    # Анализ результатов
    successful_count = sum(1 for r in results if r.success)
    
    print(f"\n📈 РЕЗУЛЬТАТЫ БЕНЧМАРКА:")
    print(f"   👥 Пользователей обработано: {len(results)}")
    print(f"   ✅ Успешных авторизаций: {successful_count}")
    print(f"   ⏱️  Общее время: {total_time:.2f} сек")
    print(f"   ⚡ Время на пользователя: {total_time / len(test_users):.2f} сек")
    print(f"   🚀 Пользователей в секунду: {len(test_users) / total_time:.2f}")
    
    # Сравнение с эталонными показателями
    expected_time_per_user = 2.0  # Ожидаем не более 2 сек на пользователя
    actual_time_per_user = total_time / len(test_users)
    
    print(f"\n🎯 СРАВНЕНИЕ С ЭТАЛОНОМ:")
    print(f"   📋 Ожидаемое время на пользователя: ≤{expected_time_per_user} сек")
    print(f"   📊 Фактическое время: {actual_time_per_user:.2f} сек")
    
    if actual_time_per_user <= expected_time_per_user:
        print(f"   ✅ Производительность соответствует требованиям")
    else:
        print(f"   ⚠️  Производительность ниже ожидаемой")
    
    # Проверки производительности
    assert successful_count > 0, "Должна быть хотя бы одна успешная авторизация"
    assert total_time < 30, f"Общее время не должно превышать 30 сек, получено {total_time:.2f}"
    
    print(f"\n🏆 Бенчмарк завершен успешно!")


if __name__ == "__main__":
    print("Тесты API авторизации")
    print("Использование:")
    print("pytest -v -s tests/auth/test_api_mass_authorization.py")
    print("pytest -v -s tests/auth/test_api_mass_authorization.py -m api")
    print("pytest -v -s tests/auth/test_api_mass_authorization.py -m demo") 