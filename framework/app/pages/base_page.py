import logging
from playwright.sync_api import Page

class BasePage:
    """
    Базовый класс для всех Page Object'ов.
    
    Содержит общую функциональность, такую как:
    - Объект страницы Playwright
    - Логгер для записи действий
    """
    
    def __init__(self, page: Page):
        """
        Инициализация базовой страницы.
        
        Args:
            page: Экземпляр страницы Playwright.
        """
        self.page = page
        self.logger = logging.getLogger(self.__class__.__name__)

    def save_cookies(self, path: str):
        """
        Сохраняет куки текущего контекста в файл.
        
        Args:
            path: Путь к файлу для сохранения куков.
        """
        cookies = self.page.context.cookies()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(cookies))
        self.logger.info(f"Куки сохранены в {path}") 