import os
import time
from typing import Dict, Optional
import requests
from framework.utils.auth_cookie_provider import AuthCookieProvider
from framework.utils.auth_utils import validate_cookie


class SmartAuthManager:
    def __init__(self):
        self.cookie_provider = AuthCookieProvider()
        self.last_valid_cookie = None
        self.last_validation_time = 0

    def get_valid_session_cookie(self, role: str = "admin") -> Optional[str]:
        current_time = time.time()
        
        # Проверяем кэшированную куку, если она есть и не устарела
        if (self.last_valid_cookie and 
            (current_time - self.last_validation_time) < 300):  # 5 мин
            if validate_cookie(self.last_valid_cookie, role):
                return self.last_valid_cookie
        
        # Получаем новую куку
        cookie = self.cookie_provider.get_auth_cookie(role)
        if not cookie:
            return None
        
        # Проверяем и кэшируем
        is_valid = validate_cookie(cookie, required_role=role)
        if is_valid:
            self.last_valid_cookie = cookie
            self.last_validation_time = current_time
            return cookie
        
        # Если кука из файла/ENV оказалась невалидной, пробуем обновить ее через API
        print(f"Кука для роли '{role}' невалидна, попытка принудительного обновления через API...")
        new_cookie = self.cookie_provider._get_cookie_via_api_login(role)
        if new_cookie and validate_cookie(new_cookie, required_role=role):
            self.last_valid_cookie = new_cookie
            self.last_validation_time = time.time()
            return new_cookie

        return None

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
