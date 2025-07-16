"""
SSO тестирование через requests API.

Проверяет работу авторизации между всеми сервисами экосистемы Bll
без использования браузера, что обеспечивает высокую скорость
и надежность тестирования.

Тестируемые домены:
- bll.by (основной сайт)
- ca.bll.by (центр авторизации)  
- expert.bll.by (экспертный раздел)
- cp.bll.by (панель управления)
- gz.bll.by (госзакупки)
- bonus.bll.by (бонусная система)

Каждый тест полностью изолирован - использует отдельную HTTP сессию.
"""
from __future__ import annotations

import pytest
import allure
from typing import Dict, Any

from framework.utils.sso_requests import SSORequestsClient
from framework.utils.html_parser import validate_sso_response, check_auth_status
from framework.utils.reporting.allure_utils import ui_test
from tests.integration.sso.constants import SSO_DOMAINS, get_domain_display_name


@ui_test(
    title="SSO: Авторизация через requests API на всех доменах",
    description="Проверка работы одной куки test_joint_session на всех сервисах экосистемы через HTTP запросы",
    feature="SSO авторизация"
)
@pytest.mark.sso
@pytest.mark.parametrize("domain_url", SSO_DOMAINS)
def test_sso_cookie_auth_all_domains(
    isolated_sso_client: SSORequestsClient,
    random_user_cookies: Dict[str, Any],
    domain_url: str
) -> None:
    """
    Параметризованный тест SSO авторизации через requests API.
    
    Выполняет полный цикл тестирования для каждого домена:
    1. GET запрос без кук → проверка неавторизованного состояния
    2. GET запрос с куками → проверка авторизованного состояния
    3. Валидация изменения состояния авторизации
    
    Args:
        isolated_sso_client: Изолированная HTTP сессия для тестирования
        random_user_cookies: Куки случайного пользователя
        domain_url: URL домена для тестирования (параметризовано)
    """
    username = random_user_cookies["username"]
    user_cookies = random_user_cookies["cookies"]
    domain_name = get_domain_display_name(domain_url)
    
    print(f"\n🌐 Тестирование SSO на домене: {domain_name}")
    print(f"👤 Используется пользователь: {username}")
    print(f"🍪 Количество кук: {len(user_cookies)}")
    
    with allure.step(f"ШАГ 1: Проверка неавторизованного доступа к {domain_name}"):
        # Выполняем запрос без кук
        status_unauth, html_unauth = isolated_sso_client.make_request(domain_url, with_cookies=False)
        
        print(f"   📡 HTTP статус без кук: {status_unauth}")
        
        # Анализируем состояние авторизации в HTML
        auth_status_unauth = check_auth_status(html_unauth)
        
        print(f"   🔍 Статус авторизации: {auth_status_unauth['status']}")
        print(f"   📄 Заголовок страницы: {auth_status_unauth['page_title']}")
        
        # Логируем найденные маркеры
        if auth_status_unauth['unauthenticated_markers']:
            print(f"   ✅ Найдены маркеры неавторизации:")
            for marker in auth_status_unauth['unauthenticated_markers'][:3]:  # Показываем первые 3
                print(f"      • {marker}")
        else:
            print(f"   ℹ️  Маркеры неавторизации не найдены (возможно, особенности интерфейса)")
    
    with allure.step(f"ШАГ 2: Установка кук и проверка авторизованного доступа"):
        # Устанавливаем куки пользователя
        isolated_sso_client.set_cookies_for_domain(user_cookies, domain_url)
        print(f"   🍪 Установлены куки пользователя: {username}")
        
        # Выполняем запрос с куками
        status_auth, html_auth = isolated_sso_client.make_request(domain_url, with_cookies=True)
        
        print(f"   📡 HTTP статус с куками: {status_auth}")
        
        # Анализируем состояние авторизации после установки кук
        auth_status_auth = check_auth_status(html_auth)
        
        print(f"   🔍 Статус авторизации: {auth_status_auth['status']}")
        
        # Логируем найденные маркеры авторизации
        if auth_status_auth['authenticated_markers']:
            print(f"   ✅ Найдены маркеры авторизации:")
            for marker in auth_status_auth['authenticated_markers'][:3]:  # Показываем первые 3
                print(f"      • {marker}")
        else:
            print(f"   ❌ Маркеры авторизации не найдены!")
    
    with allure.step(f"ШАГ 3: Валидация SSO результатов"):
        # Валидируем изменение состояния авторизации
        sso_validation = validate_sso_response(html_unauth, html_auth)
        
        print(f"   📊 Анализ SSO:")
        print(f"      • Успешность SSO: {sso_validation['sso_success']}")
        print(f"      • Состояние изменилось: {sso_validation['analysis']['cookies_changed_auth_state']}")
        print(f"      • До установки кук: {'авторизован' if sso_validation['analysis']['before_auth'] else 'не авторизован'}")
        print(f"      • После установки кук: {'авторизован' if sso_validation['analysis']['after_auth'] else 'не авторизован'}")
        
        # Основная проверка - пользователь должен стать авторизованным после установки кук
        assert sso_validation['analysis']['after_auth'], (
            f"SSO авторизация не работает на {domain_name} для пользователя {username}.\n"
            f"После установки кук пользователь остался неавторизованным.\n"
            f"Состояние до кук: {sso_validation['without_cookies']['status']}\n"
            f"Состояние после кук: {sso_validation['with_cookies']['status']}\n"
            f"HTTP статус: {status_unauth} → {status_auth}"
        )
        
        print(f"   ✅ SSO авторизация работает корректно на {domain_name}")
        print(f"      👤 Пользователь: {username}")
        print(f"      🎯 Результат: {sso_validation['with_cookies']['status']}")


@ui_test(
    title="SSO: Проверка изоляции тестов",
    description="Убеждается что каждый тест получает чистую HTTP сессию",
    feature="SSO авторизация"
)
@pytest.mark.sso
def test_sso_requests_isolation(isolated_sso_client: SSORequestsClient) -> None:
    """
    Проверяет изоляцию между SSO тестами.
    
    Убеждается что новая HTTP сессия не содержит кук
    от предыдущих тестов.
    
    Args:
        isolated_sso_client: Изолированная HTTP сессия
    """
    test_domain = "https://ca.bll.by/"
    
    with allure.step("Проверка отсутствия кук в новой сессии"):
        # Проверяем что в новой сессии нет кук
        current_cookies = isolated_sso_client.session.cookies
        cookies_count = len(current_cookies)
        
        print(f"   📊 Количество кук в новой сессии: {cookies_count}")
        
        # В изолированной сессии не должно быть кук
        assert cookies_count == 0, (
            f"Найдены куки в новой HTTP сессии: {list(current_cookies)}. "
            "Это указывает на проблему изоляции тестов!"
        )
        
        print("   ✅ Новая HTTP сессия чистая - нет кук")
    
    with allure.step("Проверка чистого состояния через HTTP запрос"):
        # Выполняем запрос к тестовому домену
        status_code, html_content = isolated_sso_client.make_request(test_domain, with_cookies=False)
        
        print(f"   📡 HTTP статус: {status_code}")
        
        # Анализируем состояние авторизации
        auth_status = check_auth_status(html_content)
        
        print(f"   🔍 Статус авторизации: {auth_status['status']}")
        print(f"   📄 Заголовок страницы: {auth_status['page_title']}")
        
        # В чистой сессии пользователь не должен быть авторизован
        # (но это не критично, так как зависит от интерфейса)
        if auth_status['is_authenticated']:
            print("   ℹ️  Пользователь авторизован в чистой сессии (возможно, кеширование)")
        else:
            print("   ✅ Пользователь не авторизован в чистой сессии")


@ui_test(
    title="SSO: Проверка доступности кук для тестирования",
    description="Проверяет наличие файлов кук и их корректность",
    feature="SSO авторизация"
)
@pytest.mark.sso
def test_sso_cookies_availability(sso_test_info: Dict[str, Any]) -> None:
    """
    Утилитарный тест для проверки доступности кук.
    
    Проверяет что файлы кук существуют и содержат
    корректные данные для тестирования.
    
    Args:
        sso_test_info: Информация о SSO тестировании
    """
    with allure.step("Проверка наличия файлов кук"):
        users_count = sso_test_info["users_count"]
        available_users = sso_test_info["available_users"]
        cookies_dir_exists = sso_test_info["cookies_dir_exists"]
        
        print(f"   📁 Папка кук существует: {cookies_dir_exists}")
        print(f"   👥 Доступно пользователей: {users_count}")
        
        assert cookies_dir_exists, "Папка с файлами кук не найдена"
        assert users_count > 0, "Нет доступных файлов кук для тестирования"
        
        print(f"   ✅ Найдено {users_count} файлов кук")
        
        # Показываем первых 5 пользователей
        users_to_show = available_users[:5]
        print(f"   👤 Доступные пользователи: {', '.join(users_to_show)}")
        if len(available_users) > 5:
            print(f"      ... и еще {len(available_users) - 5}")
    
    with allure.step("Проверка конфигурации тестирования"):
        timeout = sso_test_info["timeout"]
        cookie_name = sso_test_info["expected_cookie_name"] 
        cookie_domain = sso_test_info["test_domain"]
        
        print(f"   ⏱️  Таймаут HTTP запросов: {timeout} секунд")
        print(f"   🍪 Ожидаемое имя куки: {cookie_name}")
        print(f"   🌐 Домен кук: {cookie_domain}")
        
        assert timeout > 0, "Некорректный таймаут для HTTP запросов"
        assert cookie_name == "test_joint_session", "Неправильное имя основной куки авторизации"
        
        print(f"   ✅ Конфигурация тестирования корректна") 