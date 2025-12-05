#!/usr/bin/env python3
"""
Тест integration с новым API подходом авторизации
"""

import os
from framework.utils.smart_auth_api_approach import SmartAuthManager
from framework.utils.html_parser import ModerationPanelParser
from framework.utils.question_factory import QuestionFactory

def test_integration_api_approach():
    """Тестирование integration теста с новым API подходом"""

    # Инициализируем компоненты
    auth_manager = SmartAuthManager()
    panel_parser = ModerationPanelParser()
    question_factory = QuestionFactory()

    # Генерируем тест сигнал
    marker = "INTEGRATION_TEST_MARKER_API"
    base_question = question_factory.generate_question(category="регистрация")
    question_text = f"{marker} — {base_question}"

    print(f"📝 Тестовый вопрос: {question_text}")
    print(f"🔑 Маркер поиска: {marker}")

    # ШАГ 1: Получаем валидную сессионную куку
    print("\n🔐 Получаем куку авторизации...")
    session_cookie = auth_manager.get_valid_session_cookie(role=os.getenv("TEST_ROLE", "admin"))
    assert session_cookie, "❌ Не удалось получить валидную сессионную куку"
    print(f"✅ Куки получена (длина: {len(session_cookie)})")

    # ШАГ 2: Отправляем вопрос через API
    print("\n📨 Отправляем вопрос...")
    result = auth_manager.test_question_submission(session_cookie, question_text)
    assert result["valid"], f"❌ Кука невалидна: {result['message']}"
    assert result["success"], f"❌ Ошибка отправки вопроса: {result['message']}"
    assert result["status_code"] == 200, f"❌ Неожиданный статус код: {result['status_code']}"
    print("✅ Вопрос отправлен успешно!")

    # ШАГ 3: Проверяем наличие вопроса в панели модерации
    print("\n🔍 Проверяем панель модерации...")
    try:
        # Получаем данные из панели
        panel_data = panel_parser.get_moderation_panel_data(session_cookie, limit=50)

        if not panel_data:
            print("❌ Панель модерации пуста или недоступна")
            return False

        print(f"✅ Получено записей из панели: {len(panel_data)}")

        # Ищем наш вопрос по маркеру
        found_question = None
        for entry in panel_data:
            text_value = (entry.get("text", "") or "").lower()
            if marker.lower() in text_value:
                found_question = entry
                break

        if found_question:
            print("✅ ТЕСТ ПРОШЕЛ! Вопрос найден в панели модерации:")
            print(f"   👤 Пользователь: {found_question.get('user', 'N/A')}")
            print(f"   📅 Дата: {found_question.get('date', 'N/A')}")
            print(f"   🏷️  Тип: {found_question.get('type', 'N/A')}")
            print(f"   📝 Текст: {found_question.get('text', 'N/A')[:100]}...")
            print(f"   🆔 ID: {found_question.get('id', 'N/A')}")

            print("\n🎉 INTEGRATION ТЕСТ С НОВЫМ API ПОДХОДОМ ПРОШЕЛ УСПЕШНО!")
            return True
        else:
            print(f"❌ Вопрос с маркером '{marker}' не найден в панели модерации")
            print("   🔍 Последние записи в панели:")
            for i, entry in enumerate(panel_data[:3], 1):
                user = entry.get('user', 'N/A')
                text = (entry.get('text', 'N/A') or '')[:50]
                print(f"      {i}. {user}: {text}...")
            return False

    except Exception as e:
        print(f"❌ Ошибка при проверке панели модерации: {e}")
        return False

if __name__ == "__main__":
    print("=== ТЕСТИРОВАНИЕ INTEGRATION С НОВЫМ API ПОДХОДОМ ===\n")

    success = test_integration_api_approach()

    print("\n" + "="*60)
    if success:
        print("🎊 РЕЗУЛЬТАТ: API ПОДХОД ПОЛНОСТЬЮ СОВМЕСТИМ С INTEGRATION ТЕСТАМИ!")
        print("💡 Рекомендация: Заменить основной smart_auth_manager.py на smart_auth_api_approach.py")
    else:
        print("✖️ РЕЗУЛЬТАТ: API ПОДХОД НЕ СОВМЕСТИМ С INTEGRATION ТЕСТАМИ")
        print("💡 Требуется дальнейшая доработка")

    print("="*60)
