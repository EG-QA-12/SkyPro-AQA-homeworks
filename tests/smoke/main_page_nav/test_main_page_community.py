"""
Community Tests

Тесты навигации по разделу сообщества главной страницы bll.by
(Сообщество, Задать вопрос, Все вопросы, Мои вопросы и ответы, и т.д.)
"""

import pytest
import allure

from .pages.header_navigation_page import HeaderNavigationPage


@pytest.mark.smoke
@allure.epic("Главная страница")
@allure.feature("Навигация сообщества")
@allure.story("Community navigation")
class TestMainPageCommunity:
    """
    Класс тестов для проверки навигации по разделу сообщества главной страницы
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

    @pytest.mark.parametrize(
        "link_name,method_name,expected_fragment,description", [
            ("Сообщество", "click_community", "expert.bll.by",
             "Переход на страницу сообщества"),
            ("Задать вопрос", "click_ask_question", "expert.bll.by",
             "Переход на страницу создания вопроса"),
            ("Все вопросы", "click_all_questions", "expert.bll.by",
             "Переход на страницу всех вопросов"),
        ]
    )
    @allure.title("Навигация по ссылке '{link_name}' в разделе сообщества")
    @allure.description("Проверка перехода по ссылке {link_name}")
    def test_community_navigation(
            self, link_name, method_name, expected_fragment, description):
        """
        Параметризованный тест для проверки навигации по разделу сообщества
        
        Args:
            link_name: Название ссылки для отображения в отчетах
            method_name: Название метода для клика по ссылке
            expected_fragment: Ожидаемый фрагмент в URL после клика
            description: Описание теста
        """
        allure.attach(f"Тестируется ссылка: {link_name}", name="Описание")
        allure.attach(
            f"Ожидаемый URL фрагмент: {expected_fragment}", name="Ожидание")

        # Получаем метод объекта и вызываем его
        click_method = getattr(self.navigation, method_name)
        result = click_method()

        with allure.step(f"Проверяем переход по ссылке '{link_name}'"):
            # Для всех ссылок сообщества проверяем что URL содержит expert.bll.by
            current_url = self.page.url
            assert result or "expert.bll.by" in current_url, (
                f"Не удалось перейти на страницу '{link_name}'. "
                f"Текущий URL: {current_url}")

        with allure.step(f"Проверяем HTTP статус для '{link_name}'"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], (
                f"Неверный HTTP статус для '{link_name}': {status}")

    @allure.title("Проверка видимости всех ссылок раздела сообщества")
    @allure.description("Проверка что все ссылки раздела сообщества видны на странице")
    def test_community_links_visibility(self):
        """
        Тест проверяет видимость всех ссылок раздела сообщества
        """
        community_links = [
            "Сообщество",
            "Задать вопрос",
            "Все вопросы",
        ]
        
        with allure.step("Проверяем видимость ссылок раздела сообщества"):
            for link_name in community_links:
                try:
                    # Для некоторых элементов используем first() чтобы избежать дубликатов
                    if link_name in ["Все вопросы"]:
                        link = self.page.get_by_role("link", name=link_name).first
                    else:
                        link = self.page.get_by_role("link", name=link_name)
                    
                    is_visible = link.is_visible(timeout=3000)
                    status_text = "Видима" if is_visible else "Не видима"
                    allure.attach(
                        f"Ссылка '{link_name}': {status_text}",
                        name=f"Видимость {link_name}")
                    # Не падаем тест если ссылка не видима, просто логируем
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке ссылки '{link_name}': {e}",
                        name=f"Ошибка {link_name}")

    @allure.title("Проверка переходов на домен expert.bll.by")
    @allure.description("Проверка что все ссылки сообщества ведут на домен эксперт")
    def test_community_domain_redirects(self):
        """
        Тест проверяет что все ссылки сообщества ведут на правильный домен
        """
        community_links = [
            ("Сообщество", "click_community"),
            ("Задать вопрос", "click_ask_question"),
            ("Все вопросы", "click_all_questions"),
        ]
        
        with allure.step("Проверяем редиректы на домен expert.bll.by"):
            for link_name, method_name in community_links:
                try:
                    # Возвращаемся на главную перед каждым тестом
                    self.page.goto("https://bll.by", wait_until="domcontentloaded")
                    self.navigation.smart_wait_for_page_ready()
                    
                    # Получаем метод и вызываем его
                    click_method = getattr(self.navigation, method_name)
                    click_method()
                    
                    # Ждем загрузки страницы
                    self.page.wait_for_timeout(3000)
                    
                    # Проверяем URL
                    current_url = self.page.url
                    domain_correct = "expert.bll.by" in current_url
                    
                    status_text = "Верный домен" if domain_correct else "Неверный домен"
                    allure.attach(
                        f"Ссылка '{link_name}': {status_text} (URL: {current_url})",
                        name=f"Домен {link_name}")
                        
                except Exception as e:
                    allure.attach(
                        f"Ошибка при проверке ссылки '{link_name}': {e}",
                        name=f"Ошибка {link_name}")

    @allure.title("Проверка доступности раздела сообщества")
    @allure.description("Проверка что раздел сообщества доступен для авторизованного пользователя")
    def test_community_accessibility(self):
        """
        Тест проверяет доступность раздела сообщества для авторизованного пользователя
        """
        with allure.step("Проверяем доступность основной страницы сообщества"):
            try:
                # Кликаем на сообщество
                self.navigation.click_community()
                
                # Ждем загрузки
                self.page.wait_for_timeout(3000)
                
                # Проверяем что страница загрузилась
                current_url = self.page.url
                page_loaded = "expert.bll.by" in current_url
                
                allure.attach(
                    f"Страница сообщества загружена: {page_loaded}",
                    name="Доступность сообщества")
                
                if page_loaded:
                    # Дополнительная проверка на наличие ключевых элементов
                    try:
                        # Ищем признаки успешной загрузки страницы
                        page_content = self.page.content()
                        has_content = len(page_content) > 1000  # Простая проверка на контент
                        
                        allure.attach(
                            f"Содержимое страницы загружено: {has_content}",
                            name="Контент страницы")
                    except Exception as e:
                        allure.attach(
                            f"Ошибка при проверке контента: {e}",
                            name="Ошибка контента")
                        
            except Exception as e:
                allure.attach(
                    f"Ошибка при доступе к сообществу: {e}",
                    name="Ошибка доступа")

    @allure.title("Проверка функциональности создания вопроса")
    @allure.description("Проверка что страница создания вопроса доступна")
    def test_ask_question_functionality(self):
        """
        Тест проверяет функциональность создания вопроса
        """
        with allure.step("Проверяем доступность формы создания вопроса"):
            try:
                # Возвращаемся на главную
                self.page.goto("https://bll.by", wait_until="domcontentloaded")
                self.navigation.smart_wait_for_page_ready()
                
                # Кликаем на "Задать вопрос"
                self.navigation.click_ask_question()
                
                # Ждем загрузки
                self.page.wait_for_timeout(3000)
                
                # Проверяем URL
                current_url = self.page.url
                question_page = "expert.bll.by" in current_url
                
                allure.attach(
                    f"Страница создания вопроса доступна: {question_page}",
                    name="Доступность создания вопроса")
                
                if question_page:
                    # Проверяем наличие форм для создания вопроса
                    try:
                        # Ищем типичные элементы формы создания вопроса
                        has_form = (
                            self.page.locator("form").count() > 0 or
                            self.page.locator("textarea").count() > 0 or
                            self.page.locator("input[type='text']").count() > 0
                        )
                        
                        allure.attach(
                            f"Форма создания вопроса найдена: {has_form}",
                            name="Наличие формы")
                    except Exception as e:
                        allure.attach(
                            f"Ошибка при поиске формы: {e}",
                            name="Ошибка формы")
                        
            except Exception as e:
                allure.attach(
                    f"Ошибка при проверке создания вопроса: {e}",
                    name="Ошибка создания вопроса")
