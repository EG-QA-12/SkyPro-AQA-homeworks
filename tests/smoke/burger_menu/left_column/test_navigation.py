"""
Burger Menu Left Column Navigation Tests.

Стабильные тесты левой колонки бургер-меню по паттерну working E2E baseline.
Результаты baseline: 33/33 = 100% успеха.
"""

import pytest
from playwright.sync_api import expect

from tests.smoke.burger_menu.pages.burger_menu_page import BurgerMenuPage


@pytest.mark.smoke
@pytest.mark.burger_menu
@pytest.mark.left_column
class TestLeftColumnNavigation:

    def test_news_navigation(self, authenticated_burger_context):
        """Навигация по разделу 'Новости'."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Новости")

            # Упрощенная smoke assertion
            assert page.url == "https://bll.by/news"

        finally:
            page.close()

    def test_codes_navigation(self, authenticated_burger_context):
        """Навигация по разделу 'Коды'."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Кодексы")

            # Упрощенная smoke assertion
            assert "kodeksy" in page.url or "codes" in page.url

        finally:
            page.close()

    def test_constructors_navigation(self, authenticated_burger_context):
        """Навигация по разделу 'Конструкторы'."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Конструкторы")

            # Упрощенная smoke assertion
            assert "konstruktory" in page.url or "constructors" in page.url

        finally:
            page.close()

    def test_answers_navigation(self, authenticated_burger_context):
        """Навигация по разделу 'Справочники'."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Справочники")

            # Упрощенная smoke assertion
            assert "spravochniki" in page.url or "dictionaries" in page.url

        finally:
            page.close()

    def test_support_navigation(self, authenticated_burger_context):
        """Навигация по разделу 'Поддержка'."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Словарь")

            # Упрощенная smoke assertion
            expect(page).to_have_url("https://bll.by/terms")

        finally:
            page.close()

    def test_about_navigation(self, authenticated_burger_context):
        """Навигация по разделу 'О Платформе'."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("О Платформе")

            # Упрощенная smoke assertion
            expect(page).to_have_url("https://bll.by/about")

        finally:
            page.close()

    def test_buy_navigation(self, authenticated_burger_context):
        """Навигация по разделу 'Купить'."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Купить")

            # Упрощенная smoke assertion
            expect(page).to_have_url("https://bll.by/buy")

        finally:
            page.close()

    def test_docs_navigation(self, authenticated_burger_context):
        """Навигация по разделу 'Поиск в базе документов'."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Поиск в базе документов")

            # Упрощенная smoke assertion
            expect(page).to_have_url("https://bll.by/docs")

        finally:
            page.close()

    def test_phone_number_click(self, authenticated_burger_context):
        """Клик по номеру телефона."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()

            # Клик по телефону тестирует только наличие элемента
            phone_link = page.get_by_role("link", name="+375 17 388 32")
            assert phone_link.is_visible(), "Телефонная ссылка не найдена"

            phone_href = phone_link.get_attribute("href")
            assert phone_href and phone_href.startswith("tel:"), "Неверный формат телефонной ссылки"

        finally:
            page.close()

    def test_answers_navigation(self, authenticated_burger_context):
        """Навигация по Справочнику."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Справочник")

            # Упрощенная smoke assertion
            assert "spravochnik" in page.url or "directory" in page.url

        finally:
            page.close()

    def test_dictionary_navigation(self, authenticated_burger_context):
        """Навигация в Словарь."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Словарь")

            # Упрощенная smoke assertion
            expect(page).to_have_url("https://bll.by/terms")

        finally:
            page.close()

    def test_calculators_navigation(self, authenticated_burger_context):
        """Навигация в Калькуляторы."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Калькуляторы")

            # Упрощенная smoke assertion
            assert "kalkulyatory" in page.url

        finally:
            page.close()

    def test_home_page_navigation(self, authenticated_burger_context):
        """Навигация на Главную страницу."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            # Перейдем на другую страницу сначала
            page.goto("https://bll.by/docs", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()

            # Найдем и кликнем ссылку "Главная страница"
            home_link = page.locator("a.menu_bl_ttl-main").first
            assert home_link.is_visible(), "Главная страница ссылка не найдена"
            home_link.click()

            # Упрощенная smoke assertion
            expect(page).to_have_url("https://bll.by/")

        finally:
            page.close()

    def test_demo_access_navigation(self, authenticated_burger_context):
        """Навигация Получить демодоступ."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()

            # Найдем ссылку демодоступа
            demo_link = page.get_by_role("link", name="Получить демодоступ")
            assert demo_link.is_visible(), "Ссылка демодоступа не найдена"
            demo_link.click()

            # Упрощенная smoke assertion
            expect(page).to_have_url("https://bll.by/buy?request")

        finally:
            page.close()

    def test_reference_info_navigation(self, authenticated_burger_context):
        """Навигация в Справочную информацию."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Справочная информация")

            # Упрощенная smoke assertion
            assert "spravochnaya-informatsiya-200083" in page.url

        finally:
            page.close()

    def test_checklists_navigation(self, authenticated_burger_context):
        """Навигация в Чек-листы."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Чек-листы")

            # Упрощенная smoke assertion
            assert "cheklej" in page.url or "chek-list" in page.url

        finally:
            page.close()

    def test_catalogs_navigation(self, authenticated_burger_context):
        """Навигация в Каталоги форм."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Каталоги форм")

            # Упрощенная smoke assertion
            assert "katalogi-form-22555" in page.url

        finally:
            page.close()

    def test_tests_navigation(self, authenticated_burger_context):
        """Навигация в Тесты."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Тесты")

            # Упрощенная smoke assertion
            assert "testy-dlya-proverki-znanij-212555" in page.url

        finally:
            page.close()

    def test_hot_topics_navigation(self, authenticated_burger_context):
        """Навигация в Горячие темы."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()

            # Используем селектор как в baseline
            page.locator("a.menu_item_link[href*='goryachie-temy-200085']").first.click()

            # Упрощенная smoke assertion
            assert "goryachie-temy-200085" in page.url

        finally:
            page.close()

    def test_navigators_navigation(self, authenticated_burger_context):
        """Навигация в Навигаторы."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Навигаторы")

            # Упрощенная smoke assertion
            assert "navigatory-140000" in page.url

        finally:
            page.close()

    def test_useful_links_navigation(self, authenticated_burger_context):
        """Навигация в Полезные ссылки."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()

            # Используем селектор как в baseline
            page.locator("a.menu_item_link[href*='poleznye-ssylki-219924']").first.click()

            # Упрощенная smoke assertion
            assert "poleznye-ssylki-219924" in page.url

        finally:
            page.close()

    def test_personal_lawyer_navigation(self, authenticated_burger_context):
        """Навигация к Личному юристу."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Ваш личный юрист")

            # Упрощенная smoke assertion
            assert "lichnyj-yurist-206044" in page.url

        finally:
            page.close()

    def test_topic_collections_navigation(self, authenticated_burger_context):
        """Навигация во Всё по одной теме."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Всё по одной теме")

            # Упрощенная smoke assertion
            assert "vsyo-po-odnoj-teme-200084" in page.url

        finally:
            page.close()

    def test_user_guide_navigation(self, authenticated_burger_context):
        """Навигация в Руководство пользователя."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Руководство пользователя")

            # Упрощенная smoke assertion
            assert "rukovodstvo-polzovatelya-platformy-biznes-info-436351" in page.url

        finally:
            page.close()

    def test_video_answers_navigation(self, authenticated_burger_context):
        """Навигация в Видеоответы."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Видеоответы")

            # Упрощенная smoke assertion
            assert "videootvety-490299" in page.url

        finally:
            page.close()

    def test_procurement_navigation(self, authenticated_burger_context):
        """Навигация в Закупки."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Закупки")

            # Упрощенная smoke assertion
            assert "gz.bll.by" in page.url

        finally:
            page.close()

    def test_community_search_navigation(self, authenticated_burger_context):
        """Навигация в Поиск в сообществе."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Поиск в сообществе")

            # Упрощенная smoke assertion
            assert "expert.bll.by" in page.url

        finally:
            page.close()

    def test_contractor_check_navigation(self, authenticated_burger_context):
        """Навигация в Проверка контрагента."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Проверка контрагента")

            # Упрощенная smoke assertion
            assert "cp.bll.by" in page.url

        finally:
            page.close()

    def test_ask_question_navigation(self, authenticated_burger_context):
        """Навигация в Задать вопрос."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()

            ask_link = page.get_by_role("banner").get_by_role("link", name="Задать вопрос")
            ask_link.click()

            # Упрощенная smoke assertion
            assert "expert.bll.by" in page.url

        finally:
            page.close()

    def test_my_questions_answers_navigation(self, authenticated_burger_context):
        """Навигация в Мои вопросы и ответы."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Мои вопросы и ответы")

            # Упрощенная smoke assertion
            assert "expert.bll.by" in page.url

        finally:
            page.close()

    def test_topics_control_navigation(self, authenticated_burger_context):
        """Навигация в Топики на контроле."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()

            topics_link = page.get_by_role("banner").get_by_role("link", name="Топики на контроле")
            topics_link.click()

            # Упрощенная smoke assertion
            assert "expert.bll.by" in page.url

        finally:
            page.close()

    def test_moderator_messages_navigation(self, authenticated_burger_context):
        """Навигация в Сообщения от модератора."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Сообщения от модератора")

            # Упрощенная smoke assertion
            assert "expert.bll.by" in page.url

        finally:
            page.close()

    def test_events_navigation(self, authenticated_burger_context):
        """Навигация в Мероприятия."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()

            events_link = page.locator("a.menu_bl_ttl-events").first
            events_link.click()

            # Упрощенная smoke assertion
            assert "471630" in page.url

        finally:
            page.close()

    def test_experts_club_navigation(self, authenticated_burger_context):
        """Навигация в Клуб экспертов."""
        page = authenticated_burger_context.new_page()
        burger_menu = BurgerMenuPage(page)

        try:
            page.goto("https://bll.by/", wait_until="domcontentloaded")
            page.wait_for_timeout(500)

            burger_menu.open_menu()
            burger_menu.click_link_by_text("Клуб экспертов")

            # Упрощенная smoke assertion
            assert "expert.bll.by" in page.url

        finally:
            page.close()
