# helpers/cookie_helper.py

import json
from pathlib import Path
from typing import List, Dict, Any

# Константа для имени cookie, которое мы ищем.
# Выносим в константу, чтобы избежать "магических строк" в коде.
# Если имя cookie изменится, нам нужно будет поменять его только в одном месте.
AUTH_COOKIE_NAME = "test_joint_session"

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

    Функция открывает файл, ищет в нем JSON-объект (или список объектов) с
    cookie, у которого `name` совпадает с `AUTH_COOKIE_NAME`. Затем она
    дополняет этот cookie обязательными для Playwright полями 'domain' и 'path'.

    Args:
        file_path (Path): Путь к JSON-файлу с cookie.
        required_domain (str): Домен, для которого должен быть установлен cookie
                               (например, 'ca.bll.by').

    Returns:
        Dict[str, Any]: Словарь, представляющий собой один cookie, готовый
                        для добавления в контекст браузера Playwright.

    Raises:
        FileNotFoundError: Если файл по указанному пути не найден.
        ValueError: Если авторизационный cookie не найден в файле.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"Файл с cookie не найден: {file_path}")

    with file_path.open('r', encoding='utf-8') as f:
        cookies_data = json.load(f)

    # Cookie могут храниться как один объект или как список.
    # Мы приводим все к списку, чтобы обрабатывать оба случая одинаково.
    if isinstance(cookies_data, dict):
        cookies_data = [cookies_data]

    for cookie in cookies_data:
        if cookie.get("name") == AUTH_COOKIE_NAME:
            # Нашли нужный cookie. Теперь готовим его для Playwright.
            # Помимо 'name' и 'value', Playwright требует 'domain' и 'path'.
            # Без них браузер не поймет, к какому сайту применять cookie.
            return {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": required_domain,
                "path": "/",  # Обычно cookie ставятся на весь сайт ('/').
            }

    # Если мы прошли весь цикл и не нашли нужный cookie, это ошибка.
    raise ValueError(f"Cookie с именем '{AUTH_COOKIE_NAME}' не найден в файле {file_path}")