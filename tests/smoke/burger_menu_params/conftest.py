"""
Burger Menu Params - Multi-Domain Parameterized Tests.

Конфигурация для тестирования burger menu на всех доменах системы.
Использует параметризацию для запуска тестов на 5 доменах одновременно.
"""

import pytest


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

    Args:
        request: pytest fixture request object

    Returns:
        tuple: (domain_name, base_url) - имя домена и его базовый URL
    """
    domain = request.param
    base_url = DOMAIN_CONFIG[domain]
    return domain, base_url


@pytest.fixture(params=['bll', 'expert', 'bonus', 'ca', 'cp'])
def domain_name(request):
    """Только имя домена для тестов."""
    return request.param


@pytest.fixture(params=list(DOMAIN_CONFIG.values()))
def domain_url(request):
    """Только URL домена для тестов."""
    return request.param
