"""
Тесты для проверки функциональности капчи на сайте BLL.
"""
import pytest
from playwright.sync_api import Page
from framework.buy_page import BuyPage
import random
import string

def random_string(length=8):
    """Генерирует случайную строку из букв заданной длины.
    
    Args:
        length: Длина генерируемой строки.
        
    Returns:
        Случайная строка из латинских букв.
    """
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_phone():
    """Генерирует случайный белорусский номер телефона.
    
    Returns:
        Номер телефона в формате +37529XXXXXXX.
    """
    return "+37529" + ''.join(random.choices(string.digits, k=7))

def random_email():
    """Генерирует случайный email-адрес.
    
    Returns:
        Email в формате xxxxx@example.com.
    """
    return random_string(5) + "@example.com"

def test_form_submission_triggers_captcha(page: Page) -> None:
    """
    Проверяет, что быстрое заполнение и отправка формы на странице
    https://bll.by/buy активирует Yandex SmartCaptcha.

    Сценарий:
    1. Открыть страницу с формой.
    2. Быстро заполнить все обязательные поля.
    3. Проставить галочки согласия.
    4. Нажать кнопку "Отправить".
    5. Убедиться, что на странице появился iframe капчи.

    Args:
        page: Экземпляр playwright.sync_api.Page, предоставляемый фикстурой.
    """
    # Инициализация page object для работы со страницей покупки BLL
    buy_page = BuyPage(page)
    buy_page.navigate()
    
    # Заполнение формы тестовыми данными
    # Быстрая скорость ввода автотеста является триггером для системы защиты
    buy_page.fill_form(
        fio="Тестов Тест Тестович",
        phone="+375291112233",
        company="Тест-Автоматизация",
        position="SDET Architect",
        email="test.automation@example.com",
    )

    # Проставление обязательных чекбоксов согласия
    buy_page.agree_to_terms()

    # Отправка формы
    buy_page.submit_form()

    # Главная проверка: ожидаем появления iframe капчи
    # Это подтверждает корректную работу системы защиты от ботов
    buy_page.wait_for_captcha_to_appear(timeout=15000)

    print("\nТест успешно завершен: iframe Yandex SmartCaptcha был обнаружен после отправки формы.")


def test_captcha_trigger_random_loop(page: Page):
    """
    Многократное заполнение формы случайными данными с остановкой, если форма становится недоступна (капча заблокировала).
    После каждой попытки выводится результат (обнаружен ли iframe капчи и доступна ли форма).
    """
    buy_page = BuyPage(page)
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
