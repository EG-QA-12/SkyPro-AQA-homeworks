"""
Основной менеджер авторизации для системы авторизации.

Обеспечивает централизованное управление авторизацией с кэшированием
и автоматическим обновлением кук.
"""

import time
import logging
from typing import Optional, Dict
from .cookie_provider import CookieProvider
from .auth_utils import validate_cookie

logger = logging.getLogger(__name__)


class AuthManager:
    """
    Основной менеджер авторизации.
    
    Предоставляет единую точку доступа для всех операций авторизации
    с поддержкой кэширования и автоматического обновления.
    """

    def __init__(self, cache_timeout: int = 300):
        """
        Инициализация менеджера авторизации.
        
        Args:
            cache_timeout: Время жизни кэша в секундах (по умолчанию 5 минут)
        """
        self.cache_timeout = cache_timeout
        self._cache: Dict[str, Dict] = {}
        self._cookie_provider = CookieProvider()
        
        logger.info(f"Инициализирован AuthManager с таймаутом "
                   f"кэша {cache_timeout} сек")

    def _is_cache_valid(self, role: str) -> bool:
        """
        Проверяет валидность кэшированной авторизации.
        
        Args:
            role: Роль пользователя
            
        Returns:
            True если кэш валиден, иначе False
        """
        if role not in self._cache:
            return False
        
        cached_data = self._cache[role]
        if not cached_data.get("success") or not cached_data.get("cookie"):
            return False
        
        # Проверяем время жизни кэша
        current_time = time.time()
        if (current_time - cached_data.get("timestamp", 0)) > self.cache_timeout:
            return False
        
        # Проверяем валидность куки
        return validate_cookie(cached_data["cookie"])

    def get_session_cookie(self, role: str = "admin", 
                          force_refresh: bool = False) -> Optional[str]:
        """
        Получает валидную сессионную куку для указанной роли.
        
        Args:
            role: Роль пользователя (admin, user, moderator)
            force_refresh: Принудительное обновление куки
            
        Returns:
            Значение сессионной куки или None если не удалось получить
        """
        logger.debug(f"Запрос куки для роли '{role}', "
                    f"force_refresh={force_refresh}")
        
        # Проверяем кэш
        if not force_refresh and self._is_cache_valid(role):
            logger.debug(f"Используется кэшированная кука для роли '{role}'")
            return self._cache[role]["cookie"]
        
        # Получаем новую куку через провайдер
        cookie = self._cookie_provider.get_auth_cookie(role)
        if cookie and validate_cookie(cookie):
            # Сохраняем в кэш
            self._cache[role] = {
                "cookie": cookie,
                "success": True,
                "timestamp": time.time()
            }
            logger.info(f"Кука для роли '{role}' получена и закэширована")
            return cookie
        
        # Если не удалось получить куку
        logger.error(f"Не удалось получить валидную куку для роли '{role}'")
        return None

    def clear_cache(self, role: Optional[str] = None) -> None:
        """
        Очищает кэш авторизации.
        
        Args:
            role: Конкретная роль для очистки (если None - очищает весь кэш)
        """
        if role:
            if role in self._cache:
                del self._cache[role]
                logger.debug(f"Кэш для роли '{role}' очищен")
        else:
            self._cache.clear()
            logger.debug("Весь кэш авторизации очищен")

    def validate_current_session(self, role: str = "admin") -> bool:
        """
        Проверяет валидность текущей сессии.
        
        Args:
            role: Роль пользователя
            
        Returns:
            True если сессия валидна, иначе False
        """
        session_token = self.get_session_cookie(role)
        if not session_token:
            return False
        
        return validate_cookie(session_token)


# Глобальный экземпляр менеджера для обратной совместимости
_auth_manager = AuthManager()


def get_session_cookie(role: str = "admin") -> Optional[str]:
    """
    Удобная функция для получения сессионной куки (для обратной совместимости).
    
    Args:
        role: Роль пользователя
        
    Returns:
        Значение сессионной куки или None
    """
    return _auth_manager.get_session_cookie(role)


def get_auth_cookies(role: str = "admin", domain: str = ".bll.by") -> list[dict]:
    """
    Удобная функция для получения кук в формате Playwright (для обратной 
    совместимости).
    
    Args:
        role: Роль пользователя
        domain: Домен для кук
        
    Returns:
        Список кук в формате Playwright
    """
    from framework.utils.cookie_constants import COOKIE_NAME
    
    value = get_session_cookie(role)
    if not value:
        return []
    
    return [{
        "name": COOKIE_NAME,
        "value": value,
        "domain": domain,
        "path": "/",
    }]


if __name__ == "__main__":
    # Демонстрация использования
    manager = AuthManager()
    
    # Получение куки для администратора
    admin_cookie = manager.get_session_cookie("admin")
    if admin_cookie:
        print(f"✅ Кука администратора получена: {admin_cookie[:20]}...")
    else:
        print("❌ Не удалось получить куку администратора")
