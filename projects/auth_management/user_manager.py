"""
Модуль для расширенного управления пользователями и авторизацией.

Включает в себя функции:
- Работа с куками и сессиями
- Авторизация через Playwright
- Массовые операции с CSV файлами
- Интеграция с базой данных
"""

import json
import os
import time
import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .database import DatabaseManager
from .config import config
from .logger import setup_logger
from framework.utils.db_helpers import update_user_in_db


logger = setup_logger(__name__)


class UserManager:
    """
    Класс для расширенного управления пользователями с интеграцией авторизации.
    
    Использует DatabaseManager для базовых операций с БД и добавляет
    функциональность авторизации через Playwright.
    """
    
    COOKIE_EXPIRY_DAYS = 7
    
    def __init__(self, db_path: str = None):
        """
        Инициализирует UserManager.
        
        Args:
            db_path: Путь к базе данных (опционально)
        """
        self.db = DatabaseManager(db_path)
        
    def add_user(
        self, 
        login: str, 
        password: str, 
        role: str = "user",
        email: Optional[str] = None,
        phone: Optional[str] = None,
        is_active: bool = True,
        last_password_change: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Добавляет пользователя в базу данных.
        
        Args:
            login: Логин пользователя
            password: Пароль пользователя
            role: Роль пользователя
            email: Email (игнорируется в текущей версии)
            phone: Телефон (игнорируется в текущей версии)
            is_active: Активность (игнорируется в текущей версии)
            last_password_change: Дата смены пароля (игнорируется в текущей версии)
            user_id: ID пользователя (игнорируется в текущей версии)
            
        Returns:
            True если пользователь добавлен успешно
        """
        return self.db.create_user(login, password, role)
        
    def get_user(self, login: Optional[str] = None, role: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Получает пользователя по логину или роли.
        
        Args:
            login: Логин пользователя
            role: Роль пользователя
            
        Returns:
            Словарь с данными пользователя или None
        """
        if login:
            return self.db.get_user(login)
        elif role:
            return self.get_user_by_role(role)
        return None
        
    def get_user_by_role(self, role: str) -> Optional[Dict[str, Any]]:
        """
        Получает первого пользователя с указанной ролью.
        
        Args:
            role: Роль пользователя
            
        Returns:
            Словарь с данными пользователя или None
        """
        query = "SELECT id, username, password_hash, role, subscription, cookie, cookie_expiration FROM users WHERE role = ? LIMIT 1"
        result = self.db.execute_query(query, (role,), fetch=True)
        
        if not result:
            return None
            
        return {
            "id": result[0][0],
            "username": result[0][1],
            "login": result[0][1],  # Дублируем для совместимости
            "password_hash": result[0][2],
            "role": result[0][3],
            "subscription": result[0][4],
            "cookie": result[0][5],
            "cookie_expiration": result[0][6]
        }
        
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Возвращает список всех пользователей.
        
        Returns:
            Список словарей с данными пользователей
        """
        query = "SELECT id, username, password_hash, role, subscription, cookie, cookie_expiration FROM users"
        results = self.db.execute_query(query, fetch=True)
        
        if not results:
            return []
            
        users = []
        for row in results:
            users.append({
                "id": row[0],
                "username": row[1],
                "login": row[1],  # Дублируем для совместимости
                "password_hash": row[2],
                "role": row[3],
                "subscription": row[4],
                "cookie": row[5],
                "cookie_expiration": row[6]
            })
        return users
        
    def verify_password(self, login: str, password: str) -> bool:
        """
        Проверяет пароль пользователя.
        
        Args:
            login: Логин пользователя
            password: Пароль для проверки
            
        Returns:
            True если пароль верен
        """
        return self.db.verify_password(login, password)
        
    def delete_user(self, login: str) -> bool:
        """
        Удаляет пользователя.
        
        Args:
            login: Логин пользователя
            
        Returns:
            True если пользователь удален успешно
        """
        return self.db.delete_user(login)
        
    def authorize_users_from_csv(self, csv_path: str, headless: bool = True, force_reauth: bool = False) -> Dict[str, Any]:
        """
        Массовая авторизация пользователей из CSV файла.
        
        Args:
            csv_path: Путь к CSV файлу
            headless: Запуск браузера в безголовом режиме
            force_reauth: Принудительная переавторизация
            
        Returns:
            Словарь с результатами авторизации
        """
        from .auth import PlaywrightAuth
        
        success = {}
        failed = []
        
        if not os.path.exists(csv_path):
            logger.error(f"CSV файл {csv_path} не найден")
            return {"success": success, "failed": failed}
            
        # Инициализируем сервис авторизации
        auth_service = PlaywrightAuth(headless=headless)
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                total_users = sum(1 for _ in reader)
                csvfile.seek(0)  # Возвращаемся в начало файла
                reader = csv.DictReader(csvfile)  # Пересоздаем reader
                
                logger.info(f"Начинаем обработку {total_users} пользователей из CSV")
                processed = 0
                
                for row in reader:
                    username = row.get('username') or row.get('login')
                    password = row.get('password')
                    role = row.get('role', 'user')
                    
                    if not username or not password:
                        logger.warning(f"Пропуск строки без логина/пароля: {row}")
                        failed.append(username or str(row))
                        continue
                        
                    processed += 1
                    logger.info(f"Обработка пользователя {processed}/{total_users}: {username}")
                    
                    # Добавляем пользователя если его нет
                    if not self.get_user(login=username):
                        self.add_user(username, password, role)
                        
                    # Проверяем, нужна ли переавторизация
                    user_data = self.get_user(login=username)
                    need_auth = force_reauth or not user_data.get('cookie') or not self.is_cookie_valid(str(user_data['id']))
                    
                    if not need_auth:
                        logger.info(f"Пользователь {username} уже авторизован, пропускаем")
                        success[username] = user_data.get('cookie_expiration', int(time.time()) + self.COOKIE_EXPIRY_DAYS * 24 * 3600)
                        continue
                    
                    # Выполняем авторизацию через браузер
                    try:
                        if force_reauth:
                            logger.info(f"Принудительная переавторизация пользователя {username}")
                            
                        auth_result = auth_service.authenticate(username, password)
                        
                        if auth_result and auth_result.get('success'):
                            # Сохраняем куки в базу данных
                            cookies = auth_result.get('cookies')
                            if cookies:
                                self.save_user_cookie(str(user_data['id']), cookies)
                                # Сохраняем куки в файл для совместимости с cookie-based авторизацией
                                self.save_cookies_to_file(username, cookies)
                                # Обновляем информацию о пользователе в БД (централизованно)
                                update_user_in_db(
                                    login=username,
                                    role=role,
                                    subscription=row.get('subscription', 'basic'),
                                    cookie_file=str(self.get_cookie_path(username))
                                )
                                success[username] = int(time.time()) + self.COOKIE_EXPIRY_DAYS * 24 * 3600
                                logger.info(f"Пользователь {username} успешно авторизован")
                            else:
                                failed.append(username)
                                logger.error(f"Авторизация прошла, но куки не получены для {username}")
                        else:
                            failed.append(username)
                            error_msg = auth_result.get('error', 'Неизвестная ошибка') if auth_result else 'Авторизация не удалась'
                            logger.error(f"Ошибка авторизации для {username}: {error_msg}")
                            
                    except Exception as e:
                        failed.append(username)
                        logger.error(f"Исключение при авторизации {username}: {e}")
                    
                    # Небольшая пауза между запросами
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"Ошибка при обработке CSV: {e}")
        finally:
            # Закрываем браузер
            try:
                auth_service.close()
            except:
                pass
            
        logger.info(f"CSV обработка завершена. Успешно: {len(success)}, Ошибок: {len(failed)}")
        return {"success": success, "failed": failed}
        
    def is_cookie_valid(self, user_id: str) -> bool:
        """
        Упрощенная проверка наличия куков пользователя.
        
        Junior QA: ИСПРАВЛЕНО! Убрали бесполезную валидацию по дате.
        Куки могут быть "валидными" по дате, но неактуальными из-за повторных логинов.
        Например, если пользователь 3 раза подряд авторизовался, но сохранил только 1-й вариант куков,
        валидация покажет ОК, а куки на самом деле уже не актуальны.
        
        Теперь просто проверяем наличие куков в БД - это единственная полезная информация.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если куки есть в БД (не проверяем дату!)
        """
        try:
            query = "SELECT cookie FROM users WHERE id = ?"
            result = self.db.execute_query(query, (user_id,), fetch=True)
            
            # Просто проверяем наличие куков в БД
            has_cookies = result and result[0][0] and len(result[0][0].strip()) > 0
            
            if has_cookies:
                logger.debug(f"Найдены куки в БД для пользователя {user_id}")
            else:
                logger.debug(f"Куки не найдены в БД для пользователя {user_id}")
                
            return has_cookies
                
        except Exception as e:
            logger.error(f"Ошибка проверки куков для пользователя {user_id}: {e}")
            return False
            
    def clear_user_cookie(self, user_id: str) -> bool:
        """
        Очищает куки пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если куки очищены успешно
        """
        try:
            query = "UPDATE users SET cookie = NULL, cookie_expiration = NULL WHERE id = ?"
            self.db.execute_query(query, (user_id,))
            logger.info(f"Куки пользователя {user_id} очищены")
            return True
        except Exception as e:
            logger.error(f"Ошибка очистки куков для пользователя {user_id}: {e}")
            return False
            
    def update_cookie_expiry(self, user_id: str) -> bool:
        """
        Обновляет время истечения куков пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если обновление успешно
        """
        try:
            from datetime import datetime, timedelta
            expiry_time = datetime.now() + timedelta(days=self.COOKIE_EXPIRY_DAYS)
            
            query = "UPDATE users SET cookie_expiration = ? WHERE id = ?"
            self.db.execute_query(query, (expiry_time.isoformat(), user_id))
            logger.info(f"Время истечения куков для пользователя {user_id} обновлено")
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления времени истечения куков для пользователя {user_id}: {e}")
            return False
            
    def load_cookies(self, user_id: str) -> Optional[str]:
        """
        Загружает куки пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Куки пользователя или None
        """
        try:
            query = "SELECT cookie FROM users WHERE id = ?"
            result = self.db.execute_query(query, (user_id,), fetch=True)
            
            if result and result[0][0]:
                return result[0][0]
            return None
        except Exception as e:
            logger.error(f"Ошибка загрузки куков для пользователя {user_id}: {e}")
            return None
            
    def save_cookies(self, user_id: str, cookies: list) -> bool:
        """
        Сохраняет куки пользователя.
        
        Args:
            user_id: ID пользователя
            cookies: Список куков
            
        Returns:
            True если сохранение успешно
        """
        try:
            import json
            from datetime import datetime, timedelta
            
            # Приводим домен куки к универсальному вида .bll.by, чтобы куки работали на всех субдоменах
            for c in cookies:
                domain = c.get("domain", "")
                if domain and not domain.startswith("."):
                    # заменяем конкретный субдомен на общий
                    c["domain"] = ".bll.by"
            
            cookies_json = json.dumps(cookies, ensure_ascii=False)
            expiry_time = datetime.now() + timedelta(days=self.COOKIE_EXPIRY_DAYS)
            
            query = "UPDATE users SET cookie = ?, cookie_expiration = ? WHERE id = ?"
            self.db.execute_query(query, (cookies_json, expiry_time.isoformat(), user_id))
            logger.info(f"Куки для пользователя {user_id} сохранены в БД")

            # Дополнительно сохраняем файл в директории data
            try:
                from .config import config  # локальный импорт, чтобы избежать циклов
                data_dir = config.COOKIES_PATH.parent
                data_dir.mkdir(exist_ok=True)
                # Получаем логин пользователя
                user = self.db.get_user(user_id) if isinstance(user_id, str) else None
                login = user.get("login") if user else str(user_id)
                file_path = data_dir / f"{login}_cookies.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, ensure_ascii=False, indent=2)
                logger.info(f"Куки сохранены в файл {file_path}")
            except Exception as fe:
                logger.warning(f"Не удалось сохранить файл кук: {fe}")
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения куков для пользователя {user_id}: {e}")
            return False
            
    def save_user_cookie(self, user_id: str, cookies: dict) -> bool:
        """
        Сохраняет куки пользователя (обертка для save_cookies).
        
        Args:
            user_id: ID пользователя
            cookies: Куки в виде словаря или списка
            
        Returns:
            True если сохранение успешно
        """
        # Преобразуем cookies в список, если это словарь
        if isinstance(cookies, dict):
            if 'cookies' in cookies:
                cookies_list = cookies['cookies']
            else:
                # Преобразуем словарь в список куков
                cookies_list = [{'name': k, 'value': v, 'domain': '.bll.by'} for k, v in cookies.items()]
        elif isinstance(cookies, list):
            cookies_list = cookies
        else:
            logger.error(f"Неподдерживаемый формат куков: {type(cookies)}")
            return False
            
        return self.save_cookies(user_id, cookies_list)
    
    def get_cookie_path(self, login: str) -> Path:
        """
        Возвращает путь к файлу куки пользователя в формате, совместимом со старой системой.
        
        Args:
            login: Логин пользователя
            
        Returns:
            Path к файлу куков пользователя
        """
        from .config import config
        return config.COOKIES_PATH.parent / f"{login}_cookies.json"
    
    def save_cookies_to_file(self, login: str, cookies: list) -> bool:
        """
        Сохраняет куки пользователя в файл и базу данных.
        
        Junior QA: Эта функция важна для совместимости со старой системой.
        Она сохраняет куки как в файл (для обратной совместимости), так и в базу данных.
        
        Args:
            login: Логин пользователя
            cookies: Список куков
            
        Returns:
            True если сохранение успешно
        """
        try:
            # Получаем пользователя
            user = self.get_user(login)
            if not user:
                logger.error(f"Пользователь {login} не найден при сохранении куков")
                return False
            
            # Сохраняем куки в файл для совместимости
            cookie_path = self.get_cookie_path(login)
            cookie_path.parent.mkdir(exist_ok=True)
            
            import json
            with open(cookie_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            
            # Сохраняем в базу данных
            success = self.save_cookies(user['id'], cookies)
            
            if success:
                logger.info(f"Куки для пользователя {login} сохранены в файл {cookie_path} и БД")
            else:
                logger.error(f"Ошибка сохранения куков для пользователя {login} в БД")
                
            return success
            
        except Exception as e:
            logger.error(f"Ошибка сохранения куков для пользователя {login}: {e}")
            return False

