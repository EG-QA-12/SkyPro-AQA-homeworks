import pytest
from playwright.sync_api import BrowserContext, Page
from typing import Tuple

def test_isolated_context_fixture_works(isolated_context: Tuple[BrowserContext, Page]) -> None:
    """
    Тест для проверки работы фикстуры isolated_context.
    
    Этот тест проверяет, что фикстура isolated_context корректно предоставляет
    кортеж из BrowserContext и Page.
    
    Args:
        isolated_context: Кортеж из изолированного BrowserContext и Page
    """
    context, page = isolated_context
    
    # Проверяем, что context и page не None
    assert context is not None, "BrowserContext должен быть предоставлен фикстурой"
    assert page is not None, "Page должна быть предоставлена фикстурой"
    
    # Проверяем, что context является экземпляром BrowserContext
    assert isinstance(context, BrowserContext), f"context должен быть BrowserContext, но получил {type(context)}"
    
    # Проверяем, что page является экземпляром Page
    assert isinstance(page, Page), f"page должна быть Page, но получил {type(page)}"
    
    # Проверяем, что контекст и страница связаны
    assert page.context == context, "Page должна быть связана с предоставленным контекстом"
    
    print("Фикстура isolated_context работает корректно!")
