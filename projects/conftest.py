"""
Этот файл содержит конфигурацию Pytest для проекта.
Здесь регистрируются кастомные параметры командной строки.
"""


import pytest





def pytest_addoption(parser):
    """
    Регистрирует кастомный параметр командной строки --cookie-file.

    Это позволяет запускать тесты с разными наборами cookie-файлов.
    Пример: pytest --cookie-file my_cookies.json
    """
    parser.addoption(
        "--cookie-file",
        action="store",
        default=None,
        help=(
            "Укажите имя cookie-файла или 'all' для всех файлов."
            " Или список через запятую."
        ),
    )

    parser.addoption(
        "--limit",
        action="store",
        type=int,
        default=None,
        help=("Ограничить количество тестов случайной выборкой "
              "(например, --limit 10)")
    )
