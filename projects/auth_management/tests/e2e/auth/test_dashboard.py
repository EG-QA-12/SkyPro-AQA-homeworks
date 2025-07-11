"""
Пример теста с использованием аутентификации
"""
from playwright.sync_api import Page, expect

def test_authenticated_dashboard(page: Page, auth_integration):
    """
    Проверяет доступ к панели управления для аутентифицированного пользователя
    """
    # Настраиваем аутентифицированный контекст
    auth_integration.setup_authenticated_context(page.context, "admin")
    
    # Переходим на страницу
    page.goto("https://ca.bll.by/dashboard")
    
    # Проверяем элементы
    expect(page).to_have_url(contains="dashboard")
    expect(page.locator("text='Admin Panel'")).to_be_visible()

def test_unauthenticated_dashboard(page: Page):
    """
    Проверяет, что неаутентифицированный пользователь не может получить доступ к панели управления
    """
    # Переходим на страницу без аутентификации
    page.goto("https://ca.bll.by/dashboard")
    
    # Должны быть перенаправлены на страницу логина
    expect(page).to_have_url(contains="login")
    expect(page.locator("text='Please sign in'")).to_be_visible()
