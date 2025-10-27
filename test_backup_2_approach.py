#!/usr/bin/env python3
"""
Тест backup_2.py подхода (mass_api_auth + Dict куки)
"""

from framework.utils.smart_auth_manager_backup_2 import SmartAuthManager
from framework.utils.html_parser import ModerationPanelParser
from framework.utils.question_factory import QuestionFactory

def test_backup_2_api_approach():
    """Тестирование backup_2.py с Dict куки в API контексте"""

    # Инициализируем компоненты - адаптируем для Dict куки
    auth_manager = SmartAuthManager()
    panel_parser = ModerationPanelParser()
    question_factory = QuestionFactory()

    # Генерируем тест сигнал
    marker = "BACKUP2_TEST_DICT_COOKIE"
    base_question = question_factory.generate_question(category="регистрация")
    question_text = f"{marker} — {base_question}"

    print(f"📝 Тестовый вопрос: {question_text}")
    print(f"🔑 Маркер поиска: {marker}")

    # ШАГ 1: Получаем Dict куку
    print("\n🔐 Получаем Dict куку из backup_2.py...")
    cookie_result = auth_manager.get_valid_session_cookie(role="admin")

    if cookie_result and isinstance(cookie_result, dict):
        print("✅", end=" ")
        print(f"Получен Dict куки с {len(cookie_result)} полями")
        print(f"   Name: {cookie_result.get('name')}")
        print(f"   Domai: {cookie_result.get('domain')}")
        print(f"   sameSite: {cookie_result.get('sameSite')}")
        cookie_value = cookie_result.get('value')
        if cookie_value:
            print(f"   ✅ Значение куки получено (длина: {len(cookie_value)})")
        else:
            print("❌ Значение куки отсутствует в Dict")
            return False
    else:
        print("❌ backup_2.py вернул не Dict куку или None")
        return False

    # ШАГ 2: Отправляем вопрос через API (используем Dict куки)
    print("\n📨 Отправляем вопрос через API...")
    result = auth_manager.test_question_submission(cookie_value, question_text)  # передаем string значение
    assert result["valid"], f"❌ Кука невалидна: {result['message']}"
    assert result["success"], f"❌ Ошибка отправки вопроса: {result['message']}"
    assert result["status_code"] == 200, f"❌ Неожиданный статус код: {result['status_code']}"
    print("✅ Вопрос отправлен успешно!")

    # ШАГ 3: Проверяем наличие вопроса в панели модерации
    print("\n🔍 Проверяем панель модерации...")
    try:
        # Получаем данные из панели - передаем string куку
        panel_data = panel_parser.get_moderation_panel_data(cookie_value, limit=50)

        if not panel_data:
            print("❌ Панель модерации пуста или недоступна")
            return False

        print(f"✅ Получено записей из панели: {len(panel_data)}")

        # Ищем наш вопрос по маркеру (Dict не мешает API работе)
        found_question = None
        for entry in panel_data:
            text_value = (entry.get("text", "") or "").lower()
            if marker.lower() in text_value:
                found_question = entry
                break

        if found_question:
            print("✅ ТЕСТ ПРОШЕЛ! backup_2.py (Dict куки) работает:")
            print(f"   👤 Пользователь: {found_question.get('user', 'N/A')}")
            print(f"   📅 Дата: {found_question.get('date', 'N/A')}")
            print(f"   🏷️  Тип: {found_question.get('type', 'N/A')}")
            print(f"   📝 Текст: {found_question.get('text', 'N/A')[:100]}...")
            print(f"   🆔 ID: {found_question.get('id', 'N/A')}")

            print("\n🎉 backup_2.py (mass_api_auth + Dict куки) РАБОТАЕТ С API!")
            return True
        else:
            print(f"❌ Вопрос с маркером '{marker}' не найден в панели модерации")
            return False

    except Exception as e:
        print(f"❌ Ошибка при проверке панели модерации: {e}")
        return False

if __name__ == "__main__":
    print("=== ТЕСТИРОВАНИЕ BACKUP_2.PY (mass_api_auth + Dict куки) ===\n")

    success = test_backup_2_api_approach()

    print("\n" + "="*65)
    if success:
        print("🎊 РЕЗУЛЬТАТ: backup_2.py (Dict куки) РАБОТАЕТ С API ТЕСТАМИ!")
        print("💡 Хороший backup - авторизация mass_api_auth, куки в Dict формате")
    else:
        print("✖️ РЕЗУЛЬТАТ: backup_2.py НЕ РАБОТАЕТ С API ТЕСТАМИ")
        print("💡 Не подходит для integration тестов")

    print("="*65)
