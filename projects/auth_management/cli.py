"""
Модуль для работы с аргументами командной строки.
"""
import argparse
from argparse import Namespace


def parse_args() -> Namespace:
    """
    Обрабатывает аргументы командной строки.

    Returns:
        Namespace: Объект с разобранными аргументами
    """
    parser = argparse.ArgumentParser(
        description='Управление авторизацией и куками для тестов',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Создание группы взаимоисключающих аргументов
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--auth',
        action='store_true',
        help='Запустить браузер и выполнить авторизацию'
    )
    group.add_argument(
        '--use-cookies',
        action='store_true',
        help='Запустить браузер с сохранёнными куками'
    )
    group.add_argument(
        '--validate-cookies',
        action='store_true',
        help='Проверить валидность сохранённых куков без запуска браузера'
    )

    # Дополнительные опции
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Включить расширенное логирование'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Запустить браузер в безголовом режиме'
    )

    return parser.parse_args()
