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
    Проверяет срабатывание Yandex SmartCaptcha при быстром заполнении формы на https://bii.by/buy.
    
    Тест имитирует поведение бота, который пытается быстро заполнить и отправить
    форму заявки без естественных пауз. Ожидается, что система защиты (Yandex SmartCaptcha)
    распознает такое поведение как подозрительное и активирует защиту.
    
    Сценарий:
    1. Переход на страницу формы с параметром allow_session
    2. Быстрое заполнение всех обязательных полей формы
    3. Проставление галочек согласия
    4. Отправка формы
    5. Проверка появления iframe капчи на странице
    
    Тест использует Page Object Model через класс BiiBuyPage для управления
    элементами страницы, что обеспечивает гибкость и поддерживаемость кода.
    
    Args:
        page: Экземпляр Page из Playwright для управления браузером
        
    Returns:
        None: Тест использует assert внутри метода wait_for_captcha_to_appear
        
    Raises:
        AssertionError: если iframe капчи не появился в течение заданного таймаута
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
    Многократная проверка срабатывания капчи на https://bii.by/buy с имитацией человеческого поведения.
    
    Тест выполняет 100 попыток отправки формы с случайными данными, имитируя
    естественное поведение пользователя с разумными задержками между действиями.
    Цель теста - оценить эффективность системы защиты при различных сценариях
    заполнения формы.
    
    Для каждой попытки:
    1. Генерируются случайные данные для полей формы
    2. Поля заполняются с небольшими задержками
    3. Отправляется форма
    4. Фиксируется результат: сработала ли капча или заявка прошла успешно
    
    В конце теста выводится статистика по успешным отправкам (без капчи)
    и неудачным (с капчей). Это позволяет оценить баланс между защитой от ботов
    и удобством для реальных пользователей.
    
    Тест использует Page Object Model через класс BiiBuyPage для управления
    элементами страницы, что обеспечивает гибкость и поддерживаемость кода.
    
    Args:
        page: Экземпляр Page из Playwright для управления браузером
        
    Returns:
        None: Тест не возвращает значений, результаты выводятся в консоль
        
    Note:
        Тест использует модуль random для генерации случайных данных и
        Playwright для управления браузером и взаимодействия с веб-страницей.
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
