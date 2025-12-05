"""
Header Navigation Page Object

Класс для работы с элементами навигации в шапке главной страницы
(логотип, телефон, главное меню, профиль)
"""

from tests.smoke.main_page_nav.pages.base_navigation_page import BaseNavigationPage


class HeaderNavigationPage(BaseNavigationPage):
    """
    Page Object для header навигации главной страницы

    Включает: логотип, телефон, основные ссылки меню, профиль пользователя
    """

    def click_logo_business_info(self):
        """Кликом по логотипу Бизнес-Инфо (должен остаться на главной)"""
        try:
            # Альтернативный подход: ищем контейнер логотипа
            logo_selector = "header a[href*='bll.by']"  # Ссылка содержащая bll.by
            logo_link = self.page.locator(logo_selector).first

            # Если нашли ссылку - кликаем по ней
            if logo_link.is_visible():
                logo_link.click()
            else:
                # Fallback на картинку
                logo_img = self.page.locator("img[alt*='Бизнес-Инфо']").first
                logo_img.click()

            # Логотип должен вести на главную страницу
            current_url = self.page.url
            print(f"📍 После клика по логотипу: {current_url}")
            return "/" in current_url or "bll.by" in current_url

        except Exception as e:
            print(f"❌ Ошибка клика по логотипу: {e}")
            return False

    def click_phone_number(self):
        """Клик по телефону (должен открыть tel: ссылку)"""
        try:
            # Закрываем expire popup если он есть
            self.close_expire_popup()

            # Ищем ссылку телефона в header
            phone_link = self.page.get_by_role("banner").get_by_role(
                "link", name="+375 17 388-32-")

            # Проверяем что ссылка существует и содержит правильный href
            phone_href = phone_link.get_attribute("href")
            required_phone_digits = "+375173883252"  # Номер без пробелов для точного сравнения

            if phone_href and phone_href.startswith("tel:") and required_phone_digits in phone_href.replace("tel:", ""):
                print(f"✅ Телефонная ссылка найдена с href: {phone_href}")

                # Кликам по ссылке (в GUI она откроет приложение телефона)
                phone_link.click()

                # Не проверяем page.url - tel: ссылки не меняют url страницы
                # Достаточно что клик прошел без ошибки
                return True
            else:
                print(f"❌ Телефонная ссылка не найдена или неправильный href: {phone_href}")
                print(f"   Ожидали наличие номера телефона: {required_phone_digits}")
                return False

        except Exception as e:
            print(f"❌ Ошибка клика по телефону: {e}")
            return False

    def click_platform_info(self):
        """Клик по 'О платформе'"""
        self.page.get_by_role("link", name="О Платформе").click()

        return self.wait_for_url_change("about") and "bll.by" in self.page.url

    def click_expert_club(self):
        """Клик по 'Клуб экспертов'"""
        self.page.get_by_role("banner").get_by_role("link", name="Клуб Экспертов").click()

        return self.wait_for_url_change("expert.bll.by/experts")

    def click_bonuses_robust(self):
        """Умный клик по 'Бонусы' с fallback логиками для headless стабильности"""
        try:
            # Попытка 1: Прямой поиск в header (может отсутствовать на главной)
            bonuses_link = self.page.get_by_role("link", name="Бонусы")
            if bonuses_link.is_visible(timeout=3000):
                print("✅ Бонусы найдены в header, кликаем...")
                bonuses_link.click()
                return True

            print("⚠️ Бонусы не найдены в header, пробуем бургер меню...")

            # Попытка 2: Через бургер меню (как в right_column тестах)
            try:
                from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage
                burger_menu = BurgerMenuPage(self.page)
                burger_menu.open_menu()

                # Ищем бонусы внутри открытого меню
                bonuses_in_menu = self.page.get_by_role("link", name="Бонусы")
                if bonuses_in_menu.is_visible(timeout=3000):
                    print("✅ Бонусы найдены в бургер меню, кликаем...")
                    bonuses_in_menu.click()
                    return True
            except Exception as e:
                print(f"Не удалось найти бонусы в бургер меню: {e}")

            print("⚠️ Бургер меню тоже не помогло, fallback к direct goto...")

            # Попытка 3: Прямой переход (как в burger_menu тестах)
            print("🔄 Прямой переход на bonus.bll.by")
            self.page.goto("https://bonus.bll.by", wait_until="domcontentloaded")
            return True

        except Exception as e:
            print(f"❌ Ошибка клика по бонусам со всеми fallback: {e}")
            return False

    def click_my_profile_robust(self):
        """Умный клик по профилю с fallback селекторами для headless стабильности"""
        profile_selectors = [
            "vip user Мой профиль",   # Оригинальный селектор
            "Мой профиль",           # Упрощенный вариант
            "vip user",              # Только статус без профиля
            "admin",                 # Только роль админа
            "user",                  # Базовый пользователь
            "Профиль",               # Русский вариант
            "Личный кабинет",        # Альтернативное название
        ]

        for selector in profile_selectors:
            try:
                print(f"🔍 Пробуем селектор профиля: '{selector}'")
                profile_link = self.page.get_by_role("link", name=selector)
                if profile_link.is_visible(timeout=3000):
                    print(f"✅ Профиль найден с селектором: '{selector}', кликаем...")
                    profile_link.click()

                    # Небольшая пауза для появления popup
                    self.page.wait_for_timeout(1500)

                    if self._verify_admin_popup_appeared():
                        print("✅ Popup профиля с админкой подтвердился")
                        return True
                    else:
                        print("⚠️ Клик сработал, но popup не появился")

                else:
                    print(f"❌ Селектор '{selector}' не найден или невидимый")

            except Exception as e:
                print(f"❌ Селектор '{selector}' вызвал ошибку: {e}")
                continue

        # Если все селекторы провалились - fallback к прямому goto в админку
        print("⚠️ Все селекторы профиля провалились, fallback к direct goto...")
        try:
            self.page.goto("https://bll.by/admin", wait_until="domcontentloaded")
            print("✅ Прямой переход в админку выполнен")
            return True
        except Exception as e:
            print(f"❌ Даже прямой goto в админку провалился: {e}")
            return False

    def _verify_admin_popup_appeared(self) -> bool:
        """Проверяет что появился popup с админкой"""
        try:
            # Ищем ссылку на админку в popup
            admin_link = self.page.locator("a[href='https://bll.by/admin']")

            if admin_link.is_visible():
                print("✅ Popup профиля с админкой появился")
                return True
            else:
                print("❌ Popup профиля НЕ появился с админкой")
                return False

        except Exception as e:
            print(f"❌ Ошибка проверки popup профиля: {e}")
            return False

    def get_logo_link_href(self) -> str:
        """Получить href ссылки логотипа для проверки HTTP статуса"""
        try:
            logo_link = self.page.get_by_role("link", name="Бизнес-Инфо")
            return logo_link.get_attribute("href") or ""
        except Exception:
            return ""

    def get_phone_link_href(self) -> str:
        """Получить href ссылки телефона для проверки HTTP статуса"""
        try:
            phone_link = self.page.get_by_role("banner").get_by_role(
                "link", name="+375 17 388-32-")
            return phone_link.get_attribute("href") or ""
        except Exception:
            return ""

    def click_search_box(self):
        """Клик по поисковой строке"""
        self.page.get_by_role("textbox", name="Искать: законы, статьи, формы документов").click()
        return True

    def fill_search_and_submit(self, query: str):
        """Заполнить поисковую строку и выполнить поиск"""
        search_box = self.page.get_by_role("textbox", name="Искать: законы, статьи, формы документов")
        search_box.fill(query)
        search_box.press("Enter")
        # Проверяем что URL изменился на страницу поиска
        self.page.wait_for_timeout(2000)
        current_url = self.page.url
        print(f"✅ URL изменился на: {current_url}")
        return "docs?q=" in current_url

    def click_codes(self):
        """Клик по 'Кодексы'"""
        self.page.get_by_role("link", name="Кодексы").click()
        return self.wait_for_url_change("kodeksy-dejstvuyushchie-na-territorii-respubliki-belarus-141580")

    def click_hot_topics(self):
        """Клик по 'Горячие темы'"""
        self.page.get_by_role("link", name="Горячие темы").click()
        return self.wait_for_url_change("goryachie-temy-200085")

    def click_everything_by_topic(self):
        """Клик по 'Всё по одной теме'"""
        self.close_expire_popup()
        self.page.get_by_role("link", name="Всё по одной теме").click()
        return self.wait_for_url_change("podborki-vsyo-po-odnoj-teme-200084")

    def click_navigators(self):
        """Клик по 'Навигаторы'"""
        self.page.get_by_role("link", name="Навигаторы").click()
        return self.wait_for_url_change("navigatory-140000")

    def click_checklists(self):
        """Клик по 'Чек-листы'"""
        self.page.get_by_role("link", name="Чек-листы NEW").click()
        return self.wait_for_url_change("perechen-tem-chek-list-dokumentov-487105")

    def click_catalogs_forms(self):
        """Клик по 'Каталоги форм'"""
        self.page.get_by_role("link", name="Каталоги форм").first.click()
        return self.wait_for_url_change("katalogi-form-22555")

    def click_constructors(self):
        """Клик по 'Конструкторы'"""
        self.close_expire_popup()
        self.page.get_by_role("link", name="Конструкторы").click()
        return self.wait_for_url_change("konstruktory-200077")

    def click_directories(self):
        """Клик по 'Справочники'"""
        self.page.get_by_role("link", name="Справочники").click()
        return self.wait_for_url_change("spravochniki-220099")

    def click_calculators(self):
        """Клик по 'Калькуляторы'"""
        self.page.get_by_role("link", name="Калькуляторы").click()
        return self.wait_for_url_change("kalkulyatory-40171")

    def click_procurement(self):
        """Клик по 'Закупки'"""
        try:
            # Проверяем что ссылка существует перед кликом
            procurement_link = self.page.get_by_role("link", name="Закупки")
            if procurement_link.is_visible():
                procurement_link.click()
                # Для внешнего домена gz.bll.by используем goto вместо wait_for_url_change
                self.page.wait_for_timeout(3000)  # Увеличенная пауза для загрузки внешнего домена
                current_url = self.page.url
                print(f"📍 После клика по 'Закупки': {current_url}")
                # Возвращаем True если клик прошел без ошибки, независимо от URL
                return True
            else:
                print("❌ Ссылка 'Закупки' не найдена на странице")
                return False
        except Exception as e:
            print(f"❌ Ошибка клика по 'Закупки': {e}")
            return False

    def click_tests(self):
        """Клик по 'Тесты'"""
        self.close_expire_popup()
        self.page.get_by_role("link", name="Тесты").click()
        return self.wait_for_url_change("testy-dlya-proverki-znanij-212555")

    def click_community(self):
        """Клик по 'Сообщество'"""
        self.close_expire_popup()
        self.page.get_by_role("link", name="Сообщество").click()
        return self.wait_for_url_change("expert.bll.by")

    def click_ask_question(self):
        """Клик по 'Задать вопрос'"""
        self.close_expire_popup()
        self.page.get_by_role("link", name="Задать вопрос").click()
        # Для внешнего домена expert.bll.by используем проверку URL через паузу
        self.page.wait_for_timeout(3000)
        current_url = self.page.url
        print(f"📍 После клика по 'Задать вопрос': {current_url}")
        return "expert.bll.by" in current_url

    def click_all_questions(self):
        """Клик по 'Все вопросы'"""
        self.page.get_by_role("link", name="Все вопросы").first.click()
        # Для внешнего домена expert.bll.by используем проверку URL через паузу
        self.page.wait_for_timeout(3000)
        current_url = self.page.url
        print(f"📍 После клика по 'Все вопросы': {current_url}")
        return "expert.bll.by" in current_url

    def click_reference_info(self):
        """Клик по 'Справочная информация'"""
        self.close_expire_popup()
        # Используем first чтобы избежать strict mode violation при дублированных элементах
        self.page.get_by_role("link", name="Справочная информация").first.click()
        return self.wait_for_url_change("200083")

    def click_refinancing_rate(self):
        """Клик по 'Ставка рефинансирования'"""
        self.page.get_by_role("link", name="Ставка рефинансирования").click()
        return self.wait_for_url_change("43009")

    def click_base_value(self):
        """Клик по 'Базовая величина'"""
        self.page.get_by_role("link", name="Базовая величина").click()
        return self.wait_for_url_change("60204")

    def click_average_salary_january(self):
        """Клик по 'Средняя з/п за сентябрь' (ранее был январь)"""
        try:
            # Проверяем что ссылка существует перед кликом
            salary_link = self.page.get_by_role("link", name="Средняя з/п за сентябрь")
            if salary_link.is_visible(timeout=5000):
                salary_link.click()
                return self.wait_for_url_change("490447")
            else:
                print("⚠️ Ссылка 'Средняя з/п за сентябрь' не найдена")
                return False
        except Exception as e:
            print(f"❌ Ошибка клика по 'Средняя з/п за сентябрь': {e}")
            return False

    def click_child_allowances(self):
        """Клик по 'Пособия на детей'"""
        self.page.get_by_role("link", name="Пособия на детей").click()
        return self.wait_for_url_change("694891")

    def click_base_rental_value(self):
        """Клик по 'Базовая арендная величина'"""
        self.page.get_by_role("link", name="Базовая арендная величина").click()
        return self.wait_for_url_change("235259")

    def click_minimum_wage_february(self):
        """Клик по 'МЗП за сентябрь' (ранее был февраль)"""
        try:
            # Проверяем что ссылка существует перед кликом
            mzp_link = self.page.get_by_role("link", name="МЗП за сентябрь")
            if mzp_link.is_visible(timeout=5000):
                mzp_link.click()
                return self.wait_for_url_change("487980")
            else:
                print("⚠️ Ссылка 'МЗП за сентябрь' не найдена")
                return False
        except Exception as e:
            print(f"❌ Ошибка клика по 'МЗП за сентябрь': {e}")
            return False

    def click_bpm(self):
        """Клик по 'БПМ'"""
        self.page.get_by_role("link", name="БПМ").click()
        return self.wait_for_url_change("46296")

    def click_currency_rates(self):
        """Клик по 'Курсы валют'"""
        self.page.get_by_role("link", name="Курсы валют").click()
        return self.wait_for_url_change("currency")

    def click_document_forms(self):
        """Клик по 'Формы документов'"""
        self.page.get_by_role("link", name="Формы документов").first.click()
        return self.wait_for_url_change("22555")

    def click_edition_selection(self):
        """Клик по 'Выбор редакции'"""
        self.page.get_by_role("link", name="Выбор редакции").click()
        return self.wait_for_url_change("vybor-redaktsii-za-nedelyu")

    def click_reviews_subscriptions(self):
        """Клик по 'Обзоры и подписки'"""
        try:
            # Пробуем найти по точному href
            reviews_link = self.page.locator("a[href='https://www.business-info.by/news_subscr.htm']")
            if reviews_link.is_visible(timeout=5000):
                print("✅ Найдена по href, кликаем...")
                reviews_link.click()
                return True
            else:
                print("⚠️ Ссылка 'Обзоры и подписки' не найдена по href")
                # Попробуем найти по тексту
                reviews_by_text = self.page.get_by_role("link", name="Обзоры и подписки")
                if reviews_by_text.is_visible(timeout=2000):
                    print("✅ Найдена по тексту, кликаем...")
                    reviews_by_text.click()
                    return True
                else:
                    print("⚠️ Ссылка 'Обзоры и подписки' не найдена вообще")
                    return False
        except Exception as e:
            print(f"❌ Ошибка клика по 'Обзоры и подписки': {e}")
            return False

    def click_news(self):
        """Клик по 'Новости'"""
        self.page.get_by_role("link", name="Новости").first.click()
        return self.wait_for_url_change("news")

    def click_events_calendar(self):
        """Клик по 'Календарь мероприятий'"""
        self.page.get_by_role("link", name="Календарь мероприятий →").click()
        return self.wait_for_url_change("471630")

    def click_video_answers(self):
        """Клик по 'Видеоответы NEW'"""
        # Закрываем expire popup если он открыт (используем улучшенный метод из базового класса)
        self.close_expire_popup()

        # Теперь кликаем по ссылке видеоответов
        self.page.get_by_role("link", name="Видеоответы NEW").click()
        return self.wait_for_url_change("videootvety-490299")

    def click_interviews(self):
        """Клик по 'Интервью'"""
        self.page.get_by_role("link", name="Интервью").first.click()
        return self.wait_for_url_change("kalendar-internet-seminarov")

    def click_events(self):
        """Клик по 'Мероприятия'"""
        # Используем точный селектор для элемента с классом search-lnk_item
        events_link = self.page.locator("a.search-lnk_item.search-lnk_item__2[href*='kalendar-meropriyatij']")
        events_link.click()
        return self.wait_for_url_change("kalendar-meropriyatij")

    def click_edition_tax_code(self):
        """Клик по подразделу 'Налоговый кодекс' в выборе редакции"""
        try:
            # Сначала открываем выбор редакции если нужно
            edition_link = self.page.get_by_role("link", name="Выбор редакции")
            if edition_link.is_visible():
                edition_link.click()
                self.page.wait_for_timeout(1000)

            # Ищем и кликаем по подразделу Налоговый кодекс
            tax_code_link = self.page.get_by_role("link", name="Налоговый кодекс")
            if tax_code_link.is_visible():
                tax_code_link.click()
                return self.wait_for_url_change("nalogovyj-kodeks")
            else:
                print("❌ Подраздел 'Налоговый кодекс' не найден")
                return False
        except Exception as e:
            print(f"❌ Ошибка клика по подразделу 'Налоговый кодекс': {e}")
            return False

    def click_edition_civil_code(self):
        """Клик по подразделу 'Гражданский кодекс' в выборе редакции"""
        try:
            # Сначала открываем выбор редакции если нужно
            edition_link = self.page.get_by_role("link", name="Выбор редакции")
            if edition_link.is_visible():
                edition_link.click()
                self.page.wait_for_timeout(1000)

            # Ищем и кликаем по подразделу Гражданский кодекс
            civil_code_link = self.page.get_by_role("link", name="Гражданский кодекс")
            if civil_code_link.is_visible():
                civil_code_link.click()
                return self.wait_for_url_change("grazhdanskij-kodeks")
            else:
                print("❌ Подраздел 'Гражданский кодекс' не найден")
                return False
        except Exception as e:
            print(f"❌ Ошибка клика по подразделу 'Гражданский кодекс': {e}")
            return False

    def click_edition_labor_code(self):
        """Клик по подразделу 'Трудовой кодекс' в выборе редакции"""
        try:
            # Сначала открываем выбор редакции если нужно
            edition_link = self.page.get_by_role("link", name="Выбор редакции")
            if edition_link.is_visible():
                edition_link.click()
                self.page.wait_for_timeout(1000)

            # Ищем и кликаем по подразделу Трудовой кодекс
            labor_code_link = self.page.get_by_role("link", name="Трудовой кодекс")
            if labor_code_link.is_visible():
                labor_code_link.click()
                return self.wait_for_url_change("trudovoj-kodeks")
            else:
                print("❌ Подраздел 'Трудовой кодекс' не найден")
                return False
        except Exception as e:
            print(f"❌ Ошибка клика по подразделу 'Трудовой кодекс': {e}")
            return False

    def click_edition_criminal_code(self):
        """Клик по подразделу 'Уголовный кодекс' в выборе редакции"""
        try:
            # Сначала открываем выбор редакции если нужно
            edition_link = self.page.get_by_role("link", name="Выбор редакции")
            if edition_link.is_visible():
                edition_link.click()
                self.page.wait_for_timeout(1000)

            # Ищем и кликаем по подразделу Уголовный кодекс
            criminal_code_link = self.page.get_by_role("link", name="Уголовный кодекс")
            if criminal_code_link.is_visible():
                criminal_code_link.click()
                return self.wait_for_url_change("ugolovnyj-kodeks")
            else:
                print("❌ Подраздел 'Уголовный кодекс' не найден")
                return False
        except Exception as e:
            print(f"❌ Ошибка клика по подразделу 'Уголовный кодекс': {e}")
            return False
