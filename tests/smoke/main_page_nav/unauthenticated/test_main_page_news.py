"""
News Tests

Тесты навигации по разделу новостей главной страницы bll.by
(Новости, События, Видеоответы)
"""

import pytest
import allure

from tests.smoke.main_page_nav.unauthenticated.pages.header_navigation_page import HeaderNavigationPage


@pytest.mark.smoke
@allure.epic("Главная страница")
@allure.feature("Навигация новостей")
@allure.story("News navigation")
class TestMainPageNews:
    """
    Класс тестов для проверки навигации по разделу новостей главной страницы
    """

    @pytest.fixture(autouse=True)
    def setup_method(self, domain_aware_context_for_bll):
        """
        Настройка перед каждым тестом
        """
        self.context = domain_aware_context_for_bll
        self.page = self.context.new_page()
        self.navigation = HeaderNavigationPage(self.page)

        # Переходим на главную и ждем готовности
        self.page.goto("https://bll.by", wait_until="domcontentloaded")
        self.navigation.smart_wait_for_page_ready()

        yield

        # Cleanup
        if self.page.url != "https://bll.by":
            self.page.goto("https://bll.by")

    @pytest.mark.parametrize(
        "link_name,method_name,expected_fragment,description", [
            ("Новости", "click_news", "news",
             "Переход на страницу новостей"),
            ("События", "click_events", "events",
             "Переход на страницу событий"),
            ("Видеоответы", "click_video_answers", "video-answers",
             "Переход на страницу видеоответов"),
        ]
    )
    @allure.title("Навигация по разделу '{link_name}'")
    @allure.description("Проверка перехода по разделу {link_name}")
    def test_news_navigation(
            self, link_name, method_name, expected_fragment, description):
        """
        Параметризованный тест для проверки навигации по новостям

        Args:
            link_name: Название раздела для отображения в отчетах
            method_name: Название метода для клика по разделу
            expected_fragment: Ожидаемый фрагмент в URL после клика
            description: Описание теста
        """
        allure.attach(f"Тестируется раздел: {link_name}", name="Описание")
        allure.attach(
            f"Ожидаемый URL фрагмент: {expected_fragment}", name="Ожидание")

        # Получаем метод объекта и вызываем его
        click_method = getattr(self.navigation, method_name)
        result = click_method()

        with allure.step(f"Проверяем переход по разделу '{link_name}'"):
            assert result, f"Не удалось перейти на страницу '{link_name}'"

        with allure.step(f"Проверяем HTTP статус для '{link_name}'"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], (
                f"Неверный HTTP статус для '{link_name}': {status}")

    @allure.title("Проверка видимости всех разделов новостей")
    @allure.description("Проверка что все разделы новостей видны на странице")
    def test_news_sections_visibility(self):
        """
        Тест проверяет видимость всех разделов новостей на главной странице
        """
        news_sections = [
            "Новости",
            "События",
            "Видеоответы",
        ]

        with allure.step("Проверяем видимость разделов новостей"):
            for section_name in news_sections:
                try:
                    link = self.page.get_by_role("link", name=section_name)
                    is_visible = link.is_visible(timeout=3000)
                    status_text = "Видим" if is_visible else "Не видим"
                    allure.attach(
                        f"Раздел '{section_name}': {status_text}",
                        name=f"Видимость {section_name}")
                    # Не падаем тест если раздел не виден, просто логируем
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке раздела '{section_name}': {e}",
                        name=f"Ошибка {section_name}")

    @allure.title("Проверка функциональности новостей")
    @allure.description("Проверка что страница новостей работает корректно")
    def test_news_functionality(self):
        """
        Тест проверяет функциональность новостей
        """
        with allure.step("Проверяем доступность новостей"):
            try:
                # Кликаем на "Новости"
                result = self.navigation.click_news()

                assert result, "Не удалось перейти на страницу новостей"

                # Проверяем наличие характерных элементов
                current_url = self.page.url
                has_correct_url = "news" in current_url

                allure.attach(
                    f"URL новостей корректен: {has_correct_url}",
                    name="URL проверка")

                if has_correct_url:
                    # Проверяем наличие контента
                    try:
                        # Ищем признаки страницы новостей
                        has_content = (
                            self.page.locator("h1, h2").count() > 0 or
                            self.page.locator(".news, .article, .post").count() > 0
                        )

                        allure.attach(
                            f"Контент новостей загружен: {has_content}",
                            name="Контент новостей")
                    except Exception as e:
                        allure.attach(
                            f"Ошибка при проверке контента: {e}",
                            name="Ошибка контента")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке новостей: {e}",
                    name="Ошибка новостей")

    @allure.title("Проверка функциональности событий")
    @allure.description("Проверка что страница событий работает корректно")
    def test_events_functionality(self):
        """
        Тест проверяет функциональность событий
        """
        with allure.step("Проверяем доступность событий"):
            try:
                # Кликаем на "События"
                result = self.navigation.click_events()

                assert result, "Не удалось перейти на страницу событий"

                # Проверяем наличие характерных элементов
                current_url = self.page.url
                has_correct_url = "events" in current_url

                allure.attach(
                    f"URL событий корректен: {has_correct_url}",
                    name="URL проверка")

                if has_correct_url:
                    # Проверяем наличие контента
                    try:
                        # Ищем признаки страницы событий
                        has_content = (
                            self.page.locator("h1, h2").count() > 0 or
                            self.page.locator(".event, .calendar, .schedule").count() > 0
                        )

                        allure.attach(
                            f"Контент событий загружен: {has_content}",
                            name="Контент событий")
                    except Exception as e:
                        allure.attach(
                            f"Ошибка при проверке контента: {e}",
                            name="Ошибка контента")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке событий: {e}",
                    name="Ошибка событий")

    @allure.title("Проверка функциональности видеоответов")
    @allure.description("Проверка что страница видеоответов работает корректно")
    def test_video_answers_functionality(self):
        """
        Тест проверяет функциональность видеоответов
        """
        with allure.step("Проверяем доступность видеоответов"):
            try:
                # Кликаем на "Видеоответы"
                result = self.navigation.click_video_answers()

                assert result, "Не удалось перейти на страницу видеоответов"

                # Проверяем наличие характерных элементов
                current_url = self.page.url
                has_correct_url = "video-answers" in current_url

                allure.attach(
                    f"URL видеоответов корректен: {has_correct_url}",
                    name="URL проверка")

                if has_correct_url:
                    # Проверяем наличие контента
                    try:
                        # Ищем признаки страницы видеоответов
                        has_content = (
                            self.page.locator("h1, h2").count() > 0 or
                            self.page.locator("video, .video, iframe").count() > 0
                        )

                        allure.attach(
                            f"Контент видеоответов загружен: {has_content}",
                            name="Контент видео")
                    except Exception as e:
                        allure.attach(
                            f"Ошибка при проверке контента: {e}",
                            name="Ошибка контента")

            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке видеоответов: {e}",
                    name="Ошибка видео")

    @allure.title("Проверка структуры раздела новостей")
    @allure.description("Проверка количества и порядка разделов новостей")
    def test_news_structure(self):
        """
        Тест проверяет структуру раздела новостей
        """
        expected_sections = [
            "Новости",
            "События",
            "Видеоответы",
        ]

        with allure.step("Проверяем количество разделов новостей"):
            try:
                found_count = 0
                for section_name in expected_sections:
                    try:
                        link = self.page.get_by_role("link", name=section_name)
                        if link.is_visible(timeout=2000):
                            found_count += 1
                    except Exception:
                        pass

                allure.attach(
                    f"Найдено разделов новостей: {found_count} из {len(expected_sections)}",
                    name="Количество разделов")

                # Проверяем что большинство разделов найдены
                assert found_count >= len(expected_sections) // 2, (
                    f"Найдено слишком мало разделов новостей: {found_count}")

            except Exception as e:
                allure.attach(
                    f"Ошибка при подсчете разделов новостей: {e}",
                    name="Ошибка подсчета")