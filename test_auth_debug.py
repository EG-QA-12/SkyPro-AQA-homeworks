#!/usr/bin/env python3
"""
Отладка SmartAuthManager - диагностика проблемы с куками
"""

from framework.utils.smart_auth_manager import SmartAuthManager

def test_auth_flow():
    print("=== ДИАГНОСТИКА SMARTAUTHMANAGER ===\n")

    manager = SmartAuthManager()

    # 1. Получаем куку строкой
    print("1. Получение строковой куки...")
    session_cookie = manager.get_valid_session_cookie(role="admin")

    if session_cookie:
        print(f"✅ Получили куку: {session_cookie[:30]}...")
        length = len(session_cookie)
        print(f"   Длина куки: {length} символов")
    else:
        print("❌ Не удалось получить куку")
        return

    # 2. Получаем куки списком
    print("\n2. Получение списка куки...")
    cookies_list = manager.get_valid_cookies_list(role="admin")

    if cookies_list:
        print(f"✅ Получили список из {len(cookies_list)} куки")
        for i, cookie in enumerate(cookies_list, 1):
            print(f"   {i}. {cookie['name']}: {cookie['value'][:20]}... (domain: {cookie.get('domain')})")
    else:
        print("❌ Не удалось получить список куки")

    # 3. Тестируем отправку вопроса
    print("\n3. Тест отправки вопроса...")
    try:
        result = manager.test_question_submission(session_cookie, "TEST DIAGNOSIS MARKER")
        print("Результат теста:")
        print(f"   Валидна кука: {result.get('valid', 'Unknown')}")
        print(f"   Успех отправки: {result.get('success', 'Unknown')}")
        print(f"   HTTP код: {result.get('status_code', 'Unknown')}")
        print(f"   Сообщение: {result.get('message', 'No message')}")

        if result.get('valid'):
            print("✅ Авторизация прошла успешно!")
        else:
            print("❌ Авторизация провалилась!")

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

    print("\n=== КОНЕЦ ДИАГНОСТИКИ ===")

if __name__ == "__main__":
    test_auth_flow()
