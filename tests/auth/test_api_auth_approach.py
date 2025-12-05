#!/usr/bin/env python3
"""
Тест нового API подхода авторизации
"""

from framework.utils.smart_auth_api_approach import SmartAuthManager

def test_new_api_approach():
    print("=== ТЕСТИРОВАНИЕ НОВОГО API ПОДХОДА ===\n")

    # Создаем экземпляр с новой логикой
    manager = SmartAuthManager()

    # 1. Получаем string куку
    print("1. Получение string куки...")
    session_cookie = manager.get_valid_session_cookie(role="admin")

    if session_cookie:
        print("✅", end=" ")
        # Не показываем строку целиком из соображений безопасности
        print(f"Получили куку длиной {len(session_cookie)} символов")
    else:
        print("❌ Не удалось получить куку")
        return

    # 2. Тестируем отправку вопроса
    print("\n2. Тест отправки вопроса...")
    try:
        result = manager.test_question_submission(session_cookie, "TEST API APPROACH MARKER")

        print("Результат:")
        print(f"   Валидна кука: {result.get('valid', 'Unknown')}")
        print(f"   Успех отправки: {result.get('success', 'Unknown')}")
        print(f"   HTTP код: {result.get('status_code', 'Unknown')}")
        print(f"   Сообщение: {result.get('message', 'No message')}")

        if result.get('valid') and result.get('success'):
            print("✅ НОВЫЙ API ПОДХОД РАБОТАЕТ!")
            print("\n🎉 Теперь можно использовать этот подход для integration тестов")
            return True
        else:
            print("❌ API подход не работает")
            return False

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

    print("\n=== КОНЕЦ ТЕСТИРОВАНИЯ ===")

if __name__ == "__main__":
    success = test_new_api_approach()
    if success:
        print("\n💡 РЕКОМЕНДАЦИЯ: Заменить основной smart_auth_manager.py на новый api подход")
    else:
        print("\n💡 Необходимо доработать API подход")
