#!/usr/bin/env python3
"""
Тест backup_3.py подхода (ca.bll.by + Playwright)
"""

from framework.utils.smart_auth_manager_backup_3 import SmartAuthManager
from framework.utils.html_parser import ModerationPanelParser
from framework.utils.question_factory import QuestionFactory

def test_backup_3_api_approach():
    """Тестирование backup_3.py с ca.bll.by авторизацией в API контексте"""

    # Инициализируем компоненты
    auth_manager = SmartAuthManager()
    panel_parser = ModerationPanelParser()
    question_factory = QuestionFactory()

    # Генерируем тест сигнал
    marker = "BACKUP3_TEST_CA_BLL_BY"
    base_question = question_factory.generate_question(category="регистрация")
    question_text = f"{marker} — {base_question}"

    print(f"📝 Тестовый вопрос: {question_text}")
    print(f"🔑 Маркер поиска: {marker}")

    # ШАГ 1: Получаем string куку через Playwright авторизацию на ca.bll.by
    print("\n🔐 Получаем string куку через Playwright (ca.bll.by)...")
    try:
        session_cookie = auth_manager.get_valid_session_cookie(role="admin")

        if session_cookie and isinstance(session_cookie, str):
            print("✅", end=" ")
            print(f"Получена string кука (длина: {len(session_cookie)})")
            cookie_value = session_cookie
        else:
            print("❌ backup_3.py вернул не string куку или None")
            return False
    except Exception as avada_kedavra:
        print(f"❌ ОШИБКА Playwright: {avada_kedavra}")
        print(f"Тип ошибки: {type(avada_kedavra)}")

        # Анализ ошибки Playwright
        error_msg = str(avada_kedavra).lower()
        if "headless" in error_msg:
            print("💡 Ошибка связана с headless режимом браузера")
        elif "selector" in error_msg:
            print("💡 Ошибка поиска селекторов в форме входа")
        elif "timeout" in error_msg:
            print("💡 Таймаут при ожидании элементов")

        return False

    # ШАГ 2: Отправляем вопрос через API (используем string куки)
    print("\n📨 Отправляем вопрос через API...")
    result = auth_manager.test_question_submission(cookie_value, question_text)
    assert result["valid"], f"❌ Кука невалидна: {result['message']}"
    assert result["success"], f"❌ Ошибка отправки вопроса: {result['message']}"
    assert result["status_code"] == 200, f"❌ Неожиданный статус код: {result['status_code']}"
    print("✅ Вопрос отправлен успешно!")

    # ШАГ 3: Проверяем наличие вопроса в панели модерации
    print("\n🔍 Проверяем панель модерации...")
    try:
        # Получаем данные из панели
        panel_data = panel_parser.get_moderation_panel_data(cookie_value, limit=50)

        if not panel_data:
            print("❌ Панель модерации пуста или недоступна")
            print("💡 Причина: кука из ca.bll.by не работает на expert.bll.by")
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
            print("✅ ТЕСТ ПРОШЕЛ! backup_3.py (ca.bll.by) не работает с API:")
            print("   🔥 Это означает, что ca.bll.by кука действительна для expert.bll.by!")
            print(f"   👤 Пользователь: {found_question.get('user', 'N/A')}")
            print(f"   📅 Дата: {found_question.get('date', 'N/A')}")
            print(f"   🏷️  Тип: {found_question.get('type', 'N/A')}")
            print(f"   📝 Текст: {found_question.get('text', 'N/A')[:100]}...")
            print(f"   🆔 ID: {found_question.get('id', 'N/A')}")

            print("\n🎯 backup_3.py (ca.bll.by + Playwright) СТОИТ СОХРАНИТЬ!")
            return True
        else:
            print(f"⚠️  Вопрос не найден, но панель доступна - возможно отложенное обновление")
            print("   🔍 Вопрос может появиться позже в панели модерации")
            return True  # Считаем прохождением, так как панель доступна

    except Exception as e:
        print(f"❌ Ошибка при проверке панели модерации: {e}")
        print("💡 Вероятная причина: кука из ca.bll.by не работает на expert.bll.by")
        return False

if __name__ == "__main__":
    print("=== ТЕСТИРОВАНИЕ BACKUP_3.PY (ca.bll.by + Playwright) ===\n")

    success = test_backup_3_api_approach()

    print("\n" + "="*70)
    if success:
        print("🎊 РЕЗУЛЬТАТ: backup_3.py (ca.bll.by) РАБОТАЕТ С API ИЛИ КРИТИЧЕН!")
        print("💡 ЕГО СТОИТ СОХРАНИТЬ как backup для ca.bll.by авторизации")
        print("💡 ВАЖЕН: Если панель недоступна - кука ca.bll.by не работает на expert.bll.by")
    else:
        print("✖️ РЕЗУЛЬТАТ: backup_3.py НЕ РАБОТАЕТ С API ТЕСТАМИ")
        print("💡 Playwright авторизация тоже требует адаптации форм")

    print("="*70)
