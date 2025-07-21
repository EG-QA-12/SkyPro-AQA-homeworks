"""
Модуль содержит Page Object для страницы покупки https://bll.by/buy.
"""
from playwright.sync_api import Page, Locator, expect

class BuyPage:
    """
    Представляет страницу покупки и инкапсулирует взаимодействие с ее элементами.
    """

    def __init__(self, page: Page):
        """
        Инициализирует экземпляр страницы.

        Args:
            page: Экземпляр playwright.sync_api.Page.
        """
        self.page = page
        self.url = "https://bll.by/buy#buy-form"

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

        # --- Локаторы для управления формой ---
        # Кнопка для открытия формы заказа демодоступа
        self.demo_order_button: Locator = page.locator('button[data-scroll="buy-form"]')
        
        # --- Локатор для капчи (уникальный iframe для виджета) ---
        self.captcha_iframe: Locator = page.locator('iframe[data-testid="advanced-iframe"]')

    def navigate(self) -> None:
        """
        Переходит на URL страницы с retry-логикой и увеличенным таймаутом.
        Использует networkidle для более надёжной загрузки страницы.
        """
        print("  [DEBUG] Переходим на страницу покупки")
        
        # Пробуем 3 раза с разными стратегиями загрузки
        for attempt in range(1, 4):
            try:
                print(f"  [DEBUG] Попытка {attempt} загрузки страницы...")
                if attempt == 1:
                    # Первая попытка с networkidle (ждём сетевого покоя)
                    self.page.goto(self.url, wait_until='networkidle', timeout=60000)
                elif attempt == 2:
                    # Вторая попытка с domcontentloaded
                    self.page.goto(self.url, wait_until='domcontentloaded', timeout=60000)
                else:
                    # Третья попытка без ожидания
                    self.page.goto(self.url, wait_until='commit', timeout=60000)
                    
                print(f"  [DEBUG] Страница загружена: {self.page.url}")
                
                # Дополнительная проверка - ждём, пока форма станет доступной
                self.page.wait_for_selector('#request_fio', timeout=10000)
                print("  [DEBUG] Форма стала доступной для заполнения")
                return
                
            except Exception as e:
                print(f"  [DEBUG] Попытка {attempt} не удалась: {type(e).__name__}: {e}")
                if attempt == 3:
                    raise e
                # Небольшая пауза перед следующей попыткой
                self.page.wait_for_timeout(2000)

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
        Заполняет поля формы предоставленными данными.

        Args:
            fio: Полное имя.
            phone: Номер телефона.
            company: Название организации.
            position: Должность.
            email: Адрес электронной почты.
            promo: Промокод (опционально).
        """
        self.fio_input.fill(fio)
        self.phone_input.fill(phone)
        self.company_input.fill(company)
        self.position_input.fill(position)
        self.email_input.fill(email)
        if promo:
            self.promo_input.fill(promo)

    def agree_to_terms(self) -> None:
        """
        Активирует чек-боксы согласия с условиями.
        """
        self.agree_checkbox.check()
        self.agree_policy_checkbox.check()

    def submit_form(self) -> None:
        """
        Нажимает на кнопку отправки формы.
        """
        print("  [DEBUG] Перед кликом по кнопке 'Отправить'")
        self.submit_button.click()
        print("  [DEBUG] После клика по кнопке 'Отправить'")

    def wait_for_captcha_to_appear(self, timeout: int = 10000) -> None:
        """
        Ожидает появления iframe Yandex SmartCaptcha на странице.

        Args:
            timeout: Максимальное время ожидания в миллисекундах.

        Raises:
            TimeoutError: Если iframe капчи не появился за указанное время.
        """
        expect(self.captcha_iframe).to_be_visible(timeout=timeout)
        print("  [DEBUG] Форма стала видимой и готова к заполнению")
