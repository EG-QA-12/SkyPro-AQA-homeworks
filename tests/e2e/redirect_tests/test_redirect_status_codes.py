"""Тесты проверки HTTP статус-кодов редиректов для URL компании BLL.

Этот модуль содержит тесты для проверки конкретных HTTP статус-кодов:
- URL без редиректа должны возвращать статус 200 (не 302)
- URL с редиректом должны возвращать статус 302 и правильный Location header

Все тесты выполняются без авторизации (без кук) для имитации 
поведения неавторизованного пользователя.
"""
from __future__ import annotations

from typing import Tuple

import pytest
import requests
import allure

# Импортируем утилиты Allure из корневой директории
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from framework.utils.reporting.allure_utils import ui_test, AllureReporter


# --- DATA --------------------------------------------------------------------

NO_REDIRECT_URLS: Tuple[str, ...] = (
    "https://bll.by/",
    "https://expert.bll.by/",
    "https://cp.bll.by/",
)

REDIRECT_URLS: Tuple[str, ...] = (
    "https://gz.bll.by/",
    "https://bonus.bll.by/",
)

TARGET_REDIRECT_PREFIX = "https://ca.bll.by/"


# --- TESTS -------------------------------------------------------------------

@ui_test(
    title="Проверка отсутствия редиректа для публичных URL",
    description="Проверяет, что публичные URL не выполняют редирект для неавторизованных пользователей",
    feature="HTTP Redirects"
)
@pytest.mark.parametrize("url", NO_REDIRECT_URLS, ids=lambda u: f"no_redirect_status[{u}]")
def test_no_redirect_status_code(http_session: requests.Session, url: str) -> None:
    """
    Проверяет, что при запросе к публичному URL нет редиректа (статус-код НЕ 302).
    
    Тест отправляет HEAD запрос к URL и проверяет, что:
    1. Статус-код НЕ равен 302 (отсутствие редиректа)
    2. Статус-код находится в диапазоне успешных ответов (200-299)
    
    Args:
        http_session (requests.Session): HTTP клиент без кук.
        url (str): Проверяемый URL.
    """
    try:
        # Используем HEAD запрос для проверки статус-кода без загрузки контента
        # allow_redirects=False гарантирует, что мы получим первичный ответ
        response = http_session.head(url, allow_redirects=False, timeout=10)
        
        # Проверяем, что НЕТ редиректа (статус-код НЕ 302)
        assert response.status_code != 302, (
            f"❌ URL {url} возвращает статус-код 302 (редирект), но ожидался статус без редиректа.\n"
            f"Фактический статус-код: {response.status_code}\n"
            f"Location header: {response.headers.get('Location', 'отсутствует')}\n"
            "Проверьте конфигурацию сервера: публичные URL не должны редиректить неавторизованных пользователей."
        )
        
        # Дополнительная проверка: статус должен быть успешным (200-299)
        assert 200 <= response.status_code < 300, (
            f"❌ URL {url} возвращает неожиданный статус-код: {response.status_code}.\n"
            "Ожидался успешный статус-код в диапазоне 200-299 для публичного URL."
        )
        
        print(f"✅ URL {url} корректно возвращает статус {response.status_code} без редиректа.")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"❌ Ошибка при выполнении запроса к {url}: {e}")


@ui_test(
    title="Проверка корректного редиректа для защищенных URL",
    description="Проверяет, что защищенные URL выполняют редирект на страницу авторизации для неавторизованных пользователей",
    feature="HTTP Redirects"
)
@pytest.mark.parametrize("url", REDIRECT_URLS, ids=lambda u: f"redirect_status[{u}]")
def test_redirect_status_code(http_session: requests.Session, url: str) -> None:
    """
    Проверяет, что при запросе к защищённому URL происходит редирект (статус-код 302).
    
    Тест отправляет HEAD запрос к URL и проверяет, что:
    1. Статус-код равен 302 (наличие редиректа)
    2. Location header содержит правильный URL редиректа (https://ca.bll.by/)
    
    Args:
        http_session (requests.Session): HTTP клиент без кук.
        url (str): Проверяемый URL.
    """
    try:
        # Используем HEAD запрос для проверки статус-кода без загрузки контента
        # allow_redirects=False гарантирует, что мы получим первичный ответ с редиректом
        response = http_session.head(url, allow_redirects=False, timeout=10)
        
        # Проверяем, что ЕСТЬ редирект (статус-код 302)
        assert response.status_code == 302, (
            f"❌ URL {url} возвращает статус-код {response.status_code}, но ожидался 302 (редирект).\n"
            f"Location header: {response.headers.get('Location', 'отсутствует')}\n"
            "Проверьте конфигурацию сервера: защищённые URL должны редиректить неавторизованных пользователей."
        )
        
        # Проверяем, что Location header содержит правильный URL редиректа
        location = response.headers.get('Location', '')
        assert location.startswith(TARGET_REDIRECT_PREFIX), (
            f"❌ URL {url} редиректит на {location}, но ожидался редирект на {TARGET_REDIRECT_PREFIX}.\n"
            f"Фактический Location header: {location}\n"
            "Проверьте настройки редиректов для защищённых URL."
        )
        
        print(f"✅ URL {url} корректно редиректит (статус 302) на {location}")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"❌ Ошибка при выполнении запроса к {url}: {e}")


@pytest.mark.parametrize("url", NO_REDIRECT_URLS + REDIRECT_URLS, ids=lambda u: f"connectivity[{u}]")
def test_url_connectivity(http_session: requests.Session, url: str) -> None:
    """
    Базовый тест доступности URL - проверяет, что сервер отвечает на запросы.
    
    Этот тест является предварительной проверкой перед основными тестами редиректов.
    Он помогает быстро выявить проблемы с сетевым соединением или недоступностью сервера.
    
    Args:
        http_session (requests.Session): HTTP клиент без кук.
        url (str): Проверяемый URL.
    """
    try:
        # Используем HEAD запрос для минимальной нагрузки на сервер
        response = http_session.head(url, allow_redirects=False, timeout=10)
        
        # Проверяем, что сервер отвечает (любой HTTP статус-код означает что сервер доступен)
        assert response.status_code is not None, (
            f"❌ Сервер {url} не отвечает на запросы."
        )
        
        # Проверяем, что статус-код находится в разумных пределах
        assert 200 <= response.status_code < 500, (
            f"❌ URL {url} возвращает серверную ошибку: {response.status_code}.\n"
            "Проверьте доступность и работоспособность сервера."
        )
        
        print(f"✅ URL {url} доступен (статус {response.status_code})")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"❌ URL {url} недоступен: {e}")
