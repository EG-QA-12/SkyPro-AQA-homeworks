"""
Модуль содержит Page Object для страницы покупки https://bii.by/buy.
"""
from playwright.sync_api import Page, Locator, expect

class BiiBuyPage:
    """
    Представляет страницу покупки на bii.by и инкапсулирует взаимодействие с ее элементами.
    """

    def __init__(self, page: Page):
        """
        Инициализирует экземпляр страницы.

        Args:
            page: Экземпляр playwright.sync_api.Page.
        """
        self.page = page
        self.url = "https://bii.by/buy#buy-form"

        # --- Локаторы элементов формы ---
        self.fio_input: Locator = page.locator("#request_fio")
        self.phone_input: Locator = page.locator("#request_phone")
        self.company_input: Locator = page.locator("#request_company")
        self.position_input: Locator = page.locator("#request_position")
        self.email_input: Locator = page.locator("#request_mail")
        self.promo_input: Locator = page.locator("#request_promo")
        self.agree_checkbox: Locator = page.locator("#request_agree")
        self.agree_policy_checkbox: Locator = page.locator("#request_agree_pol")
        self.submit_button: Locator = page.locator("#request-send")

        # --- Локатор для капчи ---
        self.captcha_iframe: Locator = page.locator('iframe[data-testid="advanced-iframe"]')

    def navigate(self) -> None:
        """
        Переходит на URL страницы с улучшенной retry-логикой и проверкой готовности формы.
        Ожидает готовности всех ключевых элементов перед завершением.
        """
        print("  [DEBUG] Переходим на страницу покупки BII")
        
        # Пробуем разные стратегии загрузки с увеличенными таймаутами
        strategies = [
            ('load', 60000),
            ('domcontentloaded', 45000), 
            ('commit', 30000)
        ]
        
        page_loaded = False
        for attempt, (wait_until, timeout) in enumerate(strategies, 1):
            try:
                print(f"  [DEBUG] Попытка {attempt}: {wait_until}, timeout={timeout}ms")
                self.page.goto(self.url, wait_until=wait_until, timeout=timeout)
                page_loaded = True
                print(f"  [DEBUG] Страница загружена: {self.page.url}")
                break
            except Exception as e:
                print(f"  [DEBUG] Попытка {attempt} не удалась: {type(e).__name__}: {e}")
                if attempt == len(strategies):
                    raise e
                continue
        
        if not page_loaded:
            raise Exception("Не удалось загрузить страницу ни с одной стратегией")
        
        # Ждём готовности всех ключевых элементов формы
        print("  [DEBUG] Проверяем готовность элементов формы...")
        key_selectors = ['#request_fio', '#request_phone', '#request_company', '#request-send']
        
        for selector in key_selectors:
            try:
                self.page.wait_for_selector(selector, state='visible', timeout=10000)
                print(f"  [DEBUG] Элемент готов: {selector}")
            except Exception as e:
                print(f"  [WARNING] Элемент {selector} не готов: {e}")
        
        # Дополнительное время для полной инициализации JavaScript
        print("  [DEBUG] Даём время для инициализации JS...")
        self.page.wait_for_timeout(3000)
        print("  [DEBUG] Форма готова к заполнению!")

    def fill_form(
        self,
        fio: str,
        phone: str,
        company: str,
        position: str,
        email: str,
        promo: str = "",
    ) -> None:
        """
        Заполняет поля формы предоставленными данными с имитацией человеческого поведения.
        Добавляет небольшие паузы между вводом для обхода антибот-защиты.
        """
        print("  [DEBUG] Начинаем заполнение формы...")
        
        # ФИО
        print(f"  [DEBUG] Заполняем ФИО: {fio}")
        self.fio_input.wait_for(state='visible', timeout=5000)
        self.fio_input.click()  # Фокус на поле
        self.page.wait_for_timeout(200)  # Небольшая пауза
        self.fio_input.fill(fio)
        self.page.wait_for_timeout(300)
        
        # Телефон
        print(f"  [DEBUG] Заполняем телефон: {phone}")
        self.phone_input.wait_for(state='visible', timeout=5000)
        self.phone_input.click()
        self.page.wait_for_timeout(200)
        self.phone_input.fill(phone)
        self.page.wait_for_timeout(300)
        
        # Компания
        print(f"  [DEBUG] Заполняем компанию: {company}")
        self.company_input.wait_for(state='visible', timeout=5000)
        self.company_input.click()
        self.page.wait_for_timeout(200)
        self.company_input.fill(company)
        self.page.wait_for_timeout(300)
        
        # Должность
        print(f"  [DEBUG] Заполняем должность: {position}")
        self.position_input.wait_for(state='visible', timeout=5000)
        self.position_input.click()
        self.page.wait_for_timeout(200)
        self.position_input.fill(position)
        self.page.wait_for_timeout(300)
        
        # Email
        print(f"  [DEBUG] Заполняем email: {email}")
        self.email_input.wait_for(state='visible', timeout=5000)
        self.email_input.click()
        self.page.wait_for_timeout(200)
        self.email_input.fill(email)
        self.page.wait_for_timeout(300)
        
        # Промокод (если указан)
        if promo:
            print(f"  [DEBUG] Заполняем промокод: {promo}")
            self.promo_input.wait_for(state='visible', timeout=5000)
            self.promo_input.click()
            self.page.wait_for_timeout(200)
            self.promo_input.fill(promo)
            self.page.wait_for_timeout(300)
        
        print("  [DEBUG] Заполнение формы завершено")

    def agree_to_terms(self) -> None:
        """
        Активирует чек-боксы согласия с условиями с проверкой их готовности.
        Добавляет небольшие паузы для имитации человеческого поведения.
        """
        print("  [DEBUG] Проставляем галочки согласия...")
        
        # Согласие с условиями
        print("  [DEBUG] Чекбокс 'Согласие с условиями'")
        self.agree_checkbox.wait_for(state='visible', timeout=5000)
        self.page.wait_for_timeout(200)
        self.agree_checkbox.check()
        self.page.wait_for_timeout(400)
        
        # Согласие с политикой
        print("  [DEBUG] Чекбокс 'Согласие с политикой'")
        self.agree_policy_checkbox.wait_for(state='visible', timeout=5000)
        self.page.wait_for_timeout(200)
        self.agree_policy_checkbox.check()
        self.page.wait_for_timeout(400)
        
        print("  [DEBUG] Согласие с условиями завершено")

    def submit_form(self) -> None:
        """
        Нажимает на кнопку отправки формы с проверкой её готовности.
        Добавляет небольшую паузу для имитации человеческого поведения.
        """
        print("  [DEBUG] Подготовка к отправке формы...")
        
        # Проверяем, что кнопка видима и готова для клика
        self.submit_button.wait_for(state='visible', timeout=5000)
        # Дополнительная проверка, что кнопка активна
        if not self.submit_button.is_enabled():
            print("  [WARNING] Кнопка 'Отправить' недоступна для клика")
        print("  [DEBUG] Кнопка 'Отправить' готова к нажатию")
        
        # Небольшая пауза перед отправкой
        self.page.wait_for_timeout(500)
        
        print("  [DEBUG] Нажимаем кнопку 'Отправить'...")
        self.submit_button.click()
        print("  [DEBUG] Форма отправлена!")
        
        # Даём время на обработку формы
        self.page.wait_for_timeout(1000)

    def wait_for_captcha_to_appear(self, timeout: int = 10000) -> None:
        """
        Ожидает появления iframe Yandex SmartCaptcha на странице.

        Args:
            timeout: Максимальное время ожидания в миллисекундах.

        Raises:
            TimeoutError: Если iframe капчи не появился за указанное время.
        """
        expect(self.captcha_iframe).to_be_visible(timeout=timeout)
        print("  [DEBUG] iframe капчи стал видимым")
