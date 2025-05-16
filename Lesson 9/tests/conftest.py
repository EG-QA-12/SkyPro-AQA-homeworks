import pytest
from db import get_db_connection

@pytest.fixture(scope='session')
def db():
    """Фикстура для подключения к БД на уровне сессии."""
    connection = get_db_connection()
    yield connection
    # Здесь можно добавить логику закрытия соединения, если требуется
