"""
Модуль содержит Page Object для страницы заказа демодоступа на сайте https://bii.by.
"""
from playwright.sync_api import Page, Locator, expect

class BiiPage:
    """
    Представляет страницу заказа демодоступа на сайте bii.by и инкапсулирует взаимодействие с ее элементами.
    
    Этот класс создан по аналогии с BuyPage для bll.by, но адаптирован под структуру сайта bii.by.
    Основная цель - тестирование срабатывания капчи при быстром заполнении формы заказа демодоступа.
    """

    def __init__(self, page: Page):
        """
        Инициализирует экземпляр страницы bii.by.

        Args:
            page: Экземпляр playwright.sync_api.Page для взаимодействия с браузером.
        """
        self.page = page
        # Начинаем с главной страницы, затем найдем правильную форму демодоступа
        self.url = "https://bii.by"

        # --- Локаторы будут определены после изучения структуры формы ---
        # Поля формы заказа демодоступа (предположительные селекторы)
        self.name_input: Locator = page.locator("input[name*='name'], input[id*='name'], input[placeholder*='имя']")
        self.email_input: Locator = page.locator("input[name*='email'], input[type='email'], input[placeholder*='email']")
        self.phone_input: Locator = page.locator("input[name*='phone'], input[type='tel'], input[placeholder*='телефон']")
        self.company_input: Locator = page.locator("input[name*='company'], input[name*='organization'], input[placeholder*='компания']")
        
        # Чекбоксы согласия
        self.agreement_checkbox: Locator = page.locator("input[type='checkbox']")
        
        # Кнопка отправки формы
        self.submit_button: Locator = page.locator("button[type='submit'], input[type='submit'], .btn-submit, [class*='submit']")
        
        # Ссылка или кнопка для перехода к форме демодоступа
        self.demo_access_link: Locator = page.locator("a:has-text('демодоступ'), button:has-text('демодоступ'), [href*='demo'], [data-target*='demo']")
        
        # --- Локатор для капчи (универсальные селекторы) ---
        # Ищем различные варианты iframe капчи (Yandex, Google, reCaptcha)
        self.captcha_iframe: Locator = page.locator('iframe[src*="captcha"], iframe[data-testid*="captcha"], iframe[title*="captcha"], iframe[src*="recaptcha"]')

    def navigate(self) -> None:
        """
        Переходит на главную страницу bii.by с retry-логикой и ищет форму демодоступа.
        
        Использует несколько стратегий загрузки для максимальной надёжности:
        1. Сначала пробует networkidle (ждёт сетевого покоя)
        2. Затем domcontentloaded (ждёт готовности DOM) 
        3. В крайнем случае commit (минимальное ожидание)
        """
        print("  [DEBUG] Переходим на главную страницу bii.by")
        
        # Пробуем 3 раза с разными стратегиями загрузки
        for attempt in range(1, 4):
            try:
                print(f"  [DEBUG] Попытка {attempt} загрузки страницы bii.by...")
                if attempt == 1:
                    # Первая попытка с networkidle (ждём сетевого покоя)
                    self.page.goto(self.url, wait_until='networkidle', timeout=45000)
                elif attempt == 2:
                    # Вторая попытка с domcontentloaded
                    self.page.goto(self.url, wait_until='domcontentloaded', timeout=45000)
                else:
                    # Третья попытка с минимальным ожиданием
                    self.page.goto(self.url, wait_until='commit', timeout=45000)
                    
                print(f"  [DEBUG] Страница загружена: {self.page.url}")
                
                # Ждём, пока страница полностью инициализируется
                self.page.wait_for_timeout(2000)
                print("  [DEBUG] Страница bii.by успешно загружена")
                return
                
            except Exception as e:
                print(f"  [DEBUG] Попытка {attempt} не удалась: {type(e).__name__}: {e}")
                if attempt == 3:
                    raise e
                # Небольшая пауза перед следующей попыткой
                self.page.wait_for_timeout(2000)

    def find_and_open_demo_form(self) -> None:
        """
        Ищет и открывает форму заказа демодоступа на сайте bii.by.
        
        Проверяет различные способы доступа к форме:
        - Ссылки с текстом "демодоступ"
        - Кнопки в хедере или футере
        - Модальные окна
        - Прямые ссылки на страницы с формами
        """
        print("  [DEBUG] Ищем способ открыть форму демодоступа...")
        
        try:
            # Ищем ссылку или кнопку демодоступа
            demo_link_visible = self.demo_access_link.first.is_visible(timeout=5000)
            if demo_link_visible:
                print("  [DEBUG] Найдена ссылка на демодоступ, кликаем...")
                self.demo_access_link.first.click()
                # Ждём появления формы
                self.page.wait_for_timeout(2000)
                return
        except Exception as e:
            print(f"  [DEBUG] Не удалось найти ссылку демодоступа: {e}")
        
        # Пробуем найти форму прямо на странице
        try:
            # Проверяем, есть ли уже форма на текущей странице
            form_exists = self.page.locator("form").first.is_visible(timeout=3000)
            if form_exists:
                print("  [DEBUG] Форма уже присутствует на странице")
                return
        except Exception:
            pass
            
        print("  [WARNING] Форма демодоступа не найдена, будем работать с текущей страницей")

    def fill_form(
        self,
        name: str,
        email: str,
        phone: str = "",
        company: str = "",
    ) -> None:
        """
        Заполняет доступные поля формы демодоступа.
        
        Адаптивно находит поля формы и заполняет только те, которые присутствуют на странице.
        Это позволяет работать с разными вариантами форм на bii.by.

        Args:
            name: Имя пользователя
            email: Адрес электронной почты (обязательное поле)
            phone: Номер телефона (опционально)
            company: Название компании (опционально)
        """
        print("  [DEBUG] Начинаем заполнение формы...")
        
        # Заполняем имя, если поле присутствует
        try:
            if self.name_input.first.is_visible(timeout=3000):
                print("  [DEBUG] Заполняем поле 'Имя'")
                self.name_input.first.fill(name)
        except Exception as e:
            print(f"  [DEBUG] Поле имени недоступно: {e}")
        
        # Заполняем email (основное поле)
        try:
            if self.email_input.first.is_visible(timeout=3000):
                print("  [DEBUG] Заполняем поле 'Email'")
                self.email_input.first.fill(email)
            else:
                print("  [WARNING] Поле email не найдено!")
        except Exception as e:
            print(f"  [DEBUG] Ошибка заполнения email: {e}")
        
        # Заполняем телефон, если указан и поле доступно
        if phone:
            try:
                if self.phone_input.first.is_visible(timeout=3000):
                    print("  [DEBUG] Заполняем поле 'Телефон'")
                    self.phone_input.first.fill(phone)
            except Exception as e:
                print(f"  [DEBUG] Поле телефона недоступно: {e}")
        
        # Заполняем компанию, если указана и поле доступно
        if company:
            try:
                if self.company_input.first.is_visible(timeout=3000):
                    print("  [DEBUG] Заполняем поле 'Компания'")
                    self.company_input.first.fill(company)
            except Exception as e:
                print(f"  [DEBUG] Поле компании недоступно: {e}")

    def agree_to_terms(self) -> None:
        """
        Отмечает чекбоксы согласия с условиями использования и политикой конфиденциальности.
        
        Ищет все доступные чекбоксы и отмечает их для согласия с правилами сайта.
        """
        try:
            checkboxes = self.agreement_checkbox.all()
            if checkboxes:
                for i, checkbox in enumerate(checkboxes):
                    if checkbox.is_visible():
                        print(f"  [DEBUG] Отмечаем чекбокс согласия #{i+1}")
                        checkbox.check()
            else:
                print("  [DEBUG] Чекбоксы согласия не найдены")
        except Exception as e:
            print(f"  [DEBUG] Ошибка при работе с чекбоксами: {e}")

    def submit_form(self) -> None:
        """
        Нажимает кнопку отправки формы.
        
        Ищет различные варианты кнопок отправки и кликает по первой найденной.
        """
        print("  [DEBUG] Ищем кнопку отправки формы...")
        
        try:
            if self.submit_button.first.is_visible(timeout=5000):
                print("  [DEBUG] Найдена кнопка отправки, кликаем...")
                self.submit_button.first.click()
                print("  [DEBUG] Форма отправлена")
            else:
                print("  [WARNING] Кнопка отправки не найдена!")
        except Exception as e:
            print(f"  [ERROR] Ошибка при отправке формы: {e}")
            raise e

    def wait_for_captcha_to_appear(self, timeout: int = 10000) -> None:
        """
        Ожидает появления iframe капчи на странице.
        
        Проверяет различные варианты капчи (Yandex SmartCaptcha, Google reCaptcha и др.)

        Args:
            timeout: Максимальное время ожидания в миллисекундах.

        Raises:
            TimeoutError: Если iframe капчи не появился за указанное время.
        """
        print("  [DEBUG] Ждём появления капчи...")
        expect(self.captcha_iframe.first).to_be_visible(timeout=timeout)
        print("  [SUCCESS] Капча обнаружена на странице!")

    def check_success_redirect(self) -> bool:
        """
        Проверяет, произошёл ли редирект на страницу благодарности после отправки формы.
        
        Returns:
            bool: True если произошёл редирект на страницу успеха, False если остались на форме
        """
        current_url = self.page.url
        # Проверяем различные варианты страниц успеха
        success_indicators = ['thanks', 'success', 'спасибо', 'успех', 'thank']
        
        for indicator in success_indicators:
            if indicator in current_url.lower():
                return True
                
        return False
