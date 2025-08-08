#!/usr/bin/env python3
"""
Утилита для парсинга HTML

Предоставляет функции для парсинга HTML-страниц и извлечения данных.
"""

from bs4 import BeautifulSoup
import requests
from typing import List, Dict, Optional, Any
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HtmlParser:
    """
    Класс для парсинга HTML-страниц
    
    Предоставляет методы для извлечения данных из HTML.
    """
    
    def __init__(self, parser: str = "html.parser"):
        """
        Инициализация парсера
        
        Args:
            parser: Тип парсера для BeautifulSoup
        """
        self.parser = parser
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Парсит HTML-строку
        
        Args:
            html: HTML-строка для парсинга
            
        Returns:
            BeautifulSoup: Объект BeautifulSoup
        """
        return BeautifulSoup(html, self.parser)
    
    def find_element(self, soup: BeautifulSoup, selector: str) -> Optional[BeautifulSoup]:
        """
        Находит элемент по CSS-селектору
        
        Args:
            soup: Объект BeautifulSoup
            selector: CSS-селектор
            
        Returns:
            Optional[BeautifulSoup]: Найденный элемент или None
        """
        return soup.select_one(selector)
    
    def find_elements(self, soup: BeautifulSoup, selector: str) -> List[BeautifulSoup]:
        """
        Находит элементы по CSS-селектору
        
        Args:
            soup: Объект BeautifulSoup
            selector: CSS-селектор
            
        Returns:
            List[BeautifulSoup]: Список найденных элементов
        """
        return soup.select(selector)
    
    def extract_text(self, element: BeautifulSoup) -> str:
        """
        Извлекает текст из элемента
        
        Args:
            element: Элемент BeautifulSoup
            
        Returns:
            str: Извлеченный текст
        """
        return element.text.strip() if element else ""
    
    def extract_attribute(self, element: BeautifulSoup, attribute: str) -> Optional[str]:
        """
        Извлекает значение атрибута из элемента
        
        Args:
            element: Элемент BeautifulSoup
            attribute: Имя атрибута
            
        Returns:
            Optional[str]: Значение атрибута или None
        """
        return element.get(attribute) if element else None


class ModerationPanelParser(HtmlParser):
    """
    Парсер панели модерации
    
    Извлекает информацию о вопросах и ответах из панели модератора.
    Наследуется от базового класса HtmlParser.
    """
    
    def __init__(self, base_url: str = "https://expert.bll.by"):
        """
        Инициализация парсера панели модерации
        
        Args:
            base_url: Базовый URL сайта
        """
        super().__init__()
        self.base_url = base_url
        self.session = requests.Session()
        
    def _parse_date_to_timestamp(self, date_text: str) -> Optional[float]:
        """
        Преобразует строку даты из панели модерации в Unix timestamp.

        Args:
            date_text: Текстовое значение даты/времени из таблицы.

        Returns:
            Optional[float]: Unix timestamp (секунды) или None, если распарсить не удалось.
        """
        if not date_text:
            return None

        value = date_text.strip()
        value_lower = value.lower()

        # Базовая поддержка локальных форматов "сегодня HH:MM" / "вчера HH:MM"
        try:
            if "сегодня" in value_lower:
                time_part = re.search(r"(\d{1,2}:\d{2}(:\d{2})?)", value_lower)
                if time_part:
                    today = datetime.now()
                    time_fmt = "%H:%M:%S" if ":" in time_part.group(0) and len(time_part.group(0).split(":")) == 3 else "%H:%M"
                    dt = datetime.strptime(time_part.group(0), time_fmt)
                    combined = today.replace(hour=dt.hour, minute=dt.minute, second=(dt.second if time_fmt == "%H:%M:%S" else 0), microsecond=0)
                    return combined.timestamp()
            if "вчера" in value_lower:
                time_part = re.search(r"(\d{1,2}:\d{2}(:\d{2})?)", value_lower)
                if time_part:
                    yesterday = datetime.now() - timedelta(days=1)
                    time_fmt = "%H:%M:%S" if ":" in time_part.group(0) and len(time_part.group(0).split(":")) == 3 else "%H:%M"
                    dt = datetime.strptime(time_part.group(0), time_fmt)
                    combined = yesterday.replace(hour=dt.hour, minute=dt.minute, second=(dt.second if time_fmt == "%H:%M:%S" else 0), microsecond=0)
                    return combined.timestamp()
        except Exception:
            pass

        # Нормальные форматы дат
        candidates = [
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%d.%m.%Y, %H:%M:%S",
            "%d.%m.%Y, %H:%M",
        ]
        for fmt in candidates:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.timestamp()
            except ValueError:
                continue

        # Попытка выдернуть что-то похожее на yyyy-mm-dd hh:mm[:ss] или dd.mm.yyyy hh:mm[:ss]
        try:
            m = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}(:\d{2})?)|(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}(:\d{2})?)", value)
            if m:
                extracted = m.group(0)
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"]:
                    try:
                        dt = datetime.strptime(extracted, fmt)
                        return dt.timestamp()
                    except ValueError:
                        continue
        except Exception:
            pass

        return None

    def get_moderation_panel_data(self, session_cookie: str, limit: int = 5) -> List[Dict]:
        """
        Получает данные из панели модерации
        
        Args:
            session_cookie: Сессионная кука администратора
            limit: Максимальное количество записей для вывода
            
        Returns:
            List[Dict]: Список записей из панели модерации
        """
        try:
            # Настраиваем заголовки
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Отправляем запрос к панели модерации
            import time as _t
            response = self.session.get(
                f"{self.base_url}/admin/posts/new",
                cookies={"test_joint_session": session_cookie},
                headers=headers,
                timeout=5,
                params={"_": int(_t.time() * 1000)}
            )
            
            if response.status_code != 200:
                logger.error("Ошибка запроса к панели модерации: HTTP %s", response.status_code)
                return []
            
            # Парсим HTML
            soup = self.parse_html(response.text)
            
            # Находим таблицу с вопросами и ответами
            # Сначала пытаемся найти более специфичную таблицу панели модерации
            table = self.find_element(soup, 'table.posts-table')
            if not table:
                # Фолбек на общий класс, если специфичная таблица не найдена
                table = self.find_element(soup, 'table.table')
            if not table:
                logger.error("Таблица с вопросами не найдена")
                return []
            
            # Извлекаем строки таблицы
            rows = self.find_elements(table, 'tr')
            if not rows:
                logger.error("Строки таблицы не найдены")
                return []
            
            # Определяем заголовок и индексы нужных колонок
            header_cells = self.find_elements(rows[0], 'th, td') if rows else []
            header_texts = [self.extract_text(cell).lower() for cell in header_cells]

            def find_index(candidates: List[str], default_index: int) -> int:
                for idx, title in enumerate(header_texts):
                    for cand in candidates:
                        if cand in title:
                            return idx
                return default_index

            user_idx = find_index(["пользователь", "user"], 0)
            date_idx = find_index(["дата", "date"], 1)
            type_idx = find_index(["тип", "type"], 2)
            text_idx = find_index(["текст", "вопрос", "содерж"], 3)

            # Пропускаем заголовок таблицы
            data_rows = rows[1:] if len(rows) > 1 else []
            
            # Извлекаем данные из всех строк (лимит применим после сортировки)
            result = []
            for row in data_rows:
                cells = self.find_elements(row, 'td')
                if len(cells) < 3:
                    continue

                # Столбцы Пользователь, Дата, Тип по рассчитанным индексам
                user_text = self.extract_text(cells[user_idx]) if len(cells) > user_idx else ""
                date_text = self.extract_text(cells[date_idx]) if len(cells) > date_idx else ""
                type_text = self.extract_text(cells[type_idx]) if len(cells) > type_idx else ""

                # Текст вопроса/ответа: сначала пытаемся по специальному классу, затем по индексу
                text_cell = self.find_element(row, 'td.question-cell')
                if not text_cell and len(cells) > text_idx:
                    text_cell = cells[text_idx]

                text_value = self.extract_text(text_cell) if text_cell else ''
                if not text_value and text_cell:
                    # Фолбек: берем title или data-* атрибуты, если текст пуст
                    text_value = (
                        self.extract_attribute(text_cell, 'title')
                        or self.extract_attribute(text_cell, 'data-title')
                        or ''
                    )

                # Извлекаем ID из href в ячейке текста, если есть ссылка
                question_id = None
                if text_cell:
                    link_elem = self.find_element(text_cell, 'a[href]')
                    # Если ссылка не найдена в текстовой ячейке, ищем в строке
                    if not link_elem:
                        link_elem = self.find_element(row, 'a[href]')
                    if link_elem:
                        href = self.extract_attribute(link_elem, 'href') or ''
                        # Сначала пытаемся извлечь ID как сегмент пути
                        id_match = re.search(r'/(\d+)(?=[/?#]|$)', href)
                        if not id_match:
                            # Фолбек: любая последовательность цифр
                            id_match = re.search(r'(\d{5,})', href)
                        if id_match:
                            question_id = id_match.group(1)

                # Парсим дату в timestamp для последующей сортировки
                timestamp = self._parse_date_to_timestamp(date_text)

                entry = {
                    'user': user_text,
                    'date': date_text,
                    'type': type_text,
                    'text': text_value,
                    'id': question_id,
                    'timestamp': timestamp
                }
                result.append(entry)
            
            # Сортируем по времени (самые поздние сначала)
            result.sort(key=lambda e: (e.get('timestamp') or 0), reverse=True)

            # Применяем лимит после сортировки
            if isinstance(limit, int) and limit > 0:
                result = result[:limit]

            return result
            
        except Exception as e:
            logger.error("Ошибка при парсинге панели модерации: %s", e)
            return []
    
    def print_table(self, data: List[Dict]) -> None:
        """
        Выводит данные в виде таблицы
        
        Args:
            data: Список записей для вывода
        """
        if not data:
            print("Нет данных для отображения")
            return
        
        # Выводим заголовок таблицы
        print("\nПользователь\t\tДата\t\tТип\tТекст\t\tID")
        print("-" * 120)
        
        # Выводим данные
        for entry in data:
            print(f"{entry['user']}\t\t{entry['date']}\t{entry['type']}\t{entry['text'][:50]}\t\t{entry.get('id', 'Н/Д')}")
            
    def find_question_by_text(self, session_cookie: str, text_fragment: str) -> Optional[Dict]:
        """
        Ищет вопрос по фрагменту текста
        
        Args:
            session_cookie: Сессионная кука администратора
            text_fragment: Фрагмент текста для поиска
            
        Returns:
            Optional[Dict]: Найденный вопрос или None
        """
        # Получаем все записи (увеличиваем лимит для поиска)
        entries = self.get_moderation_panel_data(session_cookie, limit=20)
        
        # Ищем вопрос по фрагменту текста
        for entry in entries:
            if text_fragment.lower() in entry['text'].lower():
                return entry
                
        return None


# ==== SSO helpers (used by tests/integration/sso/test_sso_cookie_auth.py) ====
def _contains_text_case_insensitive(soup: BeautifulSoup, substrings: List[str]) -> bool:
    text = soup.get_text(" ", strip=True).lower()
    return any(s.lower() in text for s in substrings)


def check_auth_status(html: str) -> Dict[str, Any]:
    """
    Пытается определить статус авторизации по HTML.

    Возвращает структуру с ключами:
    - status: "authenticated" | "unauthenticated"
    - is_authenticated: bool
    - page_title: str
    - authenticated_markers: List[str]
    - unauthenticated_markers: List[str]
    """
    soup = BeautifulSoup(html or "", "html.parser")

    title_tag = soup.find("title")
    page_title = title_tag.get_text(strip=True) if title_tag else ""

    unauth_candidates = [
        "войти", "логин", "login", "sign in", "авторизация", "личный кабинет (вход)",
    ]
    auth_candidates = [
        "выйти", "logout", "личный кабинет", "мой профиль", "профиль", "account",
    ]

    unauthenticated_markers: List[str] = []
    authenticated_markers: List[str] = []

    # Проверяем по тексту страницы
    if _contains_text_case_insensitive(soup, unauth_candidates):
        unauthenticated_markers.append("unauth_text_marker")
    if _contains_text_case_insensitive(soup, auth_candidates):
        authenticated_markers.append("auth_text_marker")

    # Базовая эвристика: наличие формы/ссылки логина
    if soup.select_one('form[action*="login" i], a[href*="login" i]'):
        unauthenticated_markers.append("login_control_present")
    if soup.select_one('a[href*="logout" i], form[action*="logout" i]'):
        authenticated_markers.append("logout_control_present")

    is_authenticated = len(authenticated_markers) > 0 and not len(unauthenticated_markers) > 0
    status = "authenticated" if is_authenticated else "unauthenticated"

    return {
        "status": status,
        "is_authenticated": is_authenticated,
        "page_title": page_title,
        "authenticated_markers": authenticated_markers,
        "unauthenticated_markers": unauthenticated_markers,
    }


def validate_sso_response(html_without_cookies: str, html_with_cookies: str) -> Dict[str, Any]:
    """
    Валидирует смену авторизационного состояния до/после установки кук.

    Возвращает структуру:
    {
      'sso_success': bool,
      'without_cookies': {...check_auth_status},
      'with_cookies': {...check_auth_status},
      'analysis': {
         'before_auth': bool,
         'after_auth': bool,
         'cookies_changed_auth_state': bool
      }
    }
    """
    before = check_auth_status(html_without_cookies)
    after = check_auth_status(html_with_cookies)

    before_auth = before.get("is_authenticated", False)
    after_auth = after.get("is_authenticated", False)
    changed = before_auth != after_auth

    return {
        "sso_success": changed and (not before_auth) and after_auth,
        "without_cookies": before,
        "with_cookies": after,
        "analysis": {
            "before_auth": before_auth,
            "after_auth": after_auth,
            "cookies_changed_auth_state": changed,
        },
    }