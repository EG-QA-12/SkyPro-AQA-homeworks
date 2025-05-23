import re
from playwright.sync_api import Playwright, sync_playwright, expect
import pytest

@pytest.fixture
def browser_fixture():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        yield page
        page.close()
        browser.close()

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc/#/")
    page.get_by_placeholder("What needs to be done?").click()
    page.get_by_placeholder("What needs to be done?").fill("Задача 1")
    page.get_by_placeholder("What needs to be done?").press("Enter")
    page.get_by_placeholder("What needs to be done?").click()
    page.get_by_placeholder("What needs to be done?").fill("Задача 2")
    page.get_by_placeholder("What needs to be done?").press("Enter")
    page.get_by_placeholder("What needs to be done?").click()
    page.get_by_placeholder("What needs to be done?").fill("Задача 3")
    page.get_by_placeholder("What needs to be done?").press("Enter")
    page.get_by_text("Задача 1").click()
    page.get_by_text("Задача 1").click()
    page.get_by_role("link", name="Active").click()
    page.get_by_role("link", name="Completed").click()
    page.get_by_role("link", name="All").click()
    page.get_by_text("Задача 1").click()
    page.get_by_placeholder("What needs to be done?").click()
    page.locator("li").filter(has_text="Задача 1").get_by_label("Toggle Todo").check()
    page.get_by_text("Задача 3").click()
    page.get_by_text("Задача 3").click()
    page.get_by_text("Задача 3").click()
    page.get_by_text("Задача 3").click()
    page.get_by_role("button", name="Delete").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)