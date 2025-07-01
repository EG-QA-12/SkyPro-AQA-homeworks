"""
Демонстрация использования системы управления секретами.

Этот файл показывает практические примеры использования:
- Загрузки конфигурации
- Работы с авторизационными данными
- Безопасного логирования
- Интеграции с Playwright тестами

Автор: Lead SDET Architect
Дата создания: 2025-06-27
"""

from pathlib import Path
import logging
from typing import Optional

# Настройка логирования для демо
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SecureDemo")


def demo_configuration_loading():
    """Демонстрация загрузки конфигурации."""
    print("🔧 ДЕМО: Загрузка конфигурации")
    print("=" * 50)
    
    try:
        from config.secrets_manager import get_config, validate_required_config
        
        # Загружаем конфигурацию
        config = get_config()
        
        print(f"✅ Окружение: {config.environment.value}")
        print(f"✅ Домен авторизации: {config.auth.domain}")
        print(f"✅ Имя куки: {config.auth.cookie_name}")
        print(f"✅ Режим отладки: {config.debug_mode}")
        print(f"✅ Headless режим: {config.headless}")
        print(f"✅ Таймаут браузера: {config.browser_timeout}ms")
        
        # Проверяем опциональные компоненты
        if config.api:
            print(f"✅ API URL: {config.api.base_url}")
        else:
            print("ℹ️  API не настроено")
        
        if config.database:
            print(f"✅ База данных: {config.database.host}:{config.database.port}")
        else:
            print("ℹ️  База данных не настроена")
        
        # Валидация обязательных секций
        validate_required_config(['auth'])
        print("✅ Валидация пройдена успешно")
        
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False
    
    return True


def demo_auth_manager():
    """Демонстрация работы с менеджером авторизации."""
    print("\n🔐 ДЕМО: Менеджер авторизации")
    print("=" * 50)
    
    try:
        from secure_auth_utils import SecureAuthManager
        
        # Создаем менеджер
        auth_manager = SecureAuthManager()
        
        print(f"✅ Менеджер создан для домена: {auth_manager.auth_credentials.domain}")
        
        # Демонстрация создания куки
        cookie_data = auth_manager.create_auth_cookie(
            value="demo_session_token_12345",
            custom_domain="test.example.com"
        )
        
        print(f"✅ Создана кука: {cookie_data.name}")
        print(f"   Домен: {cookie_data.domain}")
        print(f"   Путь: {cookie_data.path}")
        print(f"   Secure: {cookie_data.secure}")
        
        # Показываем Playwright формат
        playwright_cookie = cookie_data.to_playwright_format()
        print("✅ Формат для Playwright:")
        for key, value in playwright_cookie.items():
            if key != 'value':  # Не показываем значение для безопасности
                print(f"   {key}: {value}")
            else:
                print(f"   {key}: [HIDDEN]")
        
    except Exception as e:
        print(f"❌ Ошибка работы с менеджером авторизации: {e}")
        return False
    
    return True


def demo_file_operations():
    """Демонстрация файловых операций с куками."""
    print("\n📁 ДЕМО: Файловые операции")
    print("=" * 50)
    
    try:
        from secure_auth_utils import SecureAuthManager
        
        # Создаем временный файл для демо
        demo_dir = Path("demo_temp")
        demo_dir.mkdir(exist_ok=True)
        
        cookie_file = demo_dir / "demo_cookies.json"
        
        print(f"✅ Создана демо-директория: {demo_dir}")
        print(f"✅ Путь к файлу куки: {cookie_file}")
        
        # Симуляция сохранения куки (без реального браузерного контекста)
        print("ℹ️  В реальном тесте здесь будет:")
        print("   auth_manager.save_auth_cookie(context, 'demo_cookies.json')")
        print("   auth_manager.load_auth_cookie(context, 'demo_cookies.json')")
        
        # Очистка демо-файлов
        if demo_dir.exists():
            import shutil
            shutil.rmtree(demo_dir)
            print("✅ Демо-файлы очищены")
        
    except Exception as e:
        print(f"❌ Ошибка файловых операций: {e}")
        return False
    
    return True


def demo_security_features():
    """Демонстрация функций безопасности."""
    print("\n🔒 ДЕМО: Функции безопасности")
    print("=" * 50)
    
    try:
        from config.secrets_manager import secrets_manager
        
        # Показываем маскированный обзор конфигурации
        summary = secrets_manager.get_masked_config_summary()
        
        print("✅ Безопасный обзор конфигурации:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # Демонстрация безопасного получения переменных
        print("\n✅ Методы получения переменных:")
        
        # Показываем как НЕ надо делать
        print("❌ НЕПРАВИЛЬНО:")
        print("   password = 'hardcoded_password'  # Никогда так не делайте!")
        
        # Показываем правильный способ
        print("✅ ПРАВИЛЬНО:")
        print("   password = secrets_manager.get_required_env('AUTH_PASSWORD')")
        print("   debug = secrets_manager.get_bool_env('DEBUG_MODE', False)")
        print("   timeout = secrets_manager.get_int_env('TIMEOUT', 30)")
        
    except Exception as e:
        print(f"❌ Ошибка демонстрации безопасности: {e}")
        return False
    
    return True


def demo_playwright_integration():
    """Демонстрация интеграции с Playwright."""
    print("\n🎭 ДЕМО: Интеграция с Playwright")
    print("=" * 50)
    
    print("✅ Пример кода для интеграции с Playwright:")
    
    code_example = '''
# В ваших тестах используйте:
from secure_auth_utils import save_cookie, load_cookie, create_joint_cookie

def test_with_auth(browser_context):
    """Пример теста с авторизацией."""
    
    # 1. Авторизация и сохранение куки
    page = browser_context.new_page()
    page.goto("https://test.example.com/login")
    
    # ... логика авторизации ...
    
    # Сохраняем куки после успешной авторизации
    save_cookie(browser_context, "auth_cookies.json")
    
    # 2. В следующих тестах загружаем куки
    load_cookie(browser_context, "auth_cookies.json")
    
    # 3. Или создаем куку вручную
    cookie = create_joint_cookie(
        value="session_token",
        domain="test.example.com"
    )
    browser_context.add_cookies([cookie])

# Проверка авторизации
from secure_auth_utils import auth_manager

if auth_manager.check_auth_cookie_exists(browser_context):
    print("Пользователь авторизован")
else:
    print("Требуется авторизация")
'''
    
    print(code_example)
    
    return True


def demo_environment_management():
    """Демонстрация управления окружениями."""
    print("\n🌍 ДЕМО: Управление окружениями")
    print("=" * 50)
    
    try:
        from config.secrets_manager import secrets_manager, Environment
        
        print(f"✅ Текущее окружение: {secrets_manager.current_environment.value}")
        
        print("\n✅ Доступные окружения:")
        for env in Environment:
            is_current = env == secrets_manager.current_environment
            marker = "👈 текущее" if is_current else ""
            print(f"   {env.value} {marker}")
        
        print("\n✅ Файлы конфигурации по приоритету:")
        config_files = [
            "config/.env.local (локальные настройки)",
            "config/.env.test (тестовое окружение)",
            "config/.env.dev (разработка)",
            "config/.env (основные настройки)"
        ]
        
        for i, config_file in enumerate(config_files, 1):
            print(f"   {i}. {config_file}")
        
        print("\n✅ Для переключения окружения:")
        print("   Установите переменную TEST_ENVIRONMENT в .env файле")
        print("   Или используйте переменную окружения системы")
        
    except Exception as e:
        print(f"❌ Ошибка демонстрации окружений: {e}")
        return False
    
    return True


def main():
    """Главная функция демонстрации."""
    print("🚀 ДЕМОНСТРАЦИЯ СИСТЕМЫ УПРАВЛЕНИЯ СЕКРЕТАМИ")
    print("=" * 60)
    print("Этот скрипт показывает возможности созданной системы безопасности")
    print("=" * 60)
    
    demos = [
        ("Загрузка конфигурации", demo_configuration_loading),
        ("Менеджер авторизации", demo_auth_manager),
        ("Файловые операции", demo_file_operations),
        ("Функции безопасности", demo_security_features),
        ("Интеграция с Playwright", demo_playwright_integration),
        ("Управление окружениями", demo_environment_management)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            success = demo_func()
            results.append((demo_name, success))
        except Exception as e:
            logger.error(f"Критическая ошибка в демо '{demo_name}': {e}")
            results.append((demo_name, False))
    
    # Финальный отчет
    print("\n📊 РЕЗУЛЬТАТЫ ДЕМОНСТРАЦИИ")
    print("=" * 50)
    
    successful = 0
    for demo_name, success in results:
        status = "✅ УСПЕШНО" if success else "❌ ОШИБКА"
        print(f"{status}: {demo_name}")
        if success:
            successful += 1
    
    print(f"\nИтого: {successful}/{len(results)} демонстраций прошли успешно")
    
    if successful == len(results):
        print("\n🎉 ВСЕ ДЕМОНСТРАЦИИ УСПЕШНЫ!")
        print("Система управления секретами готова к использованию.")
    else:
        print("\n⚠️  Некоторые демонстрации не прошли.")
        print("Проверьте конфигурацию и зависимости.")
    
    print("\n📚 Для получения справки:")
    print("   python config/secrets_manager.py")
    print("   python secure_auth_utils.py")
    print("   Смотрите файл: config/README.md")


if __name__ == "__main__":
    main()
