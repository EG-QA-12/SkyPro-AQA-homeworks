#!/usr/bin/env python3
"""
SmartAuthManager - ПРОБНАЯ ВЕРСИЯ (ОСТАТЬСЯ СТРОГО В ПРОБНОМ РЕЖИМЕ)

Сейчас используется smart_auth_api_approach.py как рабочий файл!
ЭТОТ ФАЙЛ НЕ ИСПОЛЬЗОВАТЬ - НЕ СОВМЕСТИМ С INTEGRATION ТЕСТАМИ!
"""

# Содержимое файла заменено на ИМПОРТ ПРОБНОГО ПОДХОДА
# НЕ ИСПОЛЬЗОВАТЬ ЭТОТ ФАЙЛ ПРЯМО! Использовать smart_auth_api_approach.py

from framework.utils.smart_auth_api_approach import SmartAuthManager

# ПЕРЕНАПРАВИТЬ ВСЕ ВЫЗОВЫ НА ПРОБНЫЙ ПОДХОД

    def _get_cookie_from_files(self, role: str) -> Optional[str]:
        """
        Пытается прочитать куку из артефактов прошлых запусков.
        Используется в fallback логике get_valid_session_cookie

        Args:
            role: Роль пользователя

        Returns:
            Optional[str]: Значение куки или None
        """
        from pathlib import Path
        import json

        project_root = Path(__file__).resolve().parents[2]
        cookies_dir = project_root / "cookies"

        # Текстовый файл
        txt_path = cookies_dir / f"{role}_session.txt"
        if txt_path.exists():
            try:
                return txt_path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                logger.warning(f"Не удалось прочитать {txt_path}: {exc}")

        # JSON-файл Playwright формата
        json_path = cookies_dir / f"{role}_cookies.json"
        if json_path.exists():
            try:
                raw = json_path.read_text(encoding="utf-8")
                data = json.loads(raw)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("name") == "test_joint_session":
                            value = item.get("value")
                            if isinstance(value, str) and value:
                                return value
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning(f"Не удалось прочитать {json_path}: {exc}")

        return None

    def _perform_auth_and_get_cookie(self, role: str = "admin") -> Optional[str]:
        """
        УСТАРЕВШИЙ МЕТОД: Сохранен для обратной совместимости с тестами
        Использует надежную логику авторизации без умного ожидания

        Args:
            role: Роль пользователя

        Returns:
            Optional[str]: Значение куки или None
        """
        logger.warning(f"[DEPRECATED] _perform_auth_and_get_cookie вызван для роли {role} - используйте get_valid_session_cookie")

        # Используем надежную версию
        return self.get_valid_session_cookie(role)

    def get_valid_storage_state(self, role: str = "admin") -> Optional[Dict]:
        """
        Получает storage_state с минимальной проверкой по времени

        Args:
            role: Роль пользователя (admin, user)

        Returns:
            Optional[Dict]: Полное storage_state или None
        """
        logger.info(f"[DEBUG] get_valid_storage_state called for role: {role}")

        # Проверка наличия и актуальности storage_state
        is_too_old = self._is_storage_state_too_old(role)
        logger.info(f"[DEBUG] _is_storage_state_too_old result: {is_too_old}")

        if is_too_old:
            logger.info("Storage state старше 1 часа, обновляем через Playwright")
            result = self._perform_auth_and_get_storage_state(role)
            logger.info(f"[DEBUG] _perform_auth_and_get_storage_state result: {result is not None}")
            return result

        logger.info("Используем существующее storage_state")
        result = self._load_storage_state(role)
        logger.info(f"[DEBUG] _load_storage_state result: {result is not None}")
        return result

    def get_valid_cookies_list(self, role: str = "admin") -> Optional[List[Dict]]:
        """
        Получает список кук в формате Playwright для браузерных тестов

        ИСПРАВЛЕНИЕ: Теперь возвращает куки из ПОЛНОГО storage_state
        (включая правильную sameSite политику для headless режима)

        Args:
            role: Роль пользователя (admin, user)

        Returns:
            Optional[List[Dict]]: Список кук для context.add_cookies() или None
        """
        logger.info(f"[DEBUG] get_valid_cookies_list called for role: {role}")
        storage_state = self.get_valid_storage_state(role)
        logger.info(f"[DEBUG] storage_state result: {storage_state is not None}")

        if storage_state and "cookies" in storage_state:
            cookies_count = len(storage_state["cookies"])
            logger.info(f"[DEBUG] Found {cookies_count} cookies in FULL storage_state")

            # ДОБАВЛЕНО: Проверяем правильность sameSite для headless режима
            for cookie in storage_state["cookies"]:
                if cookie.get('name') == 'test_joint_session':
                    logger.info(f"[COOKIE_CHECK] Session cookie sameSite: {cookie.get('sameSite')}, "
                              f"secure: {cookie.get('secure')}, domain: {cookie.get('domain')}")

            return storage_state["cookies"]

        logger.warning(f"[DEBUG] No cookies found in FULL storage_state for role {role}")
        return None

    def _is_storage_state_too_old(self, role: str) -> bool:
        """
        Проверяет, старше ли куки 1 часа по времени модификации файла

        Args:
            role: Роль пользователя

        Returns:
            bool: True если куки старше 1 часа
        """
        try:
            import os
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            cookies_dir = project_root / "cookies"
            cookie_file = cookies_dir / f"{role}_cookies.json"

            if cookie_file.exists():
                mod_time = os.path.getmtime(cookie_file)
                age_hours = (time.time() - mod_time) / 3600
                logger.info(".1f")
                return age_hours > 1  # Старше 1 часа

            return True  # Если файла нет, считаем что нужно обновить

        except Exception as e:
            logger.error(f"Ошибка при проверке возраста кук: {e}")
            return True

    def _perform_auth_and_get_storage_state(self, role: str) -> Optional[Dict]:
        """
        Выполняет авторизацию через Playwright и возвращает ПОЛНЫЙ storage_state

        КЛЮЧЕВЫЕ ИСПРАВЛЕНИЯ (из sso_cookies_debug.py):
        - Использует ПОЛНЫЙ storage_state вместо простых кук
        - Упрощенная проверка авторизации (ищет профиль, а не конкретный URL)
        - Правильная sameSite политика для headless режима
        - Увеличенные таймауты

        Args:
            role: Роль пользователя

        Returns:
            Optional[Dict]: Полное storage_state или None
        """
        try:
            import nest_asyncio
            nest_asyncio.apply()

            import asyncio
            from rebrowser_playwright.async_api import async_playwright
            from config.secrets_manager import SecretsManager

            # Загружаем пользователей
            test_users = SecretsManager.load_users_from_csv()
            if not test_users:
                logger.error("Нет тестовых пользователей")
                return None

            # Находим пользователя с нужной ролью
            target_user = next(
                (user for user in test_users if user.get('role') == role), None
            )
            if not target_user:
                logger.error(f"Не найден пользователь с ролью {role}")
                return None

            logger.info(f"Выполняем Playwright авторизацию для {role}")

            # Асинхронная функция авторизации (КОПИЯ ИЗ РАБОЧЕГО СКРИПТА)
            async def _async_auth():
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        **self.get_browser_launch_args(headless=True)
                    )
                    context = await browser.new_context(
                        user_agent=(
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        ),
                        viewport={"width": 1920, "height": 1080},
                        locale="ru-RU",
                        timezone_id="Europe/Minsk",
                        ignore_https_errors=True,
                        bypass_csp=True,
                    )
                    page = await context.new_page()

                    # Anti-detection script - помогает обходить защиту от ботов
                    await page.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined
                        });
                    """)

                    # Переход на страницу входа для expert.bll.by
                    await page.goto(
                        "https://expert.bll.by/login", wait_until="domcontentloaded"
                    )

                    # Универсальное заполнение формы входа (работает для разных систем)
                    # Сначала попробуем найти email/input поля по name атрибутам
                    try:
                        # Пробуем разные варианты имен полей для логина
                        login_selectors = [
                            'input[name="lgn"]',        # ca.bll.by
                            'input[name="login"]',      # распространённое название
                            'input[name="email"]',      # email поле
                            'input[type="email"]',      # email тип
                            'input[placeholder*="логин" i]',
                            'input[placeholder*="login" i]',
                            'input[placeholder*="email" i]'
                        ]

                        login_filled = False
                        for selector in login_selectors:
                            try:
                                await page.fill(selector, target_user['login'])
                                print(f"✅ Заполнили логин: {selector}")
                                login_filled = True
                                break
                            except Exception:
                                continue

                        if not login_filled:
                            raise Exception("Не удалось найти поле для логина")

                        # Пробуем разные варианты полей для пароля
                        password_selectors = [
                            'input[name="password"]',   # распространённое название
                            'input[name="pwd"]',        # короткое название
                            'input[type="password"]',   # password тип
                            'input[placeholder*="пароль" i]',
                            'input[placeholder*="password" i]'
                        ]

                        password_filled = False
                        for selector in password_selectors:
                            try:
                                await page.fill(selector, target_user['password'])
                                print(f"✅ Заполнили пароль: {selector}")
                                password_filled = True
                                break
                            except Exception:
                                continue

                        if not password_filled:
                            raise Exception("Не удалось найти поле для пароля")

                        # Нажимаем кнопку входа
                        submit_selectors = [
                            'input[type="submit"]',
                            'button[type="submit"]',
                            'input[value*="войти" i]',
                            'input[value*="login" i]',
                            'button:has-text("войти")',
                            'button:has-text("войти")'
                        ]

                        submit_clicked = False
                        for selector in submit_selectors:
                            try:
                                await page.click(selector)
                                print(f"✅ Нажали кнопку входа: {selector}")
                                submit_clicked = True
                                break
                            except Exception:
                                continue

                        if not submit_clicked:
                            raise Exception("Не удалось найти кнопку входа")

                    except Exception as e:
                        logger.error(f"Ошибка при заполнении формы: {e}")
                        return None

                    # УМНОЕ ОЖИДАНИЕ РЕЗУЛЬТАТА АВТОРИЗАЦИИ (вместо sleep)
                    # Ждем ЛИБО изменение URL, ЛИБО появление профиля
                    try:
                        await page.wait_for_function("""
                            () => {
                                // Успех: URL изменился (редирект после авторизации)
                                if (!window.location.href.includes('/login')) {
                                    return true;
                                }
                                // Успех: профиль появился
                                if (document.querySelector('a[class*="top-nav__item top-nav__profile"]')) {
                                    return true;
                                }
                                // Продолжаем проверку (функция вернет undefined, продолжая ожидание)
                                return false;
                            }
                        """, timeout=5000)  # Максимум 5 сек

                        logger.info("[AUTH_CHECK] Auth result detected")

                    except Exception as e:
                        logger.error(f"[AUTH_TIMEOUT] Auth check timeout: {e}")
                        return None

                    # ФИНАЛЬНАЯ ПРОВЕРКА АВТОРИЗАЦИИ
                    current_url = page.url
                    logger.info(f"[AUTH_CHECK] Final URL: {current_url}")

                    # Проверяем успешную авторизацию
                    if "login" not in current_url:
                        # Подтверждаем наличие профиля
                        profile_selector = 'a[class*="top-nav__item top-nav__profile"]'
                        try:
                            profile_element = await page.wait_for_selector(
                                profile_selector, timeout=8000  # Уменьшен до 8 сек
                            )
                            if profile_element:
                                logger.info("[AUTH_SUCCESS] Profile confirmed - auth successful")
                            else:
                                logger.error("[AUTH_FAIL] Profile not found after URL change")
                                return None
                        except Exception as e:
                            logger.error(f"[AUTH_FAIL] Error confirming profile: {e}")
                            return None
                    else:
                        logger.error("[AUTH_FAIL] Still on login page - auth failed")
                        return None

                    # Сохраняем ПОЛНЫЙ storage_state (как в рабочем скрипте)
                    storage_state = await context.storage_state()
                    logger.info(f"[STORAGE] Captured full storage_state: "
                              f"{len(storage_state.get('cookies', []))} cookies")

                    await browser.close()
                    return storage_state

            # Запускаем асинхронную авторизацию
            storage_state = asyncio.run(_async_auth())

            if storage_state:
                logger.info("Успешно получено ПОЛНОЕ storage_state")

                # Сохраняем storage_state в файл
                self._save_storage_state(role, storage_state)
                return storage_state
            else:
                logger.error("Не удалось получить storage_state")
                return None

        except Exception as e:
            logger.error(f"Ошибка при авторизации: {e}")
            return None

    def _load_storage_state(self, role: str) -> Optional[Dict]:
        """
        Загружает ПОЛНЫЙ storage_state из файла storage/{role}_storage_state.json

        ИСПРАВЛЕНИЕ: Теперь загружает полный storage_state (cookies + origins + storage)
        вместо простого массива кук

        Args:
            role: Роль пользователя

        Returns:
            Optional[Dict]: Полный storage state в формате Playwright или None
        """
        try:
            import json
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            storage_dir = project_root / "storage"
            storage_file = storage_dir / f"{role}_storage_state.json"

            if storage_file.exists():
                with open(storage_file, 'r', encoding='utf-8') as f:
                    storage_state = json.load(f)

                cookies_count = len(storage_state.get('cookies', []))
                origins_count = len(storage_state.get('origins', []))

                logger.info(f"Загружен ПОЛНЫЙ storage_state из: {storage_file}")
                logger.info(f"Storage state содержит: {cookies_count} куков, {origins_count} origins")

                return storage_state

            logger.info(f"Файл storage_state не найден: {storage_file}")
            return None

        except Exception as e:
            logger.error(f"Ошибка при загрузке ПОЛНОГО storage_state: {e}")
            return None

    def _save_storage_state(self, role: str, storage_state: Dict) -> bool:
        """
        Сохраняет ПОЛНЫЙ storage_state в файл storage/{role}_storage_state.json

        ИСПРАВЛЕНИЕ: Теперь сохраняет полный storage_state (cookies + origins + storage)
        в правильную директорию storage/

        Args:
            role: Роль пользователя
            storage_state: Полный storage state для сохранения

        Returns:
            bool: True если сохранение успешно
        """
        try:
            import json
            from pathlib import Path

            project_root = Path(__file__).parent.parent.parent
            storage_dir = project_root / "storage"
            storage_dir.mkdir(exist_ok=True)

            storage_file = storage_dir / f"{role}_storage_state.json"

            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(storage_state, f, indent=2, ensure_ascii=False)

            cookies_count = len(storage_state.get('cookies', []))
            origins_count = len(storage_state.get('origins', []))

            logger.info(f"ПОЛНЫЙ storage_state сохранен: {storage_file}")
            logger.info(f"Сохранено: {cookies_count} куков, {origins_count} origins")

            return True

        except Exception as e:
            logger.error(f"Ошибка при сохранении ПОЛНОГО storage_state: {e}")
            return False

    def get_browser_launch_args(self, headless: bool = False) -> Dict:
        """
        Возвращает оптимизированные аргументы запуска браузера для скорости

        Args:
            headless: Режим работы (headless или GUI)

        Returns:
            Dict: Аргументы запуска браузера
        """
        launch_args = [
            '--disable-web-security',  # КРИТИЧНО для cross-domain cookies
            '--disable-blink-features=AutomationControlled',  # Anti-detection
            '--disable-features=VizDisplayCompositor',  # Чистая визуализация
            '--disable-dev-shm-usage',  # Экономия памяти
            '--no-first-run',  # Пропуск первого запуска
            '--disable-default-apps',  # Отключить дефолтные приложения
            '--disable-extensions',  # Отключить расширения
            '--disable-background-timer-throttling',  # Таймеры в фоне
            '--disable-backgrounding-occluded-windows',  # Фоновые окна
            '--disable-renderer-backgrounding',  # Фоновый рендеринг
        ]

        if headless:
            # Оптимизированный headless режим для скорости
            launch_args.extend([
                '--headless=new',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',  # Для headless стабильности
                '--disable-gpu',  # Отключить GPU в headless
                '--disable-software-rasterizer',  # Отключить software rasterizer
                '--disable-background-networking',  # Отключить фоновые сети
            ])

        return {
            "headless": False,  # Управляем через аргументы
            "args": launch_args,
            "slow_mo": 0,  # Без задержек
            "chromium_sandbox": not headless,
        }

    def test_question_submission(self, session_cookie: str, question_text: str) -> Dict:
        """
        Тестирует отправку вопроса для проверки валидности куки
        
        Args:
            session_cookie: Сессионная кука
            question_text: Текст вопроса для тестирования
            
        Returns:
            Dict: Результат тестирования
        """
        try:
            from requests_toolbelt import MultipartEncoder
            
            # Создаем form-data
            form_data = MultipartEncoder(
                fields={'p': question_text}
            )
            
            # Настраиваем заголовки
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                'Referer': f'{self.base_url}/',
                'Origin': self.base_url,
                'Content-Type': form_data.content_type
            }
            
            # Извлекаем значение куки из словаря если необходимо
            if isinstance(session_cookie, dict):
                cookie_value = session_cookie.get("value")
            else:
                cookie_value = session_cookie
            
            # Отправляем запрос
            response = self.session.post(
                f"{self.base_url}/questions?allow-session=2",
                data=form_data,
                cookies={"test_joint_session": cookie_value},
                headers=headers
            )
            
            # Анализируем результат
            if response.status_code == 200:
                # Упрощенная проверка: считаем успехом любой ответ 200
                logger.info(f"Получен ответ при отправке вопроса: статус {response.status_code}")
                
                # Сохраняем первые 200 символов ответа для отладки
                logger.debug(f"Текст ответа: {response.text[:200]}...")
                
                # Для отладки - печатаем информацию о запросе
                print(f"\nОтправлен запрос на URL: {self.base_url}/questions?allow-session=2")
                print(f"Заголовки запроса: {headers}")
                print(f"Текст вопроса: {question_text}")
                
                return {
                    "valid": True,
                    "success": True,  # Считаем успешной любую отправку с кодом 200
                    "status_code": response.status_code,
                    "message": "Успешная отправка"
                }
            else:
                return {
                    "valid": False,
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Ошибка при тестировании отправки вопроса: {e}")
            return {
                "valid": False,
                "success": False,
                "status_code": 0,
                "message": str(e)
            }
