"""
Burger Menu Params - Multi-Domain Parameterized Tests.

Конфигурация для тестирования burger menu на всех доменах системы.
Использует параметризацию для запуска тестов на 5 доменах одновременно.
Поддерживает headless режим с allow-session параметром для обхода защиты от ботов.
"""

import pytest
from framework.utils.url_utils import add_allow_session_param


# Импортируем глобальную переменную headless режима из корневого conftest.py
try:
    from conftest import IS_HEADLESS_MODE
except ImportError:
    IS_HEADLESS_MODE = False


# Конфигурация доменов для multi-domain тестирования
DOMAIN_CONFIG = {
    'bll': 'https://bll.by',              # Основной сайт
    'expert': 'https://expert.bll.by',    # Экспертная система
    'bonus': 'https://bonus.bll.by',      # Бонусная система
    'ca': 'https://ca.bll.by/',           # Контрагенты
    'cp': 'https://cp.bll.by'             # Инструменты
}


@pytest.fixture(params=['bll', 'expert', 'bonus', 'ca', 'cp'],
                ids=['Main Site (bll.by)', 'Expert System', 'Bonus System', 'CA System', 'CP System'])
def multi_domain_context(request):
    """
    Параметризованный fixture для multi-domain тестирования.

    Добавляет allow-session параметр для обхода защиты от ботов в headless режиме.

    Args:
        request: pytest fixture request object

    Returns:
        tuple: (domain_name, base_url) - имя домена и его базовый URL
    """
    domain = request.param
    base_url = DOMAIN_CONFIG[domain]

    # Добавляем параметр allow-session для headless режима
    if IS_HEADLESS_MODE:
        base_url = add_allow_session_param(base_url, headless=True)

    return domain, base_url


@pytest.fixture(params=['bll', 'expert', 'bonus', 'ca', 'cp'])
def domain_name(request):
    """Только имя домена для тестов."""
    return request.param


@pytest.fixture(params=list(DOMAIN_CONFIG.values()))
def domain_url(request):
    """Только URL домена для тестов."""
    base_url = request.param
    # Добавляем параметр allow-session для headless режима
    if IS_HEADLESS_MODE:
        base_url = add_allow_session_param(base_url, headless=True)
    return base_url
