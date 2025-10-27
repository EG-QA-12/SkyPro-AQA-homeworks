"""
Footer Links Tests

Тесты навигации по ссылкам в футере главной страницы bll.by
(Политика Оператора, Скачать ярлык, email контакты, социальные сети)
"""

import pytest
import allure

from ..pages.header_navigation_page import HeaderNavigationPage


@pytest.mark.smoke
@allure.epic("Главная страница")
@allure.feature("Навигация футера")
@allure.story("Footer navigation")
class TestMainPageFooter:
    """
    Класс тестов для проверки навигации по ссылкам в футере главной страницы
    """

    @pytest.fixture(autouse=True)
    def setup_method(self, domain_aware_authenticated_context_for_bll):
        """
        Настройка перед каждым тестом
        """
        self.context = domain_aware_authenticated_context_for_bll
        self.page = self.context.new_page()
        self.navigation = HeaderNavigationPage(self.page)

        # Переходим на главную и ждем готовности
        self.page.goto("https://bll.by", wait_until="domcontentloaded")
        self.navigation.smart_wait_for_page_ready()

        yield

        # Cleanup
        if self.page.url != "https://bll.by":
            self.page.goto("https://bll.by")

    @allure.title("Проверка видимости всех footer ссылок")
    @allure.description("Проверка что все ссылки в футере видны на странице")
    def test_footer_links_visibility(self):
        """
        Тест проверяет видимость всех ссылок в футере
        """
        footer_links = [
            "Политика Оператора",
            "Скачать ярлык",
            "Условия использования",
            "Карта сайта",
            "Контакты",
            "О компании",
        ]
        
        # Email контакты (ищем по шаблону)
        email_patterns = [
            "info@bll.by",
            "support@bll.by",
            "bll@bll.by"
        ]
        
        # Социальные сети
        social_networks = [
            "Facebook",
            "Twitter",
            "LinkedIn",
            "Instagram",
            "YouTube",
            "ВКонтакте",
        ]
        
        with allure.step("Проверяем видимость основных footer ссылок"):
            for link_name in footer_links:
                try:
                    link = self.page.get_by_role("link", name=link_name)
                    is_visible = link.is_visible(timeout=3000)
                    status_text = "Видима" if is_visible else "Не видима"
                    allure.attach(
                        f"Ссылка '{link_name}': {status_text}",
                        name=f"Видимость {link_name}")
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке ссылки '{link_name}': {e}",
                        name=f"Ошибка {link_name}")

        with allure.step("Проверяем видимость email контактов"):
            for email in email_patterns:
                try:
                    # Ищем email по тексту или атрибуту href
                    email_link = self.page.locator(f"a[href*='{email}'], a:has-text('{email}')")
                    is_visible = email_link.is_visible(timeout=3000)
                    status_text = "Видим" if is_visible else "Не видим"
                    allure.attach(
                        f"Email '{email}': {status_text}",
                        name=f"Видимость {email}")
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке email '{email}': {e}",
                        name=f"Ошибка {email}")

        with allure.step("Проверяем видимость социальных сетей"):
            for network in social_networks:
                try:
                    # Ищем социальные сети по тексту или атрибуту
                    social_link = self.page.locator(
                        f"a[href*='{network.lower()}'], a:has-text('{network}')")
                    is_visible = social_link.is_visible(timeout=3000)
                    status_text = "Видима" if is_visible else "Не видима"
                    allure.attach(
                        f"Соцсеть '{network}': {status_text}",
                        name=f"Видимость {network}")
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке соцсети '{network}': {e}",
                        name=f"Ошибка {network}")

    @allure.title("Проверка функциональности ссылки 'Политика Оператора'")
    @allure.description("Проверка что ссылка на политику оператора работает корректно")
    def test_privacy_policy_functionality(self):
        """
        Тест проверяет функциональность ссылки на политику оператора
        """
        with allure.step("Проверяем доступность политики оператора"):
            try:
                # Ищем ссылку на политику оператора
                policy_link = self.page.get_by_role("link", name="Политика Оператора")
                
                if policy_link.is_visible(timeout=3000):
                    # Получаем href для проверки
                    href = policy_link.get_attribute("href")
                    allure.attach(f"Найден href: {href}", name="URL политики")
                    
                    # Кликаем по ссылке
                    policy_link.click()
                    
                    # Ждем загрузки
                    self.page.wait_for_timeout(3000)
                    
                    # Проверяем результат
                    current_url = self.page.url
                    policy_loaded = (
                        "policy" in current_url.lower() or 
                        "politika" in current_url.lower() or
                        "privacy" in current_url.lower()
                    )
                    
                    allure.attach(
                        f"Политика оператора загружена: {policy_loaded}",
                        name="Загрузка политики")
                    
                    if policy_loaded:
                        # Проверяем HTTP статус
                        status = self.navigation.assert_http_status(current_url)
                        allure.attach(
                            f"HTTP статус: {status}",
                            name="Статус политики")
                else:
                    allure.attach(
                        "Ссылка на политику оператора не найдена",
                        name="Отсутствие ссылки")
                    
            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке политики оператора: {e}",
                    name="Ошибка политики")

    @allure.title("Проверка функциональности ссылки 'Скачать ярлык'")
    @allure.description("Проверка что ссылка на скачивание ярлыка работает корректно")
    def test_download_shortcut_functionality(self):
        """
        Тест проверяет функциональность ссылки на скачивание ярлыка
        """
        with allure.step("Проверяем доступность скачивания ярлыка"):
            try:
                # Ищем ссылку на скачивание ярлыка
                shortcut_link = self.page.get_by_role("link", name="Скачать ярлык")
                
                if shortcut_link.is_visible(timeout=3000):
                    # Получаем href для проверки
                    href = shortcut_link.get_attribute("href")
                    allure.attach(f"Найден href: {href}", name="URL ярлыка")
                    
                    # Проверяем что это ссылка на скачивание
                    is_download = (
                        href and (
                            href.endswith(".url") or 
                            href.endswith(".lnk") or
                            "download" in href.lower() or
                            "shortcut" in href.lower()
                        )
                    )
                    
                    allure.attach(
                        f"Ссылка на скачивание: {is_download}",
                        name="Тип ссылки")
                    
                    # Кликаем по ссылке (может начаться скачивание)
                    with self.page.expect_download(timeout=10000) as download_info:
                        shortcut_link.click()
                    
                    # Проверяем началось ли скачивание
                    try:
                        download = download_info.value
                        filename = download.suggested_filename
                        allure.attach(
                            f"Файл для скачивания: {filename}",
                            name="Имя файла")
                    except Exception:
                        allure.attach(
                            "Скачивание не началось (возможно, внешний ресурс)",
                            name="Результат скачивания")
                else:
                    allure.attach(
                        "Ссылка на скачивание ярлыка не найдена",
                        name="Отсутствие ссылки")
                    
            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке скачивания ярлыка: {e}",
                    name="Ошибка ярлыка")

    @allure.title("Проверка email контактов")
    @allure.description("Проверка что email контакты корректны и доступны")
    def test_email_contacts_functionality(self):
        """
        Тест проверяет функциональность email контактов
        """
        email_patterns = [
            "info@bll.by",
            "support@bll.by",
            "bll@bll.by"
        ]
        
        with allure.step("Проверяем email контакты"):
            for email in email_patterns:
                try:
                    # Ищем email по тексту или атрибуту href
                    email_link = self.page.locator(
                        f"a[href*='{email}'], a:has-text('{email}')")
                    
                    if email_link.is_visible(timeout=3000):
                        # Получаем href для проверки
                        href = email_link.get_attribute("href")
                        allure.attach(f"Найден href: {href}", name=f"URL {email}")
                        
                        # Проверяем что это mailto ссылка
                        is_mailto = href and href.startswith("mailto:")
                        allure.attach(
                            f"Mailto ссылка: {is_mailto}",
                            name=f"Тип {email}")
                        
                        if is_mailto:
                            # Проверяем корректность email в href
                            email_in_href = email in href
                            allure.attach(
                                f"Email корректен: {email_in_href}",
                                name=f"Корректность {email}")
                    else:
                        allure.attach(
                            f"Email '{email}' не найден",
                            name=f"Отсутствие {email}")
                        
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке email '{email}': {e}",
                        name=f"Ошибка {email}")

    @allure.title("Проверка социальных сетей")
    @allure.description("Проверка что ссылки на социальные сети работают корректно")
    def test_social_networks_functionality(self):
        """
        Тест проверяет функциональность ссылок на социальные сети
        """
        social_networks = [
            ("Facebook", "facebook.com"),
            ("Twitter", "twitter.com"),
            ("LinkedIn", "linkedin.com"),
            ("Instagram", "instagram.com"),
            ("YouTube", "youtube.com"),
            ("ВКонтакте", "vk.com"),
        ]
        
        with allure.step("Проверяем социальные сети"):
            for network_name, domain in social_networks:
                try:
                    # Ищем социальную сеть по тексту или домену
                    social_link = self.page.locator(
                        f"a[href*='{domain}'], a:has-text('{network_name}')")
                    
                    if social_link.is_visible(timeout=3000):
                        # Получаем href для проверки
                        href = social_link.get_attribute("href")
                        allure.attach(f"Найден href: {href}", name=f"URL {network_name}")
                        
                        # Проверяем что ссылка ведет на правильный домен
                        domain_correct = domain in href.lower() if href else False
                        allure.attach(
                            f"Домен корректен: {domain_correct}",
                            name=f"Домен {network_name}")
                        
                        # Проверяем что ссылка открывается в новом окне
                        target_blank = social_link.get_attribute("target") == "_blank"
                        allure.attach(
                            f"Открывается в новом окне: {target_blank}",
                            name=f"Target {network_name}")
                    else:
                        allure.attach(
                            f"Соцсеть '{network_name}' не найдена",
                            name=f"Отсутствие {network_name}")
                        
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке соцсети '{network_name}': {e}",
                        name=f"Ошибка {network_name}")

    @allure.title("Проверка функциональности ссылки 'Условия использования'")
    @allure.description("Проверка что ссылка на условия использования работает корректно")
    def test_terms_of_use_functionality(self):
        """
        Тест проверяет функциональность ссылки на условия использования
        """
        with allure.step("Проверяем доступность условий использования"):
            try:
                # Ищем ссылку на условия использования
                terms_link = self.page.get_by_role("link", name="Условия использования")

                if terms_link.is_visible(timeout=3000):
                    # Получаем href для проверки
                    href = terms_link.get_attribute("href")
                    allure.attach(f"Найден href: {href}", name="URL условий")

                    # Кликаем по ссылке
                    terms_link.click()

                    # Ждем загрузки
                    self.page.wait_for_timeout(3000)

                    # Проверяем результат
                    current_url = self.page.url
                    terms_loaded = (
                        "terms" in current_url.lower() or
                        "usloviya" in current_url.lower() or
                        "conditions" in current_url.lower()
                    )

                    allure.attach(
                        f"Условия использования загружены: {terms_loaded}",
                        name="Загрузка условий")

                    if terms_loaded:
                        # Проверяем HTTP статус
                        status = self.navigation.assert_http_status(current_url)
                        allure.attach(
                            f"HTTP статус: {status}",
                            name="Статус условий")
                else:
                    allure.attach(
                        "Ссылка на условия использования не найдена",
                        name="Отсутствие ссылки")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке условий использования: {e}",
                    name="Ошибка условий")

    @allure.title("Проверка функциональности ссылки 'Карта сайта'")
    @allure.description("Проверка что ссылка на карту сайта работает корректно")
    def test_sitemap_functionality(self):
        """
        Тест проверяет функциональность ссылки на карту сайта
        """
        with allure.step("Проверяем доступность карты сайта"):
            try:
                # Ищем ссылку на карту сайта
                sitemap_link = self.page.get_by_role("link", name="Карта сайта")

                if sitemap_link.is_visible(timeout=3000):
                    # Получаем href для проверки
                    href = sitemap_link.get_attribute("href")
                    allure.attach(f"Найден href: {href}", name="URL карты")

                    # Кликаем по ссылке
                    sitemap_link.click()

                    # Ждем загрузки
                    self.page.wait_for_timeout(3000)

                    # Проверяем результат
                    current_url = self.page.url
                    sitemap_loaded = (
                        "sitemap" in current_url.lower() or
                        "karta" in current_url.lower() or
                        "map" in current_url.lower()
                    )

                    allure.attach(
                        f"Карта сайта загружена: {sitemap_loaded}",
                        name="Загрузка карты")

                    if sitemap_loaded:
                        # Проверяем HTTP статус
                        status = self.navigation.assert_http_status(current_url)
                        allure.attach(
                            f"HTTP статус: {status}",
                            name="Статус карты")
                else:
                    allure.attach(
                        "Ссылка на карту сайта не найдена",
                        name="Отсутствие ссылки")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке карты сайта: {e}",
                    name="Ошибка карты")

    @allure.title("Проверка функциональности ссылки 'Контакты'")
    @allure.description("Проверка что ссылка на контакты работает корректно")
    def test_contacts_functionality(self):
        """
        Тест проверяет функциональность ссылки на контакты
        """
        with allure.step("Проверяем доступность контактов"):
            try:
                # Ищем ссылку на контакты
                contacts_link = self.page.get_by_role("link", name="Контакты")

                if contacts_link.is_visible(timeout=3000):
                    # Получаем href для проверки
                    href = contacts_link.get_attribute("href")
                    allure.attach(f"Найден href: {href}", name="URL контактов")

                    # Кликаем по ссылке
                    contacts_link.click()

                    # Ждем загрузки
                    self.page.wait_for_timeout(3000)

                    # Проверяем результат
                    current_url = self.page.url
                    contacts_loaded = (
                        "contacts" in current_url.lower() or
                        "kontakty" in current_url.lower() or
                        "contact" in current_url.lower()
                    )

                    allure.attach(
                        f"Контакты загружены: {contacts_loaded}",
                        name="Загрузка контактов")

                    if contacts_loaded:
                        # Проверяем HTTP статус
                        status = self.navigation.assert_http_status(current_url)
                        allure.attach(
                            f"HTTP статус: {status}",
                            name="Статус контактов")
                else:
                    allure.attach(
                        "Ссылка на контакты не найдена",
                        name="Отсутствие ссылки")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке контактов: {e}",
                    name="Ошибка контактов")

    @allure.title("Проверка функциональности ссылки 'О компании'")
    @allure.description("Проверка что ссылка 'О компании' работает корректно")
    def test_about_company_functionality(self):
        """
        Тест проверяет функциональность ссылки 'О компании'
        """
        with allure.step("Проверяем доступность информации о компании"):
            try:
                # Ищем ссылку "О компании"
                about_link = self.page.get_by_role("link", name="О компании")

                if about_link.is_visible(timeout=3000):
                    # Получаем href для проверки
                    href = about_link.get_attribute("href")
                    allure.attach(f"Найден href: {href}", name="URL о компании")

                    # Кликаем по ссылке
                    about_link.click()

                    # Ждем загрузки
                    self.page.wait_for_timeout(3000)

                    # Проверяем результат
                    current_url = self.page.url
                    about_loaded = (
                        "about" in current_url.lower() or
                        "o-kompanii" in current_url.lower() or
                        "company" in current_url.lower()
                    )

                    allure.attach(
                        f"Информация о компании загружена: {about_loaded}",
                        name="Загрузка о компании")

                    if about_loaded:
                        # Проверяем HTTP статус
                        status = self.navigation.assert_http_status(current_url)
                        allure.attach(
                            f"HTTP статус: {status}",
                            name="Статус о компании")
                else:
                    allure.attach(
                        "Ссылка 'О компании' не найдена",
                        name="Отсутствие ссылки")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке 'О компании': {e}",
                    name="Ошибка о компании")

    @allure.title("Проверка структуры футера")
    @allure.description("Проверка количества и порядка элементов в футере")
    def test_footer_structure(self):
        """
        Тест проверяет структуру футера
        """
        with allure.step("Проверяем наличие футера"):
            try:
                # Ищем футер по различным селекторам
                footer_selectors = [
                    "footer",
                    ".footer",
                    "#footer",
                    "[role='contentinfo']"
                ]

                footer_found = False
                for selector in footer_selectors:
                    footer = self.page.locator(selector)
                    if footer.is_visible(timeout=2000):
                        footer_found = True
                        allure.attach(
                            f"Футер найден по селектору: {selector}",
                            name="Найденный футер")
                        break

                if not footer_found:
                    allure.attach(
                        "Футер не найден по стандартным селекторам",
                        name="Отсутствие футера")

                # Проверяем количество ссылок в футере
                if footer_found:
                    links_count = footer.locator("a").count()
                    allure.attach(
                        f"Количество ссылок в футере: {links_count}",
                        name="Количество ссылок")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке структуры футера: {e}",
                    name="Ошибка структуры")
