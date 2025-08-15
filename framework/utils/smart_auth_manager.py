import os
import time
from typing import Dict, Optional, Any
import requests
import logging
from framework.utils.auth_cookie_provider import AuthCookieProvider
from framework.utils.auth_utils import validate_cookie
from framework.utils.html_parser import fetch_csrf_tokens_from_panel
from framework.utils.enums import AnswerPublicationType
from urllib.parse import unquote
# Импортируем APIAuthManager напрямую
from framework.utils.api_auth import APIAuthManager

logger = logging.getLogger(__name__)


class SmartAuthManager:
    """
    Управляет авторизацией, проверяя валидность кук и обновляя их только при необходимости.
    """

    def __init__(self):
        """Инициализирует менеджер."""
        self.cookie_provider = AuthCookieProvider()
        self.last_valid_cookie: Optional[str] = None
        self.last_validation_time: float = 0
        self.session = requests.Session()  # Создаем сессию для менеджера

    def _perform_api_login(self, role: str) -> Optional[str]:
        """
        Выполняет API-логин и полностью обновляет сессию менеджера.
        Возвращает строковое значение `test_joint_session`.
        """
        # Эта логика перенесена из AuthCookieProvider для полного контроля над сессией
        username, password = self.cookie_provider._get_credentials_for_role(role)

        if not username or not password:
            logger.warning(f"Учетные данные для API-логина роли '{role}' не найдены.")
            return None
        
        # Используем APIAuthManager для выполнения логина
        api_manager = APIAuthManager()
        result = api_manager.login_user(username=username, password=password)

        if result and result.success and result.cookies:
            # Полностью обновляем куки в нашей основной сессии
            self.session.cookies.clear()
            for cookie_dict in result.cookies.values():
                self.session.cookies.set(
                    name=cookie_dict['name'],
                    value=cookie_dict['value'],
                    domain=cookie_dict['domain'],
                    path=cookie_dict['path']
                )
            logger.info(f"Сессия SmartAuthManager обновлена новыми куками для роли '{role}'.")
            return result.session_token

        logger.error(f"API-логин для роли '{role}' не удался в SmartAuthManager.")
        return None

    def get_valid_session_cookie(self, role: str, force_refresh: bool = False) -> Optional[str]:
        """
        Получает валидную сессионную куку, при необходимости выполняя API-логин.
        """
        current_time = time.time()

        if not force_refresh and self.last_valid_cookie:
             if (current_time - self.last_validation_time) < 300: # 5 мин
                if validate_cookie(self.last_valid_cookie, required_role=role):
                    print(f"Используем кэшированную куку для роли '{role}'")
                    return self.last_valid_cookie
        
        # Если кэш невалиден или требуется обновление, сначала пробуем из ENV/файлов
        cookie_from_storage = self.cookie_provider.get_auth_cookie(role, use_api_login=False)
        if cookie_from_storage:
             self.last_valid_cookie = cookie_from_storage
             self.last_validation_time = time.time()
             return cookie_from_storage
        
        # Если нигде нет, выполняем API-логин через собственный метод
        print(f"Кука для роли '{role}' не найдена или невалидна, попытка обновления через API...")
        api_cookie = self._perform_api_login(role)
        if api_cookie:
            self.last_valid_cookie = api_cookie
            self.last_validation_time = time.time()
            return api_cookie
        
        return None

    def submit_answer_with_retry(self, session_cookie: str, role: str, payload: Dict) -> Dict:
        """Отправляет ответ на вопрос с авто-ретраем при 401/419.

        Args:
            session_cookie: Значение авторизационной куки.
            role: Роль пользователя для реавторизации.
            payload: Данные для POST-запроса (включая CSRF-токен).

        Returns:
            Словарь с результатом операции.
        """
        base_url = "https://expert.bll.by"
        url = f"{base_url}/questions?allow-session=2"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": base_url,
            "Referer": f"{base_url}/questions/answers/{payload['question_id']}",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }

        def do_post(cookie_value: str) -> requests.Response:
            return requests.post(
                url,
                data=payload,
                headers=headers,
                cookies={"test_joint_session": cookie_value},
                timeout=15,
                allow_redirects=False,
            )

        try:
            resp = do_post(session_cookie)

            if resp.status_code in (401, 419):
                print(f"Получен статус {resp.status_code}. Попытка реавторизации для роли '{role}'...")
                new_cookie = self.get_valid_session_cookie(role=role)
                if new_cookie:
                    resp = do_post(new_cookie)

            return {
                "success": resp.status_code in (200, 301, 302),
                "status_code": resp.status_code,
                "response_text": resp.text,
            }
        except requests.RequestException as e:
            return {"success": False, "status_code": 0, "response_text": str(e)}

    def publish_answer_with_retry(self, role: str, payload: Dict) -> Dict:
        """
        Публикует (модерирует) ответ с авто-ретраем при 401/419.

        Args:
            role: Роль пользователя для реавторизации ('admin').
            payload: Данные для POST-запроса.

        Returns:
            Словарь с результатом операции.
        """
        base_url = "https://expert.bll.by"
        url = f"{base_url}/admin/posts/update"
        
        def do_post() -> requests.Response:
            # Для каждого запроса нужно получать свежие CSRF-токены, используя текущее состояние сессии
            tokens = fetch_csrf_tokens_from_panel(self.session, base_url)
            xsrf_token = unquote(tokens.get('xsrf_cookie') or '')
            form_token = tokens.get('form_token')

            if not form_token or not xsrf_token:
                raise ConnectionError("Не удалось получить CSRF-токены для публикации")
            
            local_payload = payload.copy()
            local_payload['_token'] = form_token
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': base_url,
                'Referer': f'{base_url}/admin/posts/new',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-TOKEN': form_token,
                'X-XSRF-TOKEN': xsrf_token,
            }
            # Используем self.session, который содержит актуальные куки
            return self.session.post(url, data=local_payload, headers=headers, timeout=15)

        try:
            # Первый вызов использует куки, которые уже должны быть в сессии
            resp = do_post()

            if resp.status_code in (401, 419):
                print(f"Получен статус {resp.status_code}. Попытка реавторизации для роли '{role}'...")
                # Выполняем полный API-логин, который обновляет self.session
                self._perform_api_login(role)
                # Второй вызов будет использовать уже обновленную сессию
                resp = do_post()

            return {
                "success": resp.status_code == 200 and resp.json().get("success") is True,
                "status_code": resp.status_code,
                "json_response": resp.json() if resp.status_code == 200 else None,
                "response_text": resp.text,
            }
        except (requests.RequestException, ConnectionError) as e:
            return {"success": False, "status_code": 0, "response_text": str(e)}

    def test_question_submission(self, session_cookie: str, question_text: str, role: str = "admin") -> Dict:
        """Отправляет вопрос через публичный endpoint с авто-ретраем при 401.

        Args:
            session_cookie: Значение авторизационной куки ``test_joint_session``.
            question_text: Текст вопроса для отправки.
            role: Роль пользователя для реавторизации при 401. По умолчанию ``"admin"``.

        Returns:
            Dict: Результат отправки с полями ``valid``, ``success``, ``message``, ``status_code``.
        """
        try:
            base_url = "https://expert.bll.by"
            url = f"{base_url}/questions?allow-session=2"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
                "Referer": f"{base_url}/",
                "Origin": base_url,
            }
            data = {"p": question_text}

            def do_post(cookie_value: str) -> requests.Response:
                return requests.post(
                    url,
                    data=data,
                    headers=headers,
                    cookies={"test_joint_session": cookie_value},
                    timeout=10,
                )

            resp = do_post(session_cookie)

            # Авто-ретрай на 401: реавторизация + одна повторная попытка
            if resp.status_code in (401, 419):
                print(f"Получен статус {resp.status_code}. Попытка реавторизации для роли '{role}'...")
                new_cookie = self.get_valid_session_cookie(role=role)
                if new_cookie:
                    resp = do_post(new_cookie)

            valid = resp.status_code == 200
            success = valid
            return {
                "valid": valid,
                "success": success,
                "message": resp.text[:200],
                "status_code": resp.status_code,
            }
        except Exception as exc:
            return {
                "valid": False,
                "success": False,
                "message": str(exc),
                "status_code": 0,
            }

    def _api_login_for_role(self, role: str = "admin") -> Optional[str]:
        """
        DEPRECATED: Логика перенесена в AuthCookieProvider.
        Этот метод может быть удален в будущем.
        """
        return self.cookie_provider._get_cookie_via_api_login(role)
