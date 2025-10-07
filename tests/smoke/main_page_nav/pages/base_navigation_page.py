"""
Базовый класс для Page Objects главной навигации

Предоставляет общие методы для всех типов навигации на главной странице bll.by
"""

from typing import Optional
from framework.app.pages.base_page import BasePage


class BaseNavigationPage(BasePage):
    """
    Базовый класс для всех элементов навигации главной страницы

    Обеспечивает унифицированный интерфейс для:
    - Проверки готовности страницы
    - Общей логики кликов и ожидания
    - Проверок URL и состояния элементов
    """

    def __init__(self, page):
        super().__init__(page)

    def smart_wait_for_page_ready(self) -> bool:
        """
        Умное ожидание готовности главной страницы

        Returns:
            bool: True если страница готова
        """
        try:
            # Ожидаем появления основных элементов навигации
            self.page.wait_for_selector("header", timeout=10000)
            self.page.wait_for_load_state('domcontentloaded', timeout=10000)

            # Небольшая пауза для стабилизации JS
            self.page.wait_for_timeout(500)

            return True
        except Exception as e:
            print(f"Ошибка ожидания готовности главной страницы: {e}")
            return False

    def wait_for_url_change(self, expected_fragment: str, timeout: int = 15000) -> bool:
        """
        Ожидает изменения URL с ожидаемым фрагментом

        Args:
            expected_fragment: ожидаемый фрагмент в URL
            timeout: таймаут ожидания в мс

        Returns:
            bool: True если URL соответствует ожиданию
        """
        try:
            self.page.wait_for_url(lambda url: expected_fragment.lower() in str(url).lower(),
                                  timeout=timeout)

            # Получить финальный URL для логирования
            final_url = self.page.url
            print(f"✅ URL изменился на: {final_url}")

            # Финальная проверка
            return expected_fragment.lower() in final_url.lower()

        except Exception as e:
            print(f"❌ Не удалось дождаться изменения URL на '{expected_fragment}': {e}")
            return False

    def assert_http_status(self, url: str) -> Optional[int]:
        """
        Проверяет HTTP статус URL (аналогично burger menu тестам)

        Args:
            url: URL для проверки

        Returns:
            int: HTTP код или None если ошибка
        """
        import requests

        try:
            # Проверка с редиректами
            response = requests.get(url, allow_redirects=True, timeout=30,
                                  headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

            status = response.status_code
            print(f"📊 HTTP статус '{url}': {status}")

            # Проверяем допустимые статусы
            assert status in [200, 301, 302], f"HTTP {status} для URL: {url}"

            return status

        except Exception as e:
            print(f"❌ Ошибка проверки HTTP статуса для {url}: {e}")
            return None

    def safe_click_and_verify(self, locator_desc: str, expected_url_fragment: str,
                             timeout: int = 10000) -> bool:
        """
        Безопасный клик с автоматической проверкой URL

        Args:
            locator_desc: описание локатора для клика
            expected_url_fragment: ожидаемый фрагмент в URL
            timeout: таймаут для клика

        Returns:
            bool: True если клик и проверка успешны
        """
        try:
            # Клик по описанию
            if "textbox" in locator_desc:
                # Для textbox - focus и fill
                self.page.get_by_role("textbox", name=locator_desc).click()

                # Набиваем тестовый текст
                test_text = "закон о физической культуре и спорте"
                self.page.fill(f'textbox[name="{locator_desc}"]', test_text)

                # Ищем и кликаем submit или enter
                self.page.keyboard.press("Enter")

            else:
                # Для ссылок - обычный клик по тексту
                self.page.get_by_role("link", name=locator_desc).click()

            # Ждем изменения URL
            return self.wait_for_url_change(expected_url_fragment)

        except Exception as e:
            print(f"❌ Ошибка клика и проверки для '{locator_desc}': {e}")
            return False
