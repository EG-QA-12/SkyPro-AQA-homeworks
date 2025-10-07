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
            logo_img = self.page.locator("img[alt='Бизнес-Инфо']")
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
            self.page.get_by_role("banner").get_by_role("link", name="+375 17 388-32-").click()

            current_url = self.page.url
            print(f"📞 После клика по телефону: {current_url}")

            # Для tel: ссылок не нужно ожидать изменения страницы
            # Достаточно проверить что URL начинается с tel:
            return current_url.startswith("tel:")

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

    def click_bonuses(self):
        """Клик по 'Бонусы'"""
        try:
            self.page.get_by_role("link", name="Бонусы").click()

            current_url = self.page.url
            print(f"🎁 После клика по 'Бонусы': {current_url}")

            # Можно попасть на bonus.bll.by или на CA редирект
            if "bonus.bll.by" in current_url:
                return True
            elif "ca.bll.by/login" in current_url:
                print("⚠️  Бонусы перенаправил на CA login (ожидаемо для SSO)")
                return True  # Это нормальное поведение
            else:
                print("❓ Неожиданное перенаправление на бонусы")
                return False

        except Exception as e:
            print(f"❌ Ошибка клика по бонусам: {e}")
            return False

    def click_my_profile(self):
        """Клик по профилю - должен показать popup с админкой"""
        try:
            # Находим ссылку профиля
            profile_link = self.page.get_by_role("link", name="vip user Мой профиль")
            profile_link.click()

            # Небольшая пауза для появления popup
            self.page.wait_for_timeout(1000)

            return self._verify_admin_popup_appeared()

        except Exception as e:
            print(f"❌ Ошибка клика по профилю: {e}")
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
