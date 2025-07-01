"""
Демонстрационный тест для новой архитектуры фреймворка.

Этот тест показывает как использовать новые возможности фреймворка:
- Централизованные Page Objects из framework.app.pages
- Умные fixtures для авторизации из framework.fixtures
- Автоматическое управление cookies из cookies/
- Получение тестовых данных из secrets/

Сравнение для Junior QA:
БЫЛО (старый подход):
- Нужно было писать код авторизации в каждом тесте
- Дублирование логики работы с cookies
- Сложность управления различными пользователями
- Разбросанность конфигураций по разным файлам

СТАЛО (новая архитектура):
- Готовые fixtures для любого типа пользователя
- Автоматическое сохранение/загрузка cookies
- Централизованное управление всеми компонентами
- Простота использования в тестах
"""

import pytest
from playwright.sync_api import Page, BrowserContext

# Импортируем Page Objects из framework
from framework.app.pages.login_page import LoginPage
from framework.utils.auth_utils import list_available_cookies, check_cookie_validity


class TestUpdatedAuthDemo:
    """
    Демонстрационный тестовый класс для новой архитектуры.
    
    Показывает различные способы работы с авторизацией и Page Objects.
    """

    def test_login_page_elements_visibility(self, clean_context: BrowserContext):
        """
        Тест проверки видимости элементов на странице логина.
        
        Использует clean_context fixture для гарантии отсутствия авторизации.
        Демонстрирует использование Page Object из framework.
        
        Args:
            clean_context: Контекст без авторизации из framework.fixtures
        """
        page = clean_context.new_page()
        login_page = LoginPage(page)
        
        # Переходим на страницу логина
        page.goto("https://bll.by/login")
        
        # Проверяем, что форма логина видна
        assert login_page.is_login_form_visible(), "Форма логина должна быть видна"
        
        # Проверяем, что нет ошибок валидации изначально
        validation_error = login_page.get_validation_error()
        assert validation_error is None, "Не должно быть ошибок валидации при загрузке страницы"

    def test_admin_dashboard_access(self, authenticated_admin: BrowserContext):
        """
        Тест доступа к админ-панели для авторизованного администратора.
        
        Использует authenticated_admin fixture, которая автоматически:
        1. Пытается загрузить cookies администратора из cookies/
        2. Если cookies нет или недействительны - выполняет авторизацию
        3. Сохраняет новые cookies для будущих тестов
        
        Args:
            authenticated_admin: Контекст с авторизованным администратором
        """
        page = authenticated_admin.new_page()
        
        # Проверяем, что авторизация прошла успешно
        assert check_cookie_validity(authenticated_admin, "admin"), \
            "Администратор должен быть авторизован"
        
        # Переходим в админ-панель
        page.goto("https://bll.by/admin")
        
        # Здесь могут быть проверки элементов админ-панели
        # Например: page.wait_for_selector(".admin-dashboard")
        
        print("✅ Админ-панель доступна авторизованному администратору")

    def test_user_profile_access(self, authenticated_user: BrowserContext):
        """
        Тест доступа к профилю для обычного пользователя.
        
        Аналогично authenticated_admin, но для обычного пользователя.
        
        Args:
            authenticated_user: Контекст с авторизованным пользователем
        """
        page = authenticated_user.new_page()
        
        # Проверяем авторизацию
        assert check_cookie_validity(authenticated_user, "user"), \
            "Пользователь должен быть авторизован"
        
        # Переходим в профиль
        page.goto("https://bll.by/profile") 
        
        print("✅ Профиль доступен авторизованному пользователю")

    def test_quick_auth_flexibility(self, quick_auth):
        """
        Тест демонстрирует гибкость quick_auth fixture.
        
        Позволяет быстро авторизоваться под любым пользователем,
        для которого есть сохраненные cookies.
        
        Args:
            quick_auth: Фикстура для быстрой авторизации любым пользователем
        """
        # Получаем список доступных пользователей
        available_users = list_available_cookies()
        print(f"Доступные пользователи с cookies: {available_users}")
        
        if "admin" in available_users:
            # Быстро авторизуемся под администратором
            admin_context = quick_auth("admin")
            admin_page = admin_context.new_page()
            
            admin_page.goto("https://bll.by/")
            print("✅ Быстрая авторизация под администратором успешна")
            
            admin_context.close()
        
        if "moderator" in available_users:
            # Быстро авторизуемся под модератором
            moderator_context = quick_auth("moderator")
            moderator_page = moderator_context.new_page()
            
            moderator_page.goto("https://bll.by/")
            print("✅ Быстрая авторизация под модератором успешна")
            
            moderator_context.close()

    def test_login_with_invalid_credentials(self, clean_context: BrowserContext):
        """
        Тест входа с неверными учетными данными.
        
        Демонстрирует использование методов LoginPage для проверки ошибок.
        
        Args:
            clean_context: Чистый контекст без авторизации
        """
        page = clean_context.new_page()
        login_page = LoginPage(page)
        
        page.goto("https://bll.by/login")
        
        # Пытаемся войти с неверными данными
        login_page.login("invalid_user", "wrong_password")
        
        # Ждем появления ошибки
        page.wait_for_timeout(2000)
        
        # Проверяем наличие ошибки валидации
        validation_error = login_page.get_validation_error()
        assert validation_error is not None, "Должна появиться ошибка при неверных данных"
        
        print(f"✅ Получена ожидаемая ошибка: {validation_error}")

    @pytest.mark.smoke
    def test_main_page_access_without_auth(self, clean_context: BrowserContext):
        """
        Smoke тест доступа к главной странице без авторизации.
        
        Проверяет, что основная функциональность доступна неавторизованным пользователям.
        
        Args:
            clean_context: Контекст без авторизации
        """
        page = clean_context.new_page()
        
        # Переходим на главную страницу
        page.goto("https://bll.by/")
        
        # Проверяем, что страница загрузилась
        page.wait_for_load_state("networkidle")
        
        # Проверяем наличие ссылки на вход
        login_link = page.locator("a:has-text('Войти'), a.top-nav__ent")
        assert login_link.is_visible(), "Ссылка 'Войти' должна быть видна для неавторизованных пользователей"
        
        print("✅ Главная страница доступна без авторизации")

    def test_multiple_users_workflow(self, browser):
        """
        Тест демонстрирует работу с несколькими пользователями в рамках одного теста.
        
        Показывает, как легко переключаться между пользователями используя новую архитектуру.
        
        Args:
            browser: Базовый браузер Playwright
        """
        # Создаем контекст для администратора
        admin_context = browser.new_context()
        from framework.utils.auth_utils import load_user_cookie
        
        admin_page = admin_context.new_page()
        
        if load_user_cookie(admin_context, "admin"):
            admin_page.goto("https://bll.by/admin")
            print("✅ Администратор вошел в админ-панель")
        
        # Создаем отдельный контекст для обычного пользователя
        user_context = browser.new_context()
        user_page = user_context.new_page()
        
        if load_user_cookie(user_context, "user"):
            user_page.goto("https://bll.by/profile")
            print("✅ Пользователь вошел в профиль")
        
        # Закрываем контексты
        admin_context.close()
        user_context.close()
        
        print("✅ Успешно протестирована работа с несколькими пользователями")


@pytest.mark.integration
class TestAuthIntegration:
    """
    Интеграционные тесты для проверки работы авторизации с новой архитектурой.
    """

    def test_cookie_persistence_across_sessions(self, authenticated_admin: BrowserContext):
        """
        Тест проверяет, что cookies сохраняются между сессиями.
        
        Args:
            authenticated_admin: Авторизованный контекст администратора
        """
        page = authenticated_admin.new_page()
        
        # Проверяем, что мы авторизованы
        assert check_cookie_validity(authenticated_admin, "admin")
        
        # Переходим на разные страницы, проверяя сохранение авторизации
        test_urls = [
            "https://bll.by/",
            "https://bll.by/profile", 
            "https://bll.by/admin"
        ]
        
        for url in test_urls:
            page.goto(url)
            page.wait_for_load_state("networkidle")
            
            # Проверяем, что авторизация сохранилась
            assert check_cookie_validity(authenticated_admin, "admin"), \
                f"Авторизация должна сохраняться на странице {url}"
        
        print("✅ Cookies корректно сохраняются между переходами по страницам")
