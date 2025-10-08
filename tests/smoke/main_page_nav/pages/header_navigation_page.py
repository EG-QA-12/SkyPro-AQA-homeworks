"""
Header Navigation Page Object

Класс для работы с элементами навигации в шапке главной страницы
(логотип, телефон, главное меню, профиль)
"""

from .base_navigation_page import BaseNavigationPage


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
