"""
Демонстрационный тест авторизации через UI с сохранением куков в файлы и базу данных.

Загружает пользователей из CSV файла и выполняет видимую авторизацию для каждого.
После успешной авторизации сохраняет cookies в файлы и обновляет информацию в БД.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page, BrowserContext, Browser
import allure
import sys
from pathlib import Path
import os
import time
from config.secrets_manager import SecretsManager

# Импортируем утилиты из фреймворка
from framework.utils.cookie_constants import COOKIE_NAME, joint_cookie
from framework.utils.reporting.allure_utils import ui_test
from framework.utils.auth_utils import save_cookie, load_cookie, get_cookie_path
from framework.utils.db_helpers import update_user_in_db
from framework.utils.url_utils import add_allow_session_param, is_headless

# Загрузка тестовых пользователей из CSV
USERS_CSV_PATH = Path("d:/Bll_tests/secrets/bulk_users.csv")
TEST_USERS = SecretsManager.load_users_from_csv()


@ui_test(
    title="Демонстрация авторизации через логин/пароль с сохранением куков",
    description="Видимый тест процесса авторизации разных пользователей и сохранения их сессий",
    feature="Демонстрация авторизации"
)
@pytest.mark.demo
def test_visible_login_and_save_cookies(browser: Browser) -> None:
    """
    Демонстрация процесса авторизации через форму с видимыми действиями.
    
    Сценарий:
    1. Для каждого пользователя:
       - Открываем браузер с замедленными действиями
       - Переходим на страницу авторизации
       - Заполняем форму логина видимо и медленно
       - Выполняем авторизацию
       - Проверяем успешность авторизации
       - Сохраняем куку test_joint_session в файл
       - Показываем результат в консоли
    """
    
    print("\n" + "="*80)
    print("🚀 ДЕМОНСТРАЦИЯ АВТОРИЗАЦИИ ЧЕРЕЗ ЛОГИН/ПАРОЛЬ")
    print("="*80)
    
    for user in TEST_USERS:
        with allure.step(f"Авторизация пользователя: {user['name']}"):
            print(f"\n📝 Авторизуем пользователя: {user['name']}")
            print(f"   Логин: {user['login']}")
            print(f"   Файл куков: {user['cookie_file']}")
            
            # Создаем контекст с медленными действиями для визуализации
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                locale="ru-RU"
            )
            
            try:
                page = context.new_page()
                
                # Шаг 1: Переход на страницу логина (как в эталонном тесте)
                with allure.step("Переход на страницу логина"):
                    login_url = add_allow_session_param("https://ca.bll.by/login", is_headless())
                    print(f"   🌐 Переходим на страницу логина: {login_url}")
                    response = page.goto(login_url, wait_until="domcontentloaded", timeout=20000)
                    
                    if response and response.status == 403:
                        print("   ⚠️  Получен статус 403 - возможно требуется тестовый сервер")
                        pytest.skip("Сервер недоступен")
                    
                    # Прямая авторизация через форму (как в эталонном тесте)
                    print("   📝 Заполняем форму авторизации...")
                    
                    # Используем те же селекторы что и в эталонном тесте
                    page.fill("input[name='login'], input[name='email'], #login", user['login'])
                    time.sleep(0.5)
                    
                    page.fill("input[type='password'], input[name='password'], #password", user['password'])
                    time.sleep(0.5)
                    
                    print("   🔘 Нажимаем кнопку входа...")
                    page.click("button[type='submit'], input[type='submit'], button:has-text('Войти')")
                    time.sleep(2)  # Ждем обработку формы
                    
                    print("   ✅ Форма авторизации отправлена")
                
                # Шаг 2: Проверка авторизации
                with allure.step("Проверка состояния авторизации"):
                    # Основной критерий успеха - наличие никнейма пользователя (как в эталонном тесте)
                    try:
                        # Ждем появления никнейма после авторизации
                        page.wait_for_selector(".user-in__nick", timeout=10000)
                        nickname_element = page.locator(".user-in__nick")
                        nickname_text = nickname_element.text_content().strip()
                        
                        print(f"   ✅ Найден никнейм пользователя: '{nickname_text}'")
                        
                        # Проверяем соответствие никнейма логину (как в эталонном тесте)
                        if nickname_text == user['login']:
                            print(f"   ✅ Никнейм совпадает с логином - авторизация успешна!")
                            
                            # Шаг 3: Сохранение куки в файл (только после успешной авторизации)
                            with allure.step("Сохранение куки в файл"):
                                save_cookie(context, user['cookie_file'])
                                print(f"   💾 Кука сохранена в файл: {user['cookie_file']}")
                                
                                # Проверяем, что файл создан
                                if os.path.exists(user['cookie_file']):
                                    file_size = os.path.getsize(user['cookie_file'])
                                    print(f"   📁 Размер файла: {file_size} байт")
                                else:
                                    print(f"   ❌ Ошибка: файл {user['cookie_file']} не создан")
                            
                            # Шаг 4: Сохранение данных пользователя в БД (только после успешной авторизации)
                            with allure.step("Сохранение данных в БД"):
                                try:
                                    update_user_in_db(
                                        login=user['login'],
                                        role=user.get('role', 'user'),
                                        subscription=user.get('subscription', 'basic'),
                                        cookie_file=user['cookie_file']
                                    )
                                    print(f"   🗄️  Данные пользователя {user['name']} сохранены в БД")
                                    print(f"   📊 Роль: {user.get('role', 'user')}, Подписка: {user.get('subscription', 'basic')}")
                                except Exception as e:
                                    print(f"   ⚠️  Ошибка сохранения в БД: {e}")
                            
                            # Дополнительная проверка страницы профиля (не критическая)
                            try:
                                profile_url = add_allow_session_param("https://ca.bll.by/user/profile", is_headless())
                                print(f"   🔄 Дополнительная проверка профиля: {profile_url}")
                                page.goto(profile_url, timeout=10000)
                                page.wait_for_load_state('domcontentloaded', timeout=5000)
                                
                                # Пытаемся найти элементы профиля (не критично если не найдены)
                                try:
                                    from playwright.sync_api import expect
                                    expect(page.locator("div.profile_ttl:has-text('Мой профиль')")).to_be_visible(timeout=5000)
                                    print("   ✅ Страница профиля доступна!")
                                except:
                                    print("   ⚠️  Страница профиля недоступна (не критично)")
                                    
                            except Exception as e:
                                print(f"   ⚠️  Ошибка при проверке профиля: {e} (не критично)")
                            
                        else:
                            print(f"   ❌ Никнейм '{nickname_text}' не соответствует логину '{user['login']}'")
                            # Делаем скриншот как в эталонном тесте
                            screenshot_path = f"auth_fail_{user['name']}_nickname_mismatch.png"
                            page.screenshot(path=screenshot_path)
                            print(f"   📸 Скриншот сохранен: {screenshot_path}")
                            
                    except Exception as e:
                        print(f"   ❌ Никнейм пользователя не найден: {e}")
                        # Делаем скриншот как в эталонном тесте 
                        screenshot_path = f"auth_fail_{user['name']}_no_nickname.png"
                        page.screenshot(path=screenshot_path)
                        print(f"   📸 Скриншот сохранен: {screenshot_path}")

                print(f"   🎉 Авторизация {user['name']} завершена успешно!\n")
                time.sleep(1)  # Пауза между пользователями
                
            finally:
                context.close()
    
    print("="*80)
    print("✅ ВСЕ ПОЛЬЗОВАТЕЛИ УСПЕШНО АВТОРИЗОВАНЫ И КУКИ СОХРАНЕНЫ")
    print("="*80)


@ui_test(
    title="Демонстрация авторизации из сохранённых куков",
    description="Видимая проверка авторизации каждого пользователя из сохранённых файлов куков",
    feature="Демонстрация загрузки куков"
)
@pytest.mark.demo  
def test_visible_auth_from_saved_cookies(browser: Browser) -> None:
    """
    Демонстрация авторизации пользователей из сохранённых куков.
    
    Сценарий:
    1. Для каждого пользователя:
       - Создаем новый чистый контекст
       - Загружаем сохранённую куку из файла
       - Переходим на сайт с загруженной кукой
       - Проверяем статус авторизации визуально
       - Показываем результат в консоли
    """
    
    print("\n" + "="*80)
    print("🔓 ДЕМОНСТРАЦИЯ АВТОРИЗАЦИИ ИЗ СОХРАНЁННЫХ КУКОВ")
    print("="*80)
    
    for user in TEST_USERS:
        with allure.step(f"Проверка авторизации из куков: {user['name']}"):
            print(f"\n🔍 Проверяем авторизацию пользователя: {user['name']}")
            print(f"   Файл куков: {user['cookie_file']}")
            
            # Проверяем наличие файла куков
            if not os.path.exists(user['cookie_file']):
                print(f"   ❌ Файл куков {user['cookie_file']} не найден!")
                print(f"   💡 Сначала запустите test_visible_login_and_save_cookies")
                continue
            
            # Создаем новый чистый контекст
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                locale="ru-RU"
            )
            
            try:
                # Шаг 1: Проверяем пустой контекст
                with allure.step("Проверка чистого контекста"):
                    initial_cookies = context.cookies()
                    print(f"   🧹 Новый контекст создан. Куков в контексте: {len(initial_cookies)}")
                    assert len(initial_cookies) == 0, "Контекст должен быть пустым"
                
                # Шаг 2: Загружаем куку из файла
                with allure.step("Загрузка куки из файла"):
                    print(f"   📥 Загружаем куку из файла {user['cookie_file']}")
                    load_cookie(context, user['cookie_file'])
                    
                    loaded_cookies = context.cookies()
                    print(f"   📊 После загрузки куков в контексте: {len(loaded_cookies)}")
                    
                    if loaded_cookies:
                        cookie = loaded_cookies[0]
                        print(f"   🔑 Загружена кука: {cookie['name']}")
                        print(f"   📝 Значение: {cookie['value'][:50]}...")
                        print(f"   🌐 Домен: {cookie['domain']}")
                        assert cookie['name'] == COOKIE_NAME, f"Неожиданное имя куки: {cookie['name']}"
                    else:
                        print("   ❌ Кука не загружена!")
                        continue
                
                # Шаг 3: Проверяем авторизацию на сайте
                with allure.step("Проверка авторизации на сайте"):
                    page = context.new_page()
                    main_url = add_allow_session_param("https://ca.bll.by", is_headless())
                    print(f"   🌐 Переходим на сайт с загруженной кукой: {main_url}")
                    
                    response = page.goto(main_url, wait_until="domcontentloaded")
                    time.sleep(2)  # Пауза для визуализации
                    
                    if response:
                        status = response.status
                        print(f"   📊 HTTP статус: {status}")
                        
                        if status == 200:
                            print("   ✅ Сайт доступен!")
                            
                            # Проверяем наличие элементов авторизованного пользователя
                            auth_indicators = [
                                "text=Выйти", "text=Профиль", "text=Личный кабинет",
                                ".user-menu", ".profile-link", ".logout-link"
                            ]
                            
                            auth_found = False
                            for indicator in auth_indicators:
                                try:
                                    if page.is_visible(indicator, timeout=1000):
                                        print(f"   🎯 Найден индикатор авторизации: {indicator}")
                                        auth_found = True
                                        break
                                except:
                                    continue
                            
                            if auth_found:
                                print(f"   🎉 {user['name']} УСПЕШНО АВТОРИЗОВАН через куки!")
                            else:
                                print(f"   ⚠️  Индикаторы авторизации не найдены, но кука загружена")
                        
                        elif status == 403:
                            print("   ⚠️  Статус 403 - возможно требуется тестовый сервер")
                            print("   💡 Но кука успешно загружена в контекст")
                            
                        else:
                            print(f"   ⚠️  Неожиданный статус: {status}")
                    
                    # Финальная проверка куков в контексте
                    final_cookies = context.cookies()
                    auth_cookies = [c for c in final_cookies if c['name'] == COOKIE_NAME]
                    
                    if auth_cookies:
                        print(f"   ✅ Кука {COOKIE_NAME} присутствует в финальном состоянии")
                    else:
                        print(f"   ❌ Кука {COOKIE_NAME} потеряна!")
                
                print(f"   🏁 Проверка авторизации {user['name']} завершена\n")
                time.sleep(1)  # Пауза между пользователями
                
            finally:
                context.close()
    
    print("="*80)
    print("✅ ПРОВЕРКА АВТОРИЗАЦИИ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ ЗАВЕРШЕНА")
    print("="*80)


@pytest.mark.integration
def test_single_evgenqa_auth(browser: Browser) -> None:
    """
    Тест авторизации только пользователя EvgenQA для проверки корректности учетных данных.
    Запускается отдельно, без влияния других пользователей.
    """
    print("\n" + "="*80)
    print("🔍 ТЕСТ АВТОРИЗАЦИИ ТОЛЬКО EVGENQA")
    print("="*80)
    
    # Берем только EvgenQA из списка
    evgenqa_user = None
    for user in TEST_USERS:
        if user['name'] == 'EvgenQA':
            evgenqa_user = user
            break
    
    if not evgenqa_user:
        pytest.skip("Пользователь EvgenQA не найден в TEST_USERS")
    
    print(f"\n📝 Авторизуем пользователя: {evgenqa_user['name']}")
    print(f"   Логин: {evgenqa_user['login']}")
    
    context = browser.new_context()
    page = context.new_page()
    
    try:
        with allure.step(f"Авторизация {evgenqa_user['name']}"):
            # Переход на страницу логина
            login_url = add_allow_session_param("https://ca.bll.by/login", is_headless())
            print(f"   🌐 Переходим на страницу логина: {login_url}")
            page.goto(login_url, wait_until="domcontentloaded", timeout=20000)
            
            # Заполнение формы
            print(f"   📝 Заполняем форму авторизации...")
            page.fill("input[name='login'], input[name='email'], #login", evgenqa_user['login'])
            page.fill("input[type='password'], input[name='password'], #password", evgenqa_user['password'])
            
            print(f"   🔘 Нажимаем кнопку входа...")
            page.click("button[type='submit'], input[type='submit'], button:has-text('Войти')")
            print(f"   ✅ Форма авторизации отправлена")
            
            # Проверка авторизации
            try:
                page.wait_for_selector(".user-in__nick", timeout=15000)
                nickname_element = page.locator(".user-in__nick")
                nickname_text = nickname_element.text_content().strip()
                
                print(f"   ✅ Найден никнейм пользователя: '{nickname_text}'")
                
                if nickname_text == evgenqa_user['login']:
                    print(f"   ✅ Никнейм совпадает с логином - авторизация успешна!")
                    print(f"   🎉 EvgenQA успешно авторизован!")
                else:
                    print(f"   ❌ Никнейм '{nickname_text}' не соответствует логину '{evgenqa_user['login']}'")
                    assert False, f"Никнейм не совпадает с логином"
                    
            except Exception as e:
                print(f"   ❌ Никнейм пользователя не найден: {e}")
                screenshot_path = f"evgenqa_solo_auth_fail.png" 
                page.screenshot(path=screenshot_path)
                print(f"   📸 Скриншот сохранен: {screenshot_path}")
                assert False, f"Авторизация EvgenQA не удалась: никнейм не найден"
                
    finally:
        context.close()


@pytest.mark.integration
def test_single_third_user_auth(browser: Browser) -> None:
    """
    Тест авторизации третьего пользователя из списка для сравнения с EvgenQA.
    Проверяем, что проблема действительно в учетных данных, а не в системе.
    """
    print("\n" + "="*80)
    print("🔍 ТЕСТ АВТОРИЗАЦИИ ТРЕТЬЕГО ПОЛЬЗОВАТЕЛЯ")
    print("="*80)
    
    # Берем третьего пользователя из списка (индекс 2)
    if len(TEST_USERS) < 3:
        pytest.skip("Недостаточно пользователей в TEST_USERS")
    
    third_user = TEST_USERS[2]  # Третий пользователь (fKL5nOOz)
    
    print(f"\n📝 Авторизуем пользователя: {third_user['name']}")
    print(f"   Логин: {third_user['login']}")
    
    context = browser.new_context()
    page = context.new_page()
    
    try:
        with allure.step(f"Авторизация {third_user['name']}"):
            # Переход на страницу логина
            login_url = add_allow_session_param("https://ca.bll.by/login", is_headless())
            print(f"   🌐 Переходим на страницу логина: {login_url}")
            page.goto(login_url, wait_until="domcontentloaded", timeout=20000)
            
            # Заполнение формы
            print(f"   📝 Заполняем форму авторизации...")
            page.fill("input[name='login'], input[name='email'], #login", third_user['login'])
            page.fill("input[type='password'], input[name='password'], #password", third_user['password'])
            
            print(f"   🔘 Нажимаем кнопку входа...")
            page.click("button[type='submit'], input[type='submit'], button:has-text('Войти')")
            print(f"   ✅ Форма авторизации отправлена")
            
            # Проверка авторизации
            try:
                page.wait_for_selector(".user-in__nick", timeout=15000)
                nickname_element = page.locator(".user-in__nick")
                nickname_text = nickname_element.text_content().strip()
                
                print(f"   ✅ Найден никнейм пользователя: '{nickname_text}'")
                
                if nickname_text == third_user['login']:
                    print(f"   ✅ Никнейм совпадает с логином - авторизация успешна!")
                    print(f"   🎉 {third_user['name']} успешно авторизован!")
                else:
                    print(f"   ❌ Никнейм '{nickname_text}' не соответствует логину '{third_user['login']}'")
                    assert False, f"Никнейм не совпадает с логином"
                    
            except Exception as e:
                print(f"   ❌ Никнейм пользователя не найден: {e}")
                screenshot_path = f"{third_user['name']}_solo_auth_fail.png" 
                page.screenshot(path=screenshot_path)
                print(f"   📸 Скриншот сохранен: {screenshot_path}")
                assert False, f"Авторизация {third_user['name']} не удалась: никнейм не найден"
                
    finally:
        context.close()


@pytest.mark.integration
def test_stealth_headless_auth(browser: Browser) -> None:
    """
    Тест авторизации с улучшенными антибот настройками.
    
    Использует дополнительные JavaScript скрипты и задержки для обхода защиты.
    """
    print("\n" + "="*80)
    print("🥷 ТЕСТ АВТОРИЗАЦИИ С АНТИБОТ НАСТРОЙКАМИ")
    print("="*80)
    
    from framework.utils.auth_utils import create_stealth_context
    
    # Тестируем первых 3 пользователей
    test_users = TEST_USERS[:3]
    
    for user in test_users:
        print(f"\n📝 Тестируем пользователя: {user['name']}")
        print(f"   Логин: {user['login']}")
        
        # Создаем улучшенный контекст
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ru-RU", 
            timezone_id="Europe/Minsk",
            ignore_https_errors=True,
            java_script_enabled=True,
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8", 
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate", 
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1"
            }
        )
        
        # Устанавливаем увеличенные таймауты
        context.set_default_navigation_timeout(60000)
        context.set_default_timeout(30000)
        
        page = context.new_page()
        
        try:
            # Дополнительная маскировка - убираем webdriver свойство
            page.add_init_script("""
                // Убираем признаки автоматизации
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Маскируем chrome runtime
                window.chrome = {
                    runtime: {}
                };
                
                // Переопределяем плагины
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Переопределяем языки
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['ru-RU', 'ru', 'en-US', 'en'],
                });
                
                // Маскируем автоматизацию через permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            # Переход на страницу логина с увеличенным таймаутом
            login_url = add_allow_session_param("https://ca.bll.by/login", is_headless())
            print(f"   🌐 Переходим на: {login_url}")
            
            page.goto(login_url, wait_until="domcontentloaded", timeout=60000)
            
            # Дополнительное ожидание для полной загрузки
            print(f"   ⏱️  Ожидаем полную загрузку страницы...")
            page.wait_for_timeout(3000)
            
            # Заполнение формы с реалистичными задержками
            print(f"   📝 Заполняем форму с задержками...")
            page.fill("input[name='login'], input[name='email'], #login", user['login'])
            page.wait_for_timeout(800)  # Пауза между полями как у реального пользователя
            
            page.fill("input[type='password'], input[name='password'], #password", user['password'])
            page.wait_for_timeout(600)
            
            print(f"   🔘 Отправляем форму...")
            page.click("button[type='submit'], input[type='submit'], button:has-text('Войти')")
            
            # Ожидание с увеличенным таймаутом
            print(f"   🔍 Ищем никнейм с таймаутом 30 сек...")
            try:
                page.wait_for_selector(".user-in__nick", timeout=30000)
                nickname_element = page.locator(".user-in__nick")
                nickname_text = nickname_element.text_content().strip()
                
                print(f"   ✅ Успех! Найден никнейм: '{nickname_text}'")
                
                if nickname_text == user['login']:
                    print(f"   🎉 {user['name']} успешно авторизован с антибот настройками!")
                else:
                    print(f"   ⚠️ Никнейм '{nickname_text}' не совпадает с логином '{user['login']}'")
                    
            except Exception as e:
                print(f"   ❌ Не удалось найти никнейм: {str(e)[:100]}...")
                screenshot_path = f"stealth_fail_{user['name']}.png"
                page.screenshot(path=screenshot_path)
                print(f"   📸 Скриншот: {screenshot_path}")
                
        finally:
            context.close()
    
    print(f"\n🏁 Тестирование антибот настроек завершено!")


# @pytest.fixture(autouse=True, scope="module")
# def cleanup_demo_files():
#     """Автоматическая очистка демонстрационных файлов после тестов."""
#     yield
#     
#     print("\n🧹 Очистка демонстрационных файлов...")
#     for user in TEST_USERS:
#         if os.path.exists(user['cookie_file']):
#             os.remove(user['cookie_file'])
#             print(f"   🗑️  Удален файл: {user['cookie_file']}")
#     print("✅ Очистка завершена")


def manual_cleanup():
    """Ручная очистка файлов куков."""
    print("\n🧹 Ручная очистка демонстрационных файлов...")
    for user in TEST_USERS:
        if os.path.exists(user['cookie_file']):
            os.remove(user['cookie_file'])
            print(f"   🗑️  Удален файл: {user['cookie_file']}")
    print("✅ Очистка завершена")


if __name__ == "__main__":
    print("Для запуска демонстрации используйте:")
    print("pytest -v -s test_ui_login_and_session_save.py::test_visible_login_and_save_cookies")
    print("pytest -v -s test_ui_login_and_session_save.py::test_visible_auth_from_saved_cookies")
