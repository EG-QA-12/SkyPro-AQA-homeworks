"""
Модуль тестов для проверки авторизации модераторов.
"""
from playwright.sync_api import sync_playwright

from src.auth import authorize_and_save_cookies
from pages.login_page import LoginPage
from pages.moderator_dashboard_page import ModeratorDashboardPage
from src.config import config


def test_moderator_direct_login(cookies_path=None, login_url=None, target_url=None, headless=True):
    """
    Тестирует прямую авторизацию модератора через страницу логина и сохраняет куки.
    
    Args:
        cookies_path: Путь для сохранения кук (по умолчанию: данные из config)
        login_url: URL страницы логина (по умолчанию: данные из config)
        target_url: Целевой URL после авторизации (по умолчанию: данные из config)
        headless: Запускать браузер в headless режиме
        
    Returns:
        bool: True если авторизация прошла успешно
    """
    # Используем значения из конфигурации, если параметры не указаны
    if cookies_path is None:
        cookies_path = config.COOKIES_PATH.parent / f"{config.MODERATOR_LOGIN}_cookies.json"
    if login_url is None:
        login_url = config.LOGIN_URL
    if target_url is None:
        target_url = config.TARGET_URL
    
    print(f"🔐 Тест прямой авторизации модератора {config.MODERATOR_LOGIN}")
    print(f"📁 Сохранение кук в: {cookies_path}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context()
            page = context.new_page()
            
            print(f"🌐 Переход на страницу логина: {login_url}")
            # Переход на страницу логина и авторизация
            login_page = LoginPage(page)
            page.goto(login_url)
            login_page.login(config.MODERATOR_LOGIN, config.MODERATOR_PASS)
            
            print(f"🔎 Проверка успешности авторизации")
            # Проверяем URL после авторизации
            if not page.url.startswith(target_url):
                print(f"❌ Ошибка авторизации. Текущий URL: {page.url}, ожидался: {target_url}")
                return False
            
            # Переходим на панель модератора
            print(f"🧭 Переход на панель модератора")
            moderator_dashboard_page = ModeratorDashboardPage(page)
            
            # Пробуем сначала проверить наличие элементов модерации на текущей странице
            if moderator_dashboard_page.has_moderation_elements():
                print("✅ Найдены элементы модерации на текущей странице")
            else:
                # Пробуем перейти на панель модератора
                if not moderator_dashboard_page.navigate_to_dashboard():
                    print("❌ Панель модератора недоступна")
                    moderator_dashboard_page.take_screenshot("moderator_panel_unavailable.png")
                    return False
            
            if not moderator_dashboard_page.is_moderator_authorized():
                print("❌ Пользователь не авторизован как модератор")
                return False
            
            # Сохраняем куки для будущего использования
            print(f"💾 Сохранение кук модератора")
            cookies_path.parent.mkdir(exist_ok=True)
            context.storage_state(path=str(cookies_path))
            print(f"✅ Куки сохранены в {cookies_path}")
            
            browser.close()
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при авторизации модератора: {e}")
        return False


def test_moderator_cookie_auth(user_login=None, headless=True):
    """
    Тестирует авторизацию модератора через куки.
    
    Args:
        user_login: Логин пользователя-модератора (по умолчанию: MODERATOR_LOGIN из config)
        headless: Запускать браузер в headless режиме
        
    Returns:
        bool: True если авторизация через куки прошла успешно
    """
    from framework.utils.auth_utils import load_cookie
    
    # Используем значения из конфигурации, если параметры не указаны
    if user_login is None:
        user_login = config.MODERATOR_LOGIN
    
    # Формируем путь к файлу кук
    cookies_file = config.COOKIES_PATH.parent / f"{user_login}_cookies.json"
    
    print(f"🍪 Тест авторизации модератора {user_login} через куки")
    print(f"📁 Файл кук: {cookies_file}")
    
    if not cookies_file.exists():
        print(f"❌ Файл кук для пользователя {user_login} не найден: {cookies_file}")
        return False
    
    try:
        with sync_playwright() as p:
            # Запускаем браузер
            print(f"🌐 Запуск браузера (headless: {headless})...")
            browser = p.chromium.launch(headless=headless)
            
            # Загружаем куки
            cookies = load_cookie(cookies_file)
            if not cookies:
                print(f"❌ Не удалось загрузить куки из {cookies_file}")
                return False
            
            print(f"📊 Загружено {len(cookies)} кук")
            
            # Создаем новый контекст и добавляем куки
            context = browser.new_context()
            context.add_cookies(cookies)
            page = context.new_page()
            
            # Переходим на целевую страницу
            print(f"🔗 Переход на целевую страницу: {config.TARGET_URL}")
            page.goto(config.TARGET_URL, timeout=30000)
            
            # Проверяем успешную авторизацию
            if "/login" in page.url:
                print(f"❌ Ошибка авторизации через куки. Произошел редирект на страницу логина.")
                return False
            
            # Проверяем права модератора
            print(f"🔎 Проверка прав модератора")
            moderator_dashboard_page = ModeratorDashboardPage(page)
            if moderator_dashboard_page.is_moderator_authorized():
                print(f"✅ Пользователь {user_login} успешно авторизован как модератор через куки")
                return True
            else:
                print(f"❌ Пользователь {user_login} не имеет прав модератора")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка при тестировании авторизации через куки: {e}")
        return False


def validate_moderator_permissions(user_login=None, headless=True):
    """
    Валидирует права модератора после авторизации через куки.
    
    Args:
        user_login: Логин пользователя-модератора (по умолчанию: MODERATOR_LOGIN из config)
        headless: Запускать браузер в headless режиме
        
    Returns:
        bool: True если права модератора подтверждены
    """
    # Используем значения из конфигурации, если параметры не указаны
    if user_login is None:
        user_login = config.MODERATOR_LOGIN
    
    print(f"🔍 Валидация прав модератора для пользователя {user_login}")
    
    # Сначала выполняем авторизацию через куки
    if not test_moderator_cookie_auth(user_login, headless):
        print("❌ Не удалось авторизоваться как модератор через куки")
        return False
    
    # Если авторизация успешна, продолжаем с проверкой прав
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context()
            page = context.new_page()
            
            # Загружаем куки
            cookies_file = config.COOKIES_PATH.parent / f"{user_login}_cookies.json"
            from framework.utils.auth_utils import load_cookie
            cookies = load_cookie(cookies_file)
            context.add_cookies(cookies)
            
            # Переходим на панель модератора
            print(f"🧭 Проверка доступа к панели модератора")
            moderator_dashboard_page = ModeratorDashboardPage(page)
            if not moderator_dashboard_page.navigate_to_dashboard():
                print("❌ Панель модератора недоступна")
                return False
            
            # Проверяем наличие элементов модерации
            if not moderator_dashboard_page.has_moderation_elements():
                print("❌ Элементы модерации не найдены")
                return False
            
            # Получаем количество элементов для модерации
            items_count = moderator_dashboard_page.get_moderation_items_count()
            print(f"📊 Элементов для модерации: {items_count}")
            
            browser.close()
            print(f"✅ Права модератора для пользователя {user_login} подтверждены")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при валидации прав модератора: {e}")
        return False
