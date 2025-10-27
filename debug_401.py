#!/usr/bin/env python3
"""
Отладка HTTP 401 - анализ ответа сервера
"""

from framework.utils.smart_auth_manager import SmartAuthManager
import requests

def debug_401_response():
    print("=== АНАЛИЗ ОТВЕТА 401 ===\n")

    manager = SmartAuthManager()

    # Получаем куку
    session_cookie = manager.get_valid_session_cookie(role="admin")
    if not session_cookie:
        print("❌ Не удалось получить куку")
        return

    print(f"Получена кука: {session_cookie[:50]}...")

    # Создаем такой же запрос manual
    base_url = "https://expert.bll.by"
    question_text = "DEBUG 401 ANALYSIS TEST"

    try:
        from requests_toolbelt import MultipartEncoder

        # Создаем form-data
        form_data = MultipartEncoder(
            fields={'p': question_text}
        )

        # Настраиваем заголовки
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Referer': f'{base_url}/',
            'Origin': base_url,
            'Content-Type': form_data.content_type
        }

        # Отправляем запрос напрямую
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        response = session.post(
            f"{base_url}/questions?allow-session=2",
            data=form_data,
            cookies={"test_joint_session": session_cookie},
            headers=headers
        )

        print("=== ОТВЕТ СЕРВЕРА ===")
        print(f"Статус код: {response.status_code}")
        print(f"Заголовки ответа:")
        for name, value in response.headers.items():
            print(f"  {name}: {value}")

        print(f"\nТекст ответа (первые 500 символов):")
        print(response.text[:500])

        if response.status_code == 401:
            print("\n🔍 АНАЛИЗ 401:")
            possible_reasons = [
                "Кука невалидна для этого домена (expert.bll.by требует отдельной авторизации)",
                "Авторизация устарела или истекла",
                "Кука имеет неправильную область (только .bll.by не покрывает expert.bll.by)",
                "Сервер expert.bll.by использует другой механизм авторизации",
                "Может требоваться активация куки другим запросом"
            ]
            for reason in possible_reasons:
                print(f"  - {reason}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

    print("\n=== КОНЕЦ АНАЛИЗА ===")

if __name__ == "__main__":
    debug_401_response()
