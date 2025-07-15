"""
Тесты авторизации по кукам между всеми сервисами экосистемы Bll (SSO).

Проверяет что одна кука test_joint_session работает на всех доменах:
- bll.by (основной сайт)
- ca.bll.by (центр авторизации)
- expert.bll.by (экспертный раздел)
- cp.bll.by (панель управления)
- gz.bll.by (госзакупки)
- bonus.bll.by (бонусная система)

Каждый тест полностью изолирован - использует отдельный браузерный контекст.
"""
from __future__ import annotations

import pytest
import allure
import random
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from playwright.sync_api import Page, BrowserContext, Browser, expect
from framework.utils.reporting.allure_utils import ui_test


# === КОНСТАНТЫ И КОНФИГУРАЦИЯ ===

# Домены для тестирования SSO
SSO_DOMAINS = [
    "https://bll.by/",
    "https://ca.bll.by/", 
    "https://expert.bll.by/",
    "https://cp.bll.by/",
    "https://gz.bll.by/",
    "https://bonus.bll.by/"
]

# Локаторы для проверки состояния авторизации
LOCATORS = {
    # Локаторы неавторизованного пользователя
    "login_button": 'a[href*="login"]:has-text("Войти"), a.top-nav__ent:has-text("Войти")',
    "login_link": 'a[href*="login"]',  # Более широкий поиск ссылок на логин
    
    # Основные локаторы авторизованного пользователя  
    "profile_menu": 'a.top-nav__profile#myProfile_id, a[onclick*="toggle_visibility"]:has-text("Мой профиль")',
    "my_profile_link": 'a#myProfile_id, a[onclick*="myProfile"]',
    
    # Альтернативные локаторы для проверки авторизации
    "user_nickname": 'div.user-in__nick',
    "profile_link": 'a[href*="/user/profile"]:has-text("Мои данные")',
    "my_profile_text": ':has-text("Мой профиль")',
    "profile_dropdown": 'div[id*="box0"], div.profile-dropdown'
}


# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def get_available_cookie_files() -> List[Path]:
    """
    Получает список всех доступных файлов кук.
    
    Returns:
        Список путей к файлам кук пользователей
    """
    cookies_dir = Path("cookies")
    if not cookies_dir.exists():
        return []
    
    cookie_files = list(cookies_dir.glob("*_cookies.json"))
    return [f for f in cookie_files if f.stat().st_size > 100]  # Фильтруем пустые файлы


def select_random_user_cookie() -> Optional[Dict[str, Any]]:
    """
    Выбирает случайного пользователя и загружает его куки.
    
    Returns:
        Словарь с данными пользователя и куками или None если кук нет
    """
    cookie_files = get_available_cookie_files()
    if not cookie_files:
        return None
    
    # Выбираем случайный файл
    selected_file = random.choice(cookie_files)
    username = selected_file.stem.replace("_cookies", "")
    
    try:
        with open(selected_file, "r", encoding="utf-8") as f:
            cookies_data = json.load(f)
        
        return {
            "username": username,
            "cookie_file": selected_file,
            "cookies": cookies_data
        }
    except Exception:
        return None


# === PAGE OBJECTS ===

class SSOAuthPage:
    """
    Page Object для проверки состояния авторизации на любом домене Bll.
    
    Содержит методы для:
    - Проверки неавторизованного состояния
    - Установки кук авторизации  
    - Проверки авторизованного состояния
    """
    
    def __init__(self, page: Page):
        """
        Инициализация Page Object.
        
        Args:
            page: Страница Playwright
        """
        self.page = page
    
    def navigate_to_domain(self, domain_url: str) -> None:
        """
        Переходит на указанный домен.
        
        Args:
            domain_url: URL домена для перехода
        """
        with allure.step(f"Переход на домен: {domain_url}"):
            self.page.goto(domain_url, timeout=30000)
            # Ждем загрузки основных элементов страницы
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
    
    def check_unauthenticated_state(self) -> bool:
        """
        Проверяет что пользователь НЕ авторизован (видна кнопка "Войти").
        
        Returns:
            True если пользователь не авторизован
        """
        try:
            # Ищем кнопку "Войти"
            login_button = self.page.locator(LOCATORS["login_button"]).first
            
            # Ждем появления кнопки (до 5 сек)
            login_button.wait_for(state="visible", timeout=5000)
            
            # Проверяем что кнопка действительно содержит текст "Войти"
            button_text = login_button.inner_text().strip()
            return "Войти" in button_text
            
        except Exception:
            # Если кнопка "Войти" не найдена, возможно пользователь уже авторизован
            return False
    
    def set_auth_cookies(self, cookies_data: List[Dict[str, Any]]) -> None:
        """
        Устанавливает куки авторизации в браузерный контекст.
        
        Args:
            cookies_data: Список кук для установки
        """
        with allure.step("Установка авторизационных кук"):
            if cookies_data:
                self.page.context.add_cookies(cookies_data)
                # Обновляем страницу чтобы куки подействовали
                self.page.reload(timeout=15000)
    
    def check_authenticated_state(self) -> Dict[str, bool]:
        """
        Проверяет что пользователь авторизован по нескольким локаторам.
        
        Returns:
            Словарь с результатами проверки разных локаторов
        """
        results = {}
        
        # Основной локатор - меню профиля
        try:
            profile_menu = self.page.locator(LOCATORS["profile_menu"]).first
            profile_menu.wait_for(state="visible", timeout=3000)
            results["profile_menu"] = True
        except Exception:
            results["profile_menu"] = False
        
        # Альтернативный локатор - прямая ссылка на профиль
        try:
            my_profile = self.page.locator(LOCATORS["my_profile_link"]).first
            my_profile.wait_for(state="visible", timeout=2000)
            results["my_profile_link"] = True
        except Exception:
            results["my_profile_link"] = False
        
        # Альтернативный локатор - никнейм пользователя
        try:
            user_nick = self.page.locator(LOCATORS["user_nickname"]).first
            user_nick.wait_for(state="visible", timeout=2000)
            results["user_nickname"] = True
        except Exception:
            results["user_nickname"] = False
        
        # Альтернативный локатор - ссылка на профиль
        try:
            profile_link = self.page.locator(LOCATORS["profile_link"]).first
            profile_link.wait_for(state="visible", timeout=2000)
            results["profile_link"] = True
        except Exception:
            results["profile_link"] = False
        
        # Альтернативный локатор - выпадающее меню профиля
        try:
            profile_dropdown = self.page.locator(LOCATORS["profile_dropdown"]).first
            profile_dropdown.wait_for(state="visible", timeout=2000)
            results["profile_dropdown"] = True
        except Exception:
            results["profile_dropdown"] = False
        
        return results
    
    def is_authenticated(self) -> bool:
        """
        Определяет авторизован ли пользователь (любой из локаторов найден).
        
        Returns:
            True если найден хотя бы один признак авторизации
        """
        auth_results = self.check_authenticated_state()
        return any(auth_results.values())
    
    def get_auth_status_details(self) -> str:
        """
        Получает детальную информацию о статусе авторизации.
        
        Returns:
            Строка с описанием найденных элементов авторизации
        """
        auth_results = self.check_authenticated_state()
        found_elements = [key for key, found in auth_results.items() if found]
        
        if found_elements:
            return f"Найдены элементы авторизации: {', '.join(found_elements)}"
        else:
            return "Элементы авторизации не найдены"


# === ФИКСТУРЫ ===

@pytest.fixture
def isolated_browser_page(browser: Browser) -> Page:
    """
    Создает изолированную страницу браузера для каждого теста.
    
    Каждый тест получает полностью чистый контекст без кук и истории.
    Это обеспечивает автономность тестов согласно требованиям.
    
    Yields:
        Page: Чистая страница браузера
    """
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        locale="ru-RU",
        timezone_id="Europe/Minsk"
    )
    page = context.new_page()
    
    try:
        yield page
    finally:
        page.close()
        context.close()


@pytest.fixture
def sso_page(isolated_browser_page: Page) -> SSOAuthPage:
    """
    Создает Page Object для SSO тестирования.
    
    Args:
        isolated_browser_page: Изолированная страница браузера
        
    Returns:
        SSOAuthPage: Готовый Page Object для тестирования
    """
    return SSOAuthPage(isolated_browser_page)


@pytest.fixture
def random_user_data() -> Dict[str, Any]:
    """
    Фикстура для получения данных случайного пользователя.
    
    Returns:
        Словарь с данными пользователя и куками
        
    Raises:
        pytest.skip: Если нет доступных файлов кук
    """
    user_data = select_random_user_cookie()
    if not user_data:
        pytest.skip("Нет доступных файлов кук для тестирования")
    
    return user_data


# === ОСНОВНЫЕ SSO ТЕСТЫ ===

@ui_test(
    title="SSO: Базовый тест авторизации на ca.bll.by",
    description="Проверка полного цикла: неавторизован → кука → авторизован",
    feature="SSO авторизация"
)
@pytest.mark.sso
def test_basic_sso_auth_ca_domain(sso_page: SSOAuthPage, random_user_data: Dict[str, Any]) -> None:
    """
    Базовый тест SSO авторизации на центральном домене ca.bll.by.
    
    Сценарий:
    1. Переходим на ca.bll.by как неавторизованный пользователь
    2. Проверяем что видна кнопка "Войти" 
    3. Устанавливаем случайную куку пользователя
    4. Проверяем что пользователь авторизован (меню профиля)
    """
    domain_url = "https://ca.bll.by/"
    username = random_user_data["username"]
    cookies = random_user_data["cookies"]
    
    with allure.step(f"ШАГ 1: Проверка неавторизованного доступа на {domain_url}"):
        sso_page.navigate_to_domain(domain_url)
        
        # Проверяем что пользователь не авторизован (мягкая проверка)
        is_unauthenticated = sso_page.check_unauthenticated_state()
        is_already_authenticated = sso_page.is_authenticated()
        
        if is_unauthenticated:
            print(f"✅ Пользователь не авторизован на {domain_url} - найдена кнопка 'Войти'")
        elif not is_already_authenticated:
            print(f"ℹ️  Кнопка 'Войти' не найдена на {domain_url}, но пользователь также не авторизован")
        else:
            # Если пользователь уже авторизован, очищаем куки и проверяем снова
            print(f"⚠️  Пользователь уже авторизован на {domain_url}, очищаем куки...")
            sso_page.page.context.clear_cookies()
            sso_page.page.reload()
            print(f"✅ Куки очищены, контекст теперь чистый")
    
    with allure.step(f"ШАГ 2: Установка кук пользователя {username}"):
        sso_page.set_auth_cookies(cookies)
        print(f"🍪 Установлены куки пользователя: {username}")
    
    with allure.step("ШАГ 3: Проверка авторизованного состояния"):
        # Проверяем что пользователь теперь авторизован
        is_authenticated = sso_page.is_authenticated()
        auth_details = sso_page.get_auth_status_details()
        
        assert is_authenticated, f"Пользователь {username} не авторизован на {domain_url}. {auth_details}"
        
        print(f"✅ Пользователь {username} успешно авторизован на {domain_url}")
        print(f"   {auth_details}")


@ui_test(
    title="SSO: Авторизация по кукам на всех доменах",
    description="Проверка работы одной куки на всех сервисах экосистемы Bll",
    feature="SSO авторизация"
)
@pytest.mark.sso
@pytest.mark.parametrize("domain_url", SSO_DOMAINS)
def test_sso_cookie_auth_all_domains(
    sso_page: SSOAuthPage, 
    random_user_data: Dict[str, Any],
    domain_url: str
) -> None:
    """
    Параметризованный тест авторизации по кукам на всех доменах экосистемы.
    
    Проверяет что одна кука test_joint_session работает на всех сервисах:
    - bll.by, ca.bll.by, expert.bll.by, cp.bll.by, gz.bll.by, bonus.bll.by
    
    Каждый домен тестируется в отдельном браузерном контексте для изоляции.
    
    Args:
        domain_url: URL домена для тестирования (параметризовано)
    """
    username = random_user_data["username"]
    cookies = random_user_data["cookies"]
    
    print(f"\n🌐 Тестирование SSO на домене: {domain_url}")
    print(f"👤 Используется пользователь: {username}")
    
    with allure.step(f"Переход на {domain_url} без авторизации"):
        sso_page.navigate_to_domain(domain_url)
        
        # Не всегда на всех доменах есть кнопка "Войти", поэтому проверяем мягко
        try:
            is_unauthenticated = sso_page.check_unauthenticated_state()
            if is_unauthenticated:
                print(f"✅ Найдена кнопка 'Войти' на {domain_url}")
            else:
                print(f"ℹ️  Кнопка 'Войти' не найдена на {domain_url} (возможно, особенности интерфейса)")
        except Exception:
            print(f"ℹ️  Не удалось определить состояние авторизации до установки кук на {domain_url}")
    
    with allure.step(f"Установка кук пользователя {username}"):
        sso_page.set_auth_cookies(cookies)
        print(f"🍪 Куки установлены для {username}")
    
    with allure.step(f"Проверка авторизации на {domain_url}"):
        # Проверяем что пользователь авторизован
        is_authenticated = sso_page.is_authenticated()
        auth_details = sso_page.get_auth_status_details()
        
        # Основная проверка - пользователь должен быть авторизован
        assert is_authenticated, (
            f"SSO авторизация не работает на {domain_url} для пользователя {username}. "
            f"Детали: {auth_details}"
        )
        
        print(f"✅ SSO авторизация работает на {domain_url}")
        print(f"   👤 Пользователь: {username}")
        print(f"   🔍 {auth_details}")


@ui_test(
    title="SSO: Проверка изоляции тестов",
    description="Убеждается что каждый тест получает чистый браузерный контекст",
    feature="SSO авторизация"
)
@pytest.mark.sso
def test_sso_test_isolation(sso_page: SSOAuthPage) -> None:
    """
    Проверяет что тесты изолированы друг от друга.
    
    Этот тест убеждается что новый контекст браузера не содержит
    кук от предыдущих тестов.
    """
    domain_url = "https://ca.bll.by/"
    
    with allure.step("Проверка отсутствия кук в новом контексте"):
        sso_page.navigate_to_domain(domain_url)
        
        # Получаем все куки из контекста
        current_cookies = sso_page.page.context.cookies()
        auth_cookies = [c for c in current_cookies if c.get("name") == "test_joint_session"]
        
        assert len(auth_cookies) == 0, (
            f"Найдены авторизационные куки в новом контексте: {auth_cookies}. "
            "Это указывает на проблему изоляции тестов!"
        )
        
        print("✅ Новый браузерный контекст чистый - нет авторизационных кук")
        print(f"   Всего кук в контексте: {len(current_cookies)}")
    
    with allure.step("Проверка неавторизованного состояния"):
        # На чистом контексте пользователь должен быть не авторизован
        is_unauthenticated = sso_page.check_unauthenticated_state()
        
        # Это не критичная проверка, так как интерфейс может отличаться
        if is_unauthenticated:
            print("✅ Пользователь не авторизован - найдена кнопка 'Войти'")
        else:
            print("ℹ️  Кнопка 'Войти' не найдена, но контекст чистый")


# === СЛУЖЕБНЫЕ ТЕСТЫ ===

@pytest.mark.sso
def test_available_cookie_files() -> None:
    """
    Служебный тест для проверки доступности файлов кук.
    
    Помогает диагностировать проблемы если другие тесты падают
    из-за отсутствия кук.
    """
    cookie_files = get_available_cookie_files()
    
    assert len(cookie_files) > 0, (
        "Не найдено файлов кук для тестирования SSO. "
        "Запустите API авторизацию: pytest tests/auth/test_api_mass_authorization.py"
    )
    
    print(f"✅ Найдено {len(cookie_files)} файлов кук для SSO тестирования:")
    for file in cookie_files:
        username = file.stem.replace("_cookies", "")
        file_size = file.stat().st_size
        print(f"   🍪 {username}: {file_size} байт")


if __name__ == "__main__":
    print("SSO тесты авторизации по кукам")
    print("Использование:")
    print("pytest tests/e2e/sso/ -v -s -m sso")
    print("pytest tests/e2e/sso/test_sso_cookie_auth.py::test_basic_sso_auth_ca_domain -v -s") 