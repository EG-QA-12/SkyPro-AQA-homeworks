"""
Тесты для проверки функциональности капчи на сайте BLL.
"""
import pytest
from playwright.sync_api import Page
import random
import string
from framework.utils.url_utils import add_allow_session_param, is_headless

def random_string(length=8):
    """Генерирует случайную строку из букв заданной длины."""
    return ''.join(random.choices(string.ascii_letters, k=length))

def random_phone():
    """Генерирует случайный белорусский номер телефона."""
    return "+37529" + ''.join(random.choices(string.digits, k=7))

def random_email():
    """Генерирует случайный email-адрес."""
    return random_string(5) + "@example.com"


def test_captcha_fill_without_anchor(page: Page):
    """
    Проверяет срабатывание капчи при быстром заполнении формы на https://bll.by/buy.
    
    Тест имитирует поведение бота, который пытается быстро заполнить и отправить
    форму заявки без естественных пауз. Ожидается, что система защиты (капча)
    распознает такое поведение как подозрительное и активирует защиту.
    
    Сценарий:
    1. Переход на страницу формы с параметром allow_session
    2. Клик по кнопке 'Заказать демодоступ' для отображения формы
    3. Быстрое заполнение всех полей формы с минимальными задержками
    4. Отправка формы
    5. Проверка результата: ожидается, что капча сработает и редиректа на /thanks не произойдет
    
    Тест использует фикстуру page из Playwright, которая предоставляет
    экземпляр страницы браузера для взаимодействия с веб-интерфейсом.
    
    Args:
        page: Экземпляр Page из Playwright для управления браузером
        
    Returns:
        None: Тест использует assert для проверки условий
        
    Raises:
        AssertionError: если заявка прошла успешно без срабатывания капчи
    """
    url = add_allow_session_param("https://bll.by/buy", is_headless())
    page.goto(url, timeout=60000, wait_until="commit")
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.wait_for_timeout(1500)
    button = page.locator('button.land-btn-main[data-scroll="buy-form"]').first
    button.scroll_into_view_if_needed()
    button.click()
    page.wait_for_selector('input[name="fio"]', timeout=10000)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # Диагностика: вывести все input name
    inputs = page.locator('input')
    input_count = inputs.count()
    print(f"[DIAG] На форме найдено {input_count} input-полей:")
    for i in range(input_count):
        name = inputs.nth(i).get_attribute('name')
        print(f"[DIAG] input[{i}] name=", name)

    fields = [
        ('input[name="fio"]', "Тестов Тест Тестович"),
        ('input[name="phone"]', "+375291112233"),
        ('input[name="organisation"]', "Тест-Автоматизация"),
        ('input[name="position"]', "SDET Architect"),
        ('input[name="email"]', "test.automation@example.com"),
        ('input[name="promo"]', "PROMO2024"),  # если не требуется, можно закомментировать
    ]
    for selector, value in fields:
        try:
            page.wait_for_selector(selector, timeout=10000)
            field = page.locator(selector)
            field.scroll_into_view_if_needed()
            field.fill(value)
            print(f"[DIAG] Заполнено поле {selector} значением '{value}'")
            page.wait_for_timeout(200)
        except Exception as e:
            print(f"[DIAG] Не удалось найти или заполнить поле {selector}: {e}")
    page.check('input[name="request_agree"]')
    page.check('input[name="request_agree_pol"]')
    submit_btn = page.locator('#request-send')
    print("[DIAG] Кнопка submit видима:", submit_btn.is_visible())
    print("[DIAG] Кнопка submit активна:", submit_btn.is_enabled())
    submit_btn.click()
    # Проверяем редирект на /thanks (2 секунды)
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    try:
        page.wait_for_url("**/thanks", timeout=2000)
        redirected = True
    except PlaywrightTimeoutError:
        redirected = False
    current_url = page.url
    print(f"  [DEBUG] Текущий URL: {current_url}")
    if redirected or "thanks" in current_url:
        print("  [Результат] ПРОВАЛ: заявка прошла без капчи, редирект на /thanks")
        assert False, "Заявка прошла без капчи — тест не пройден!"
    else:
        print("  [Результат] КАПЧА ИЛИ ДРУГАЯ ЗАЩИТА СРАБОТАЛА: остались на странице формы (тест пройден)")
        assert True


def test_captcha_random_loop_bll_humanlike(page: Page):
    """
    Многократная проверка срабатывания капчи на https://bll.by/buy с имитацией человеческого поведения.
    
    Тест выполняет 20 попыток отправки формы с случайными данными, имитируя
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
    
    Args:
        page: Экземпляр Page из Playwright для управления браузером
        
    Returns:
        None: Тест не возвращает значений, результаты выводятся в консоль
        
    Note:
        Тест использует модуль random для генерации случайных данных и
        Playwright для управления браузером и взаимодействия с веб-страницей.
    """
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    success_count = 0
    total_attempts = 20
    for attempt in range(1, total_attempts + 1):
        print(f"\n=== Попытка {attempt} ===")
        url = add_allow_session_param("https://bll.by/buy", is_headless())
        page.goto(url, timeout=60000, wait_until="commit")
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.wait_for_timeout(1500)
        button = page.locator('button.land-btn-main[data-scroll="buy-form"]').first
        button.scroll_into_view_if_needed()
        button.click()
        page.wait_for_selector('input[name="fio"]', timeout=10000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        fields = [
            ('input[name="fio"]', random_string(12)),
            ('input[name="phone"]', random_phone()),
            ('input[name="organisation"]', random_string(10)),
            ('input[name="position"]', random_string(6)),
            ('input[name="email"]', random_email()),
            ('input[name="promo"]', random_string(5)),
        ]
        for selector, value in fields:
            try:
                page.wait_for_selector(selector, timeout=10000)
                field = page.locator(selector)
                field.scroll_into_view_if_needed()
                field.click()
                field.fill(value)
                print(f"[DIAG] Заполнено поле {selector} значением '{value}'")
                page.wait_for_timeout(100)
            except Exception as e:
                print(f"[DIAG] Не удалось найти или заполнить поле {selector}: {e}")
        page.check('input[name="request_agree"]')
        page.check('input[name="request_agree_pol"]')
        submit_btn = page.locator('#request-send')
        print("[DIAG] Кнопка submit видима:", submit_btn.is_visible())
        print("[DIAG] Кнопка submit активна:", submit_btn.is_enabled())
        try:
            submit_btn.click()
        except Exception as e:
            print(f"[DIAG] Не удалось кликнуть по кнопке submit: {e}")
            continue
        # Проверяем редирект на /thanks (2 секунды)
        try:
            page.wait_for_url("**/thanks", timeout=2000)
            redirected = True
        except PlaywrightTimeoutError:
            redirected = False
        current_url = page.url
        print(f"  [DEBUG] Текущий URL: {current_url}")
        if redirected or "thanks" in current_url:
            print("  [Результат] ПРОВАЛ: заявка прошла без капчи, редирект на /thanks")
            success_count += 1
        else:
            print("  [Результат] КАПЧА ИЛИ ДРУГАЯ ЗАЩИТА СРАБОТАЛА: остались на странице формы (тест пройден)")
    print(f"\nИТОГ: Успешных отправок (редирект на /thanks): {success_count} из {total_attempts} попыток.")
