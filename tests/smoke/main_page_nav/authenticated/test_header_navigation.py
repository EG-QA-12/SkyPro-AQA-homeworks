"""
Header Navigation Tests

Тесты навигации хэдэра главной страницы bll.by
(версия без теста клика по логотипу - ссылка удалена с сайта)
"""

import pytest
import allure

from .pages.header_navigation_page import HeaderNavigationPage


@pytest.mark.smoke
@allure.epic("Главная страница")
@allure.feature("Навигация хэдэра")
@allure.story("Header navigation")
class TestHeaderNavigation:
    """
    Класс тестов для проверки навигации в header главной страницы
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

    @allure.title("Клик по телефону в header")
    @allure.description("Проверка что телефон ведет на tel: ссылку")
    def test_phone_link_click(self):
        """Тест клика по телефону"""
        allure.attach("Тестируется телефонная ссылка +375 17 388-32-52", name="Описание")

        result = self.navigation.click_phone_number()

        with allure.step("Проверяем что ссылка ведет на tel:"):
            assert result, "Телефон не ведет на tel: ссылку"

        with allure.step("Проверяем HTTP статус главной страницы"):
            status = self.navigation.assert_http_status("https://bll.by")
            assert status in [200, 301, 302], f"Неверный HTTP статус главной страницы: {status}"

    @allure.title("Навигация 'О платформе'")
    @allure.description("Проверка перехода на страницу информации о платформе")
    def test_platform_info_navigation(self):
        """Тест клика по 'О платформе'"""
        allure.attach("Тестируется переход на https://bll.by/about", name="Описание")

        result = self.navigation.click_platform_info()

        with allure.step("Проверяем переход на страницу about"):
            assert result, "Не удалось перейти на страницу 'О платформе'"

        with allure.step("Проверяем HTTP статус страницы about"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы about: {status}"

    @allure.title("Навигация 'Клуб экспертов'")
    @allure.description("Проверка перехода на страницу клуба экспертов")
    def test_expert_club_navigation(self):
        """Тест клика по 'Клуб экспертов'"""
        allure.attach("Тестируется переход на https://expert.bll.by/experts", name="Описание")

        result = self.navigation.click_expert_club()

        with allure.step("Проверяем переход на expert.bll.by/experts"):
            assert result, "Не удалось перейти на страницу клуба экспертов"

        with allure.step("Проверяем HTTP статус страницы экспертов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы экспертов: {status}"

    @allure.title("Навигация 'Бонусы'")
    @allure.description("Проверка перехода на страницу бонусов с robust fallback логиками")
    def test_bonuses_navigation(self):
        """Тест клика по 'Бонусы' с множественными fallback"""
        allure.attach("Тестируется переход на https://bonus.bll.by/bonus с умными fallback логиками для headless стабильности", name="Описание")

        result = self.navigation.click_bonuses_robust()

        with allure.step("Проверяем переход на https://bonus.bll.by/bonus через любой из fallback способов"):
            current_url = self.page.url
            assert result and current_url == "https://bonus.bll.by/bonus", f"Не удалось перейти на страницу бонусов. Ожидался URL: https://bonus.bll.by/bonus, получен: {current_url}"

        with allure.step("Проверяем HTTP статус финальной страницы"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы бонусов: {status}"

    @allure.title("Popup профиля пользователя")
    @allure.description("Проверка появления popup профиля с ссылкой на админку - robust версия")
    def test_my_profile_popup(self):
        """Тест клика по профилю с popup и множественными fallback"""
        allure.attach("Тестируется popup профиля с ссылкой на админку с умными fallback селекторами", name="Описание")

        result = self.navigation.click_my_profile_robust()

        with allure.step("Проверяем появление popup с админкой через какой-либо из working селекторов"):
            assert result, "Popup профиля с админкой не появился ни с одним из селекторов"

    @allure.title("Поисковая строка")
    @allure.description("Проверка работы поисковой строки с переходом на страницу результатов")
    def test_search_functionality(self):
        """Тест поисковой функциональности"""
        allure.attach("Тестируется поиск 'закон о физической культуре и спорте' с переходом на docs?q=", name="Описание")

        # Клик по поисковой строке
        result = self.navigation.click_search_box()
        assert result, "Не удалось кликнуть по поисковой строке"

        # Заполнение и поиск
        result = self.navigation.fill_search_and_submit("закон о физической культуре и спорте")
        assert result, "Поиск не привел к ожидаемому результату"

        with allure.step("Проверяем HTTP статус страницы поиска"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы поиска: {status}"

    @allure.title("Навигация 'Кодексы'")
    @allure.description("Проверка перехода на страницу кодексов")
    def test_codes_navigation(self):
        """Тест клика по 'Кодексы'"""
        allure.attach("Тестируется переход на страницу кодексов", name="Описание")

        result = self.navigation.click_codes()

        with allure.step("Проверяем переход на страницу кодексов"):
            assert result, "Не удалось перейти на страницу кодексов"

        with allure.step("Проверяем HTTP статус страницы кодексов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы кодексов: {status}"

    @allure.title("Навигация 'Горячие темы'")
    @allure.description("Проверка перехода на страницу горячих тем")
    def test_hot_topics_navigation(self):
        """Тест клика по 'Горячие темы'"""
        allure.attach("Тестируется переход на страницу горячих тем", name="Описание")

        result = self.navigation.click_hot_topics()

        with allure.step("Проверяем переход на страницу горячих тем"):
            assert result, "Не удалось перейти на страницу горячих тем"

        with allure.step("Проверяем HTTP статус страницы горячих тем"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы горячих тем: {status}"

    @allure.title("Навигация 'Всё по одной теме'")
    @allure.description("Проверка перехода на страницу подборок тем")
    def test_everything_by_topic_navigation(self):
        """Тест клика по 'Всё по одной теме'"""
        allure.attach("Тестируется переход на страницу подборок тем", name="Описание")

        result = self.navigation.click_everything_by_topic()

        with allure.step("Проверяем переход на страницу подборок тем"):
            assert result, "Не удалось перейти на страницу подборок тем"

        with allure.step("Проверяем HTTP статус страницы подборок тем"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы подборок тем: {status}"

    @allure.title("Навигация 'Навигаторы'")
    @allure.description("Проверка перехода на страницу навигаторов")
    def test_navigators_navigation(self):
        """Тест клика по 'Навигаторы'"""
        allure.attach("Тестируется переход на страницу навигаторов", name="Описание")

        result = self.navigation.click_navigators()

        with allure.step("Проверяем переход на страницу навигаторов"):
            assert result, "Не удалось перейти на страницу навигаторов"

        with allure.step("Проверяем HTTP статус страницы навигаторов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы навигаторов: {status}"

    @allure.title("Навигация 'Чек-листы'")
    @allure.description("Проверка перехода на страницу чек-листов")
    def test_checklists_navigation(self):
        """Тест клика по 'Чек-листы'"""
        allure.attach("Тестируется переход на страницу чек-листов", name="Описание")

        result = self.navigation.click_checklists()

        with allure.step("Проверяем переход на страницу чек-листов"):
            assert result, "Не удалось перейти на страницу чек-листов"

        with allure.step("Проверяем HTTP статус страницы чек-листов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы чек-листов: {status}"

    @allure.title("Навигация 'Каталоги форм'")
    @allure.description("Проверка перехода на страницу каталогов форм")
    def test_catalogs_forms_navigation(self):
        """Тест клика по 'Каталоги форм'"""
        allure.attach("Тестируется переход на страницу каталогов форм", name="Описание")

        result = self.navigation.click_catalogs_forms()

        with allure.step("Проверяем переход на страницу каталогов форм"):
            assert result, "Не удалось перейти на страницу каталогов форм"

        with allure.step("Проверяем HTTP статус страницы каталогов форм"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы каталогов форм: {status}"

    @allure.title("Навигация 'Конструкторы'")
    @allure.description("Проверка перехода на страницу конструкторов")
    def test_constructors_navigation(self):
        """Тест клика по 'Конструкторы'"""
        allure.attach("Тестируется переход на страницу конструкторов", name="Описание")

        result = self.navigation.click_constructors()

        with allure.step("Проверяем переход на страницу конструкторов"):
            assert result, "Не удалось перейти на страницу конструкторов"

        with allure.step("Проверяем HTTP статус страницы конструкторов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы конструкторов: {status}"

    @allure.title("Навигация 'Справочники'")
    @allure.description("Проверка перехода на страницу справочников")
    def test_directories_navigation(self):
        """Тест клика по 'Справочники'"""
        allure.attach("Тестируется переход на страницу справочников", name="Описание")

        result = self.navigation.click_directories()

        with allure.step("Проверяем переход на страницу справочников"):
            assert result, "Не удалось перейти на страницу справочников"

        with allure.step("Проверяем HTTP статус страницы справочников"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы справочников: {status}"

    @allure.title("Навигация 'Калькуляторы'")
    @allure.description("Проверка перехода на страницу калькуляторов")
    def test_calculators_navigation(self):
        """Тест клика по 'Калькуляторы'"""
        allure.attach("Тестируется переход на страницу калькуляторов", name="Описание")

        result = self.navigation.click_calculators()

        with allure.step("Проверяем переход на страницу калькуляторов"):
            assert result, "Не удалось перейти на страницу калькуляторов"

        with allure.step("Проверяем HTTP статус страницы калькуляторов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы калькуляторов: {status}"

    @allure.title("Навигация 'Закупки'")
    @allure.description("Проверка перехода на страницу закупок")
    def test_procurement_navigation(self):
        """Тест клика по 'Закупки'"""
        allure.attach("Тестируется переход на https://gz.bll.by/", name="Описание")

        result = self.navigation.click_procurement()

        with allure.step("Проверяем переход на https://gz.bll.by/"):
            current_url = self.page.url
            assert result and current_url.startswith("https://gz.bll.by/"), f"Не удалось перейти на страницу закупок. Ожидался URL: https://gz.bll.by/, получен: {current_url}"

        with allure.step("Проверяем HTTP статус страницы закупок"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы закупок: {status}"

    @allure.title("Навигация 'Тесты'")
    @allure.description("Проверка перехода на страницу тестов")
    def test_tests_navigation(self):
        """Тест клика по 'Тесты'"""
        allure.attach("Тестируется переход на страницу тестов", name="Описание")

        result = self.navigation.click_tests()

        with allure.step("Проверяем переход на страницу тестов"):
            assert result, "Не удалось перейти на страницу тестов"

        with allure.step("Проверяем HTTP статус страницы тестов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы тестов: {status}"

    @allure.title("Навигация 'Сообщество'")
    @allure.description("Проверка перехода на страницу сообщества")
    def test_community_navigation(self):
        """Тест клика по 'Сообщество'"""
        allure.attach("Тестируется переход на https://expert.bll.by/", name="Описание")

        result = self.navigation.click_community()

        with allure.step("Проверяем переход на https://expert.bll.by/"):
            current_url = self.page.url
            assert result and current_url.startswith("https://expert.bll.by/"), f"Не удалось перейти на страницу сообщества. Ожидался URL: https://expert.bll.by/, получен: {current_url}"

        with allure.step("Проверяем HTTP статус страницы сообщества"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы сообщества: {status}"

    @allure.title("Навигация 'Задать вопрос'")
    @allure.description("Проверка перехода на страницу создания вопроса")
    def test_ask_question_navigation(self):
        """Тест клика по 'Задать вопрос'"""
        allure.attach("Тестируется переход на https://expert.bll.by/questions/create", name="Описание")

        result = self.navigation.click_ask_question()

        with allure.step("Проверяем переход на https://expert.bll.by/questions/create"):
            current_url = self.page.url
            assert result and current_url == "https://expert.bll.by/questions/create", f"Не удалось перейти на страницу создания вопроса. Ожидался URL: https://expert.bll.by/questions/create, получен: {current_url}"

        with allure.step("Проверяем HTTP статус страницы создания вопроса"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы создания вопроса: {status}"

    @allure.title("Навигация 'Все вопросы'")
    @allure.description("Проверка перехода на страницу всех вопросов")
    def test_all_questions_navigation(self):
        """Тест клика по 'Все вопросы'"""
        allure.attach("Тестируется переход на https://expert.bll.by/questions", name="Описание")

        result = self.navigation.click_all_questions()

        with allure.step("Проверяем переход на https://expert.bll.by/questions"):
            current_url = self.page.url
            assert result and current_url == "https://expert.bll.by/questions", f"Не удалось перейти на страницу всех вопросов. Ожидался URL: https://expert.bll.by/questions, получен: {current_url}"

        with allure.step("Проверяем HTTP статус страницы всех вопросов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы всех вопросов: {status}"

    @allure.title("Навигация 'Справочная информация'")
    @allure.description("Проверка перехода на страницу справочной информации")
    def test_reference_info_navigation(self):
        """Тест клика по 'Справочная информация'"""
        allure.attach("Тестируется переход на страницу справочной информации", name="Описание")

        result = self.navigation.click_reference_info()

        with allure.step("Проверяем переход на страницу справочной информации"):
            assert result, "Не удалось перейти на страницу справочной информации"

        with allure.step("Проверяем HTTP статус страницы справочной информации"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы справочной информации: {status}"

    @allure.title("Навигация 'Ставка рефинансирования'")
    @allure.description("Проверка перехода на страницу ставки рефинансирования")
    def test_refinancing_rate_navigation(self):
        """Тест клика по 'Ставка рефинансирования'"""
        allure.attach("Тестируется переход на страницу ставки рефинансирования", name="Описание")

        result = self.navigation.click_refinancing_rate()

        with allure.step("Проверяем переход на страницу ставки рефинансирования"):
            assert result, "Не удалось перейти на страницу ставки рефинансирования"

        with allure.step("Проверяем HTTP статус страницы ставки рефинансирования"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы ставки рефинансирования: {status}"

    @allure.title("Навигация 'Базовая величина'")
    @allure.description("Проверка перехода на страницу базовой величины")
    def test_base_value_navigation(self):
        """Тест клика по 'Базовая величина'"""
        allure.attach("Тестируется переход на страницу базовой величины", name="Описание")

        result = self.navigation.click_base_value()

        with allure.step("Проверяем переход на страницу базовой величины"):
            assert result, "Не удалось перейти на страницу базовой величины"

        with allure.step("Проверяем HTTP статус страницы базовой величины"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы базовой величины: {status}"

    @allure.title("Навигация 'Средняя з/п за январь'")
    @allure.description("Проверка перехода на страницу средней зарплаты")
    def test_average_salary_january_navigation(self):
        """Тест клика по 'Средняя з/п за январь'"""
        allure.attach("Тестируется переход на страницу средней зарплаты за январь", name="Описание")

        result = self.navigation.click_average_salary_january()

        with allure.step("Проверяем переход на страницу средней зарплаты"):
            assert result, "Не удалось перейти на страницу средней зарплаты"

        with allure.step("Проверяем HTTP статус страницы средней зарплаты"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы средней зарплаты: {status}"

    @allure.title("Навигация 'Пособия на детей'")
    @allure.description("Проверка перехода на страницу пособий на детей")
    def test_child_allowances_navigation(self):
        """Тест клика по 'Пособия на детей'"""
        allure.attach("Тестируется переход на страницу пособий на детей", name="Описание")

        result = self.navigation.click_child_allowances()

        with allure.step("Проверяем переход на страницу пособий на детей"):
            assert result, "Не удалось перейти на страницу пособий на детей"

        with allure.step("Проверяем HTTP статус страницы пособий на детей"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы пособий на детей: {status}"

    @allure.title("Навигация 'Базовая арендная величина'")
    @allure.description("Проверка перехода на страницу базовой арендной величины")
    def test_base_rental_value_navigation(self):
        """Тест клика по 'Базовая арендная величина'"""
        allure.attach("Тестируется переход на страницу базовой арендной величины", name="Описание")

        result = self.navigation.click_base_rental_value()

        with allure.step("Проверяем переход на страницу базовой арендной величины"):
            assert result, "Не удалось перейти на страницу базовой арендной величины"

        with allure.step("Проверяем HTTP статус страницы базовой арендной величины"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы базовой арендной величины: {status}"

    @allure.title("Навигация 'МЗП за февраль'")
    @allure.description("Проверка перехода на страницу минимальной зарплаты")
    def test_minimum_wage_february_navigation(self):
        """Тест клика по 'МЗП за февраль'"""
        allure.attach("Тестируется переход на страницу минимальной зарплаты за февраль", name="Описание")

        result = self.navigation.click_minimum_wage_february()

        with allure.step("Проверяем переход на страницу минимальной зарплаты"):
            assert result, "Не удалось перейти на страницу минимальной зарплаты"

        with allure.step("Проверяем HTTP статус страницы минимальной зарплаты"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы минимальной зарплаты: {status}"

    @allure.title("Навигация 'БПМ'")
    @allure.description("Проверка перехода на страницу бюджета прожиточного минимума")
    def test_bpm_navigation(self):
        """Тест клика по 'БПМ'"""
        allure.attach("Тестируется переход на страницу бюджета прожиточного минимума", name="Описание")

        result = self.navigation.click_bpm()

        with allure.step("Проверяем переход на страницу бюджета прожиточного минимума"):
            assert result, "Не удалось перейти на страницу бюджета прожиточного минимума"

        with allure.step("Проверяем HTTP статус страницы бюджета прожиточного минимума"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы бюджета прожиточного минимума: {status}"

    @allure.title("Навигация 'Курсы валют'")
    @allure.description("Проверка перехода на страницу курсов валют")
    def test_currency_rates_navigation(self):
        """Тест клика по 'Курсы валют'"""
        allure.attach("Тестируется переход на страницу курсов валют", name="Описание")

        result = self.navigation.click_currency_rates()

        with allure.step("Проверяем переход на страницу курсов валют"):
            assert result, "Не удалось перейти на страницу курсов валют"

        with allure.step("Проверяем HTTP статус страницы курсов валют"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы курсов валют: {status}"

    @allure.title("Навигация 'Формы документов'")
    @allure.description("Проверка перехода на страницу форм документов")
    def test_document_forms_navigation(self):
        """Тест клика по 'Формы документов'"""
        allure.attach("Тестируется переход на страницу форм документов", name="Описание")

        result = self.navigation.click_document_forms()

        with allure.step("Проверяем переход на страницу форм документов"):
            assert result, "Не удалось перейти на страницу форм документов"

        with allure.step("Проверяем HTTP статус страницы форм документов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы форм документов: {status}"

    @allure.title("Навигация 'Выбор редакции'")
    @allure.description("Проверка перехода на страницу выбора редакции")
    def test_edition_selection_navigation(self):
        """Тест клика по 'Выбор редакции'"""
        allure.attach("Тестируется переход на страницу выбора редакции", name="Описание")

        result = self.navigation.click_edition_selection()

        with allure.step("Проверяем переход на страницу выбора редакции"):
            assert result, "Не удалось перейти на страницу выбора редакции"

        with allure.step("Проверяем HTTP статус страницы выбора редакции"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы выбора редакции: {status}"

    @allure.title("Навигация 'Обзоры и подписки'")
    @allure.description("Проверка перехода на страницу обзоров и подписок")
    def test_reviews_subscriptions_navigation(self):
        """Тест клика по 'Обзоры и подписки'"""
        allure.attach("Тестируется переход на страницу обзоров и подписок", name="Описание")

        result = self.navigation.click_reviews_subscriptions()

        with allure.step("Проверяем переход на страницу обзоров и подписок"):
            assert result, "Не удалось перейти на страницу обзоров и подписок"

        with allure.step("Проверяем HTTP статус страницы обзоров и подписок"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы обзоров и подписок: {status}"

    @allure.title("Навигация 'Новости'")
    @allure.description("Проверка перехода на страницу новостей")
    def test_news_navigation(self):
        """Тест клика по 'Новости'"""
        allure.attach("Тестируется переход на страницу новостей", name="Описание")

        result = self.navigation.click_news()

        with allure.step("Проверяем переход на страницу новостей"):
            assert result, "Не удалось перейти на страницу новостей"

        with allure.step("Проверяем HTTP статус страницы новостей"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы новостей: {status}"

    @allure.title("Навигация 'Календарь мероприятий'")
    @allure.description("Проверка перехода на страницу календаря мероприятий")
    def test_events_calendar_navigation(self):
        """Тест клика по 'Календарь мероприятий'"""
        allure.attach("Тестируется переход на страницу календаря мероприятий", name="Описание")

        result = self.navigation.click_events_calendar()

        with allure.step("Проверяем переход на страницу календаря мероприятий"):
            assert result, "Не удалось перейти на страницу календаря мероприятий"

        with allure.step("Проверяем HTTP статус страницы календаря мероприятий"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы календаря мероприятий: {status}"

    @allure.title("Навигация 'Видеоответы NEW'")
    @allure.description("Проверка перехода на страницу видеоответов")
    def test_video_answers_navigation(self):
        """Тест клика по 'Видеоответы NEW'"""
        allure.attach("Тестируется переход на страницу видеоответов", name="Описание")

        result = self.navigation.click_video_answers()

        with allure.step("Проверяем переход на страницу видеоответов"):
            assert result, "Не удалось перейти на страницу видеоответов"

        with allure.step("Проверяем HTTP статус страницы видеоответов"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы видеоответов: {status}"

    @allure.title("Навигация 'Интервью'")
    @allure.description("Проверка перехода на страницу интервью")
    def test_interviews_navigation(self):
        """Тест клика по 'Интервью'"""
        allure.attach("Тестируется переход на страницу интервью", name="Описание")

        result = self.navigation.click_interviews()

        with allure.step("Проверяем переход на страницу интервью"):
            assert result, "Не удалось перейти на страницу интервью"

        with allure.step("Проверяем HTTP статус страницы интервью"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы интервью: {status}"

    @allure.title("Навигация 'Мероприятия'")
    @allure.description("Проверка перехода на страницу мероприятий")
    def test_events_navigation(self):
        """Тест клика по 'Мероприятия'"""
        allure.attach("Тестируется переход на страницу мероприятий", name="Описание")

        result = self.navigation.click_events()

        with allure.step("Проверяем переход на страницу мероприятий"):
            assert result, "Не удалось перейти на страницу мероприятий"

        with allure.step("Проверяем HTTP статус страницы мероприятий"):
            status = self.navigation.assert_http_status(self.page.url)
            assert status in [200, 301, 302], f"Неверный HTTP статус страницы мероприятий: {status}"
