"""
Модуль для работы с файлами cookies.

Содержит функции для поиска cookie-файлов и извлечения авторизационных cookies.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

# Константа для имени cookie, которое мы ищем.
# Выносим в константу, чтобы избежать "магических строк" в коде.
# Если имя cookie изменится, нам нужно будет поменять его только в одном месте.
AUTH_COOKIE_NAME: str = "test_joint_session"

def get_cookie_files(directory: Path, file_pattern: str) -> List[Path]:
    """
    Находит все файлы, соответствующие шаблону, в указанной директории.

    Эта функция сканирует заданную папку и возвращает список путей к файлам,
    имена которых соответствуют указанному шаблону. Это позволяет нам легко
    найти все наши cookie-файлы для параметризации тестов.

    Args:
        directory (Path): Объект Path из библиотеки pathlib, указывающий на
            директорию для поиска.
        file_pattern (str): Шаблон для поиска файлов (например, '*_cookies.json').

    Returns:
        List[Path]: Список объектов Path для каждого найденного файла.

    Raises:
        None. Если директория не найдена, возвращается пустой список.

    Example:
        >>> from pathlib import Path
        >>> files = get_cookie_files(Path('d:/Bll_tests/cookies/'), '*_cookies.json')
        >>> print(files)
        [WindowsPath('d:/Bll_tests/cookies/1_cookies.json'), ...]
    """
    if not directory.is_dir():
        # Если указанная папка не существует, возвращаем пустой список,
        # чтобы избежать ошибок и корректно отобразить пропущенные тесты.
        print(f"Предупреждение: Директория не найдена: {directory}")
        return []
    
    return list(directory.glob(file_pattern))

def parse_auth_cookie(file_path: Path, required_domain: str) -> Dict[str, Any]:
    """
    Парсит JSON-файл, находит авторизационный cookie и подготавливает его для Playwright.

    Функция открывает указанный JSON-файл, ищет в нем cookie с заданным именем (AUTH_COOKIE_NAME)
    и проверяет, что домен cookie соответствует требуемому домену (required_domain).

    Args:
        file_path (Path): Путь к JSON-файлу с cookies.
        required_domain (str): Домен, для которого предназначен cookie (например, 'ca.bll.by').

    Returns:
        Dict[str, Any]: Словарь с данными cookie в формате, подходящем для передачи в Playwright.

    Raises:
        ValueError: Если в файле не найден cookie с заданным именем или если домен cookie не совпадает с требуемым.
        json.JSONDecodeError: Если файл не является корректным JSON.
        FileNotFoundError: Если файл не найден.

    Example:
        >>> from pathlib import Path
        >>> cookie = parse_auth_cookie(Path('cookies/admin_cookies.json'), 'ca.bll.by')
        >>> print(cookie['name'])
        test_joint_session
    """
    # Открываем и читаем JSON-файл
    with file_path.open('r', encoding='utf-8') as file:
        cookies = json.load(file)
    
    # Ищем куку по имени
    for cookie in cookies:
        if cookie['name'] == AUTH_COOKIE_NAME:
            # Проверяем домен
            # Допускаем как точный домен, так и поддомен с точкой в начале
            cookie_domain: str = cookie['domain']
            # Приводим домен из куки к «нормальной» форме без начальной точки,
            # чтобы корректно сравнить его с требуемым доменом.
            normalized_cookie_domain: str = cookie_domain.lstrip('.')
            if normalized_cookie_domain != required_domain:
                raise ValueError(
                    f"Домен куки ({cookie_domain}) не соответствует требуемому: {required_domain}")
            
            # Форматируем куку для Playwright
            return {
                'name': cookie['name'],
                'value': cookie['value'],
                'domain': cookie['domain'],
                'path': cookie['path'],
                'expires': cookie.get('expiry', -1),  # Playwright использует -1 для сессионных кук
                'httpOnly': cookie['httpOnly'],
                'secure': cookie['secure'],
                'sameSite': cookie['sameSite']
            }
    
    # Если кука не найдена
    raise ValueError(f"Кука с именем '{AUTH_COOKIE_NAME}' не найдена в файле: {file_path}")