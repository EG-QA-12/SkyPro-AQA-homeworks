import pytest
import sys
from typing import List

def main(args: List[str]) -> int:
    """Запускает тесты с помощью pytest в GUI-режиме.

    Args:
        args: Список аргументов командной строки для pytest.

    Returns:
        Код завершения pytest.
    
    Эта функция настраивает и запускает pytest с параметрами для видимого браузера,
    что полезно для визуальной отладки тестов. Мы используем --headed для отображения
    браузера, --browser=chromium для выбора браузера и --slowmo=500 для замедления
    действий, чтобы легче наблюдать за процессом.
    """
    test_args = ['tests/'] + args  # Добавляем директорию тестов
    return pytest.main(test_args)

if __name__ == '__main__':
    # Пример параметров: visible mode, chromium, slow motion
    gui_args = ['--headed', '--browser=chromium', '--slowmo=500']
    sys.exit(main(gui_args)) 