"""
Интеграционный тест для полного жизненного цикла вопроса и ответа

Сценарий:
1. Пользователь создает вопрос
2. Модератор проверяет вопрос в админке
3. Модератор модерирует и публикует вопрос
4. Админ проверяет наличие вопроса на сайте
5. Эксперт отвечает на вопрос
6. Модератор проверяет ответ в админке
7. Модератор модерирует и публикует ответ
8. Админ проверяет наличие ответа на сайте
9. Пользователь ставит лайк ответу эксперта
"""

import pytest
import re
import time
from playwright.sync_api import expect
from tests.e2e.workflow_fixtures import (
    workflow_context, user_page, moderator_page, admin_page, expert_page
)


class TestQuestionWorkflow:
    """Интеграционный тест полного жизненного цикла вопроса и ответа"""

    @pytest.mark.workflow
    def test_01_user_creates_question(self, user_page, workflow_context):
        """Шаг 1: Пользователь создает и отправляет вопрос"""
        page = user_page
        
        # Генерация уникального вопроса для тестирования
        timestamp = int(time.time())
        question_title = f"Тестовый вопрос {timestamp}"
        question_body = f"Это тестовый вопрос, созданный автоматически в {timestamp}"
        
        # Навигация на страницу создания вопроса
        page.goto("https://bll.by/ask-question")
        
        # Заполняем форму вопроса
        page.fill("input#question-title", question_title)
        page.fill("textarea#question-body", question_body)
        page.click("select#question-category")
        page.click("option[value='legal']")
        
        # Отправляем вопрос
        page.click("button#submit-question")
        
        # Проверяем успешное создание
        expect(page.locator("div.success-message")).to_be_visible()
        
        # Сохраняем данные в контекст для следующих тестов
        workflow_context.set("question_title", question_title)
        workflow_context.set("question_body", question_body)
        workflow_context.set("question_timestamp", timestamp)
        
        # Дополнительная проверка
        assert "Ваш вопрос успешно отправлен" in page.content()

    @pytest.mark.workflow
    def test_02_moderator_checks_question(self, moderator_page, workflow_context):
        """Шаг 2: Модератор проверяет вопрос в админке"""
        page = moderator_page
        question_title = workflow_context.get("question_title")
        
        # Заходим в админку
        page.goto("https://bll.by/admin/questions")
        
        # Поиск по заголовку вопроса
        page.fill("input#search-questions", question_title)
        page.click("button#search-button")
        
        # Проверка что вопрос найден
        question_row = page.locator(f"tr:has-text('{question_title}')")
        expect(question_row).to_be_visible()
        
        # Сохраняем ID вопроса для дальнейших тестов
        question_id_match = re.search(r'question-(\d+)', question_row.get_attribute("id") or "")
        assert question_id_match, "ID вопроса не найден"
        question_id = question_id_match.group(1)
        workflow_context.set("question_id", question_id)
        
        # Проверка что статус "На модерации"
        status_cell = question_row.locator("td.status")
        expect(status_cell).to_contain_text("На модерации")

    @pytest.mark.workflow
    def test_03_moderator_approves_question(self, moderator_page, workflow_context):
        """Шаг 3: Модератор модерирует и публикует вопрос"""
        page = moderator_page
        question_id = workflow_context.get("question_id")
        
        # Заходим на страницу модерации вопроса
        page.goto(f"https://bll.by/admin/questions/{question_id}")
        
        # Выбираем эксперта
        page.click("select#assign-expert")
        page.click("option[value='expert']")
        
        # Устанавливаем категорию
        page.click("select#question-category")
        page.click("option[value='legal']")
        
        # Публикуем вопрос
        page.click("button#publish-question")
        
        # Проверяем результат
        expect(page.locator("div.success-banner")).to_be_visible()
        expect(page.locator("div.question-status")).to_contain_text("Опубликовано")
        
        # Сохраняем информацию о статусе
        workflow_context.set("question_published", True)
        workflow_context.set("question_assigned_expert", "expert")

    @pytest.mark.workflow
    def test_04_admin_checks_published_question(self, admin_page, workflow_context):
        """Шаг 4: Админ проверяет наличие вопроса на сайте"""
        page = admin_page
        question_title = workflow_context.get("question_title")
        
        # Переходим на страницу вопросов
        page.goto("https://bll.by/questions")
        
        # Проверяем наличие опубликованного вопроса
        question_link = page.locator(f"a:has-text('{question_title}')")
        expect(question_link).to_be_visible()
        
        # Сохраняем URL вопроса
        question_link.click()
        question_url = page.url
        workflow_context.set("question_url", question_url)
        
        # Проверяем контент страницы вопроса
        question_body = workflow_context.get("question_body")
        expect(page.locator("div.question-content")).to_contain_text(question_body)

    @pytest.mark.workflow
    def test_05_expert_answers_question(self, expert_page, workflow_context):
        """Шаг 5: Эксперт отвечает на вопрос"""
        page = expert_page
        question_url = workflow_context.get("question_url")
        
        # Получаем КПО до ответа на вопрос
        page.goto("https://bll.by/expert/dashboard")
        kpo_before_text = page.locator("div.expert-kpo").text_content()
        kpo_before = float(re.search(r'(\d+\.?\d*)', kpo_before_text).group(1))
        workflow_context.set("kpo_before", kpo_before)
        
        # Переходим на страницу вопроса
        page.goto(question_url)
        
        # Создаем ответ
        timestamp = int(time.time())
        answer_text = f"Это тестовый ответ эксперта на вопрос. Создан в {timestamp}"
        
        # Заполняем форму ответа
        page.fill("textarea#answer-text", answer_text)
        page.click("button#submit-answer")
        
        # Проверяем успешную отправку ответа
        expect(page.locator("div.success-message")).to_be_visible()
        
        # Сохраняем данные ответа
        workflow_context.set("answer_text", answer_text)
        workflow_context.set("answer_timestamp", timestamp)

    @pytest.mark.workflow
    def test_06_moderator_checks_answer(self, moderator_page, workflow_context):
        """Шаг 6: Модератор проверяет ответ в админке"""
        page = moderator_page
        question_id = workflow_context.get("question_id")
        
        # Заходим в админку ответов
        page.goto("https://bll.by/admin/answers")
        
        # Поиск по ID вопроса
        page.fill("input#search-question-id", question_id)
        page.click("button#search-button")
        
        # Проверка что ответ найден
        answer_row = page.locator("tr.answer-item").first
        expect(answer_row).to_be_visible()
        
        # Сохраняем ID ответа
        answer_id_match = re.search(r'answer-(\d+)', answer_row.get_attribute("id") or "")
        assert answer_id_match, "ID ответа не найден"
        answer_id = answer_id_match.group(1)
        workflow_context.set("answer_id", answer_id)
        
        # Проверка статуса "На модерации"
        status_cell = answer_row.locator("td.status")
        expect(status_cell).to_contain_text("На модерации")

    @pytest.mark.workflow
    def test_07_moderator_approves_answer(self, moderator_page, workflow_context):
        """Шаг 7: Модератор модерирует и публикует ответ"""
        page = moderator_page
        answer_id = workflow_context.get("answer_id")
        
        # Переходим на страницу модерации ответа
        page.goto(f"https://bll.by/admin/answers/{answer_id}")
        
        # Устанавливаем оценку ответа
        page.click("select#answer-quality")
        page.click("option[value='good']")
        
        # Публикуем ответ
        page.click("button#publish-answer")
        
        # Проверяем результат
        expect(page.locator("div.success-banner")).to_be_visible()
        expect(page.locator("div.answer-status")).to_contain_text("Опубликовано")
        
        # Сохраняем информацию о статусе
        workflow_context.set("answer_published", True)

    @pytest.mark.workflow
    def test_08_admin_checks_published_answer(self, admin_page, workflow_context):
        """Шаг 8: Админ проверяет наличие ответа на сайте"""
        page = admin_page
        question_url = workflow_context.get("question_url")
        answer_text = workflow_context.get("answer_text")
        
        # Переходим на страницу вопроса
        page.goto(question_url)
        
        # Проверяем наличие опубликованного ответа
        answer_content = page.locator("div.answer-content")
        expect(answer_content).to_be_visible()
        expect(answer_content).to_contain_text(answer_text)

    @pytest.mark.workflow
    def test_09_user_likes_answer(self, user_page, workflow_context):
        """Шаг 9: Пользователь ставит лайк ответу эксперта"""
        page = user_page
        question_url = workflow_context.get("question_url")
        
        # Переходим на страницу вопроса
        page.goto(question_url)
        
        # Находим кнопку лайка у ответа
        like_button = page.locator("button.like-answer").first
        
        # Количество лайков до
        likes_before = int(page.locator("span.likes-count").first.text_content().strip())
        
        # Ставим лайк
        like_button.click()
        
        # Проверяем увеличение счетчика лайков
        page.wait_for_timeout(1000)  # Ждем обновления счетчика
        likes_after = int(page.locator("span.likes-count").first.text_content().strip())
        assert likes_after > likes_before, "Количество лайков не увеличилось"
        
        # Сохраняем информацию о лайке
        workflow_context.set("answer_liked", True)
        workflow_context.set("likes_before", likes_before)
        workflow_context.set("likes_after", likes_after)

    @pytest.mark.workflow
    def test_10_check_expert_kpo_after_like(self, expert_page, workflow_context):
        """Шаг 10: Проверяем КПО эксперта после получения лайка"""
        page = expert_page
        kpo_before = workflow_context.get("kpo_before")
        
        # Переходим в дашборд эксперта
        page.goto("https://bll.by/expert/dashboard")
        
        # Получаем актуальное значение КПО
        kpo_after_text = page.locator("div.expert-kpo").text_content()
        kpo_after = float(re.search(r'(\d+\.?\d*)', kpo_after_text).group(1))
        
        # Проверяем что КПО увеличилось
        assert kpo_after > kpo_before, f"КПО не увеличилось: было {kpo_before}, стало {kpo_after}"
        
        # Сохраняем данные о КПО
        workflow_context.set("kpo_after", kpo_after)
        workflow_context.set("kpo_increase", kpo_after - kpo_before)
