"""
Тесты для проверки функциональности капчи на сайте BII.
"""
import pytest
from playwright.sync_api import Page
from framework.bii_buy_page import BiiBuyPage
import random
import string
from framework.utils.url_utils import add_allow_session_param, is_headless

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_phone():
    return "+37529" + ''.join(random.choices(string.digits, k=7))

def random_email():
    return random_string(5) + "@example.com"

def test_form_submission_triggers_captcha_bii(page: Page) -> None:
    """
    Проверяет, что быстрое заполнение и отправка формы на странице
    https://bii.by/buy активирует Yandex SmartCaptcha.

    Сценарий:
    1. Открыть страницу с формой.
    2. Быстро заполнить все обязательные поля.
    3. Проставить галочки согласия.
    4. Нажать кнопку "Отправить".
    5. Убедиться, что на странице появился iframe капчи.

    Args:
        page: Экземпляр playwright.sync_api.Page, предоставляемый фикстурой.
    """
    # 1. Инициализация и переход на страницу
    buy_page = BiiBuyPage(page)
    url = add_allow_session_param("https://bii.by/buy", is_headless())
    page.goto(url)
    
    # Заполнение формы данными. 
    buy_page.fill_form(
        fio="Тестов Тест Тестович",
        phone="+375291112233",
        company="Тест-Автоматизация",
        position="SDET Architect",
        email="test.automation@example.com",
    )

    # 4. Согласие с условиями
    buy_page.agree_to_terms()

    # 5. Нажатие на кнопку отправки
    buy_page.submit_form()

    # 6. Главная проверка: ожидаем появления iframe капчи.
    buy_page.wait_for_captcha_to_appear(timeout=15000)

    print("\nТест успешно завершен: iframe Yandex SmartCaptcha был обнаружен после отправки формы.")


def test_captcha_trigger_random_loop_bii(page: Page):
    """
    Многократное заполнение формы случайными данными с остановкой, если форма становится недоступна (капча заблокировала).
    После каждой попытки выводится результат (обнаружен ли iframe капчи и доступна ли форма).
    """
    buy_page = BiiBuyPage(page)
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

    success_count = 0
    for attempt in range(1, 101):
        print(f"\n=== Попытка {attempt} ===")
        buy_page.navigate()
        
        try:
            print("  Заполняем форму...")
            buy_page.fill_form(
                fio=random_string(12),
                phone=random_phone(),
                company=random_string(10),
                position=random_string(6),
                email=random_email(),
                promo=random_string(5)
            )
            print("  Ставим чекбокс...")
            buy_page.agree_to_terms()
            print("  Жмём кнопку 'Отправить'...")
            buy_page.submit_form()
            
            # Даём время на обработку формы и возможный редирект
            page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"  [Ошибка] Не удалось отправить форму — {type(e).__name__}: {e}")
            continue

        # Проверяем текущий URL после отправки формы
        current_url = page.url
        print(f"  [DEBUG] Текущий URL: {current_url}")
        
        # Если произошёл редирект на страницу благодарности - это ПРОВАЛ для теста капчи
        if "thanks" in current_url:
            print("  [Результат] ПРОВАЛ: заявка прошла без капчи, редирект на /thanks")
            success_count += 1
            continue
        else:
            print("  [Результат] КАПЧА СРАБОТАЛА: остались на странице формы")

            try:
                buy_page.wait_for_captcha_to_appear(timeout=2000)
                print("  ✅ Капча-iframe обнаружен - система защиты работает")
            except Exception:
                print("  ❌ Капча-iframe не обнаружен - возможна другая блокировка")

            page.wait_for_timeout(500)

    print(f"\nИТОГ: Успешных отправок (редирект на /thanks): {success_count} из 100 попыток.")

