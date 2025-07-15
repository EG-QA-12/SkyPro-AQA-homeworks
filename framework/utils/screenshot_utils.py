"""
Утилиты для работы со скриншотами в тестах.

Обеспечивает централизованное управление путями к скриншотам,
автоматическое создание папок и правильную организацию файлов.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def get_screenshot_path(filename: str, test_name: Optional[str] = None) -> Path:
    """
    Получает правильный путь для сохранения скриншота.
    
    Args:
        filename: Имя файла скриншота (может содержать или не содержать .png)
        test_name: Имя теста для группировки скриншотов (опционально)
        
    Returns:
        Полный путь к файлу скриншота в папке screenshots/
        
    Example:
        >>> get_screenshot_path("auth_fail_user.png")
        WindowsPath('D:/Bll_tests/screenshots/auth_fail_user.png')
        
        >>> get_screenshot_path("debug", "test_login")
        WindowsPath('D:/Bll_tests/screenshots/test_login/debug.png')
    """
    # Получаем корень проекта (3 уровня вверх от framework/utils/screenshot_utils.py)
    project_root = Path(__file__).resolve().parents[2]
    screenshots_dir = project_root / "screenshots"
    
    # Добавляем подпапку для теста если указано
    if test_name:
        screenshots_dir = screenshots_dir / test_name
    
    # Создаем директорию если не существует
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    # Добавляем расширение .png если не указано
    if not filename.endswith(('.png', '.jpg', '.jpeg')):
        filename = f"{filename}.png"
    
    screenshot_path = screenshots_dir / filename
    logger.debug(f"Сгенерирован путь к скриншоту: {screenshot_path}")
    
    return screenshot_path


def get_timestamped_screenshot_path(
    base_name: str, 
    test_name: Optional[str] = None
) -> Path:
    """
    Получает путь к скриншоту с временной меткой для уникальности.
    
    Args:
        base_name: Базовое имя файла
        test_name: Имя теста для группировки
        
    Returns:
        Путь к файлу с временной меткой
        
    Example:
        >>> get_timestamped_screenshot_path("auth_fail")
        WindowsPath('D:/Bll_tests/screenshots/auth_fail_20250715_223456.png')
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_name = f"{base_name}_{timestamp}"
    return get_screenshot_path(timestamped_name, test_name)


def save_screenshot_with_path(page, filename: str, test_name: Optional[str] = None) -> Path:
    """
    Сохраняет скриншот страницы с автоматическим определением пути.
    
    Args:
        page: Playwright Page объект
        filename: Имя файла скриншота
        test_name: Имя теста для группировки
        
    Returns:
        Путь к сохраненному файлу
        
    Raises:
        Exception: Если не удалось сохранить скриншот
    """
    screenshot_path = get_screenshot_path(filename, test_name)
    
    try:
        page.screenshot(path=str(screenshot_path))
        logger.info(f"Скриншот сохранен: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        logger.error(f"Ошибка сохранения скриншота {screenshot_path}: {e}")
        raise


def get_failure_screenshot_path(username: str, test_name: str) -> Path:
    """
    Получает путь для скриншота при ошибке авторизации.
    
    Args:
        username: Имя пользователя
        test_name: Имя теста
        
    Returns:
        Путь к файлу скриншота ошибки
    """
    failure_name = f"auth_fail_{username}"
    return get_screenshot_path(failure_name, test_name) 