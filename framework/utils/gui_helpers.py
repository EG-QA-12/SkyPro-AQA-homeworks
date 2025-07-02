"""
Вспомогательные функции для работы с GUI интерфейсом.

Содержит утилиты для:
- Обновления статуса в интерфейсе
- Добавления сообщений в логи
- Управления состоянием кнопок
- Форматирования сообщений
"""

import tkinter as tk
from datetime import datetime
from typing import Optional, Any


class GUIHelper:
    """Помощник для работы с GUI элементами."""
    
    def __init__(self, status_label: tk.Label, status_indicator: tk.Label, 
                 result_text: tk.Text, logger: Any):
        """
        Инициализация GUI помощника.
        
        Args:
            status_label: Метка статуса
            status_indicator: Индикатор статуса
            result_text: Текстовое поле результатов
            logger: Объект логгера
        """
        self.status_label = status_label
        self.status_indicator = status_indicator
        self.result_text = result_text
        self.logger = logger
    
    def set_status(self, message: str, color: str = "green") -> None:
        """
        Установка статуса в статусной строке.
        
        Args:
            message: Сообщение статуса
            color: Цвет индикатора (green, orange, red)
        """
        self.status_label.config(text=message)
        self.status_indicator.config(foreground=color)
        
        # Обновляем интерфейс
        if hasattr(self.status_label, 'master'):
            self.status_label.master.update_idletasks()
    
    def add_result(self, message: str, level: str = "INFO") -> None:
        """
        Добавление сообщения в область результатов.
        
        Args:
            message: Текст сообщения
            level: Уровень сообщения (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.result_text.config(state=tk.NORMAL)
        
        # Определяем префикс по уровню
        prefix_map = {
            "ERROR": "❌",
            "WARNING": "⚠️", 
            "SUCCESS": "✅",
            "INFO": "ℹ️"
        }
        
        prefix = prefix_map.get(level, "ℹ️")
        formatted_message = f"[{timestamp}] {prefix} {message}\n"
        
        self.result_text.insert(tk.END, formatted_message)
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # Записываем в лог
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)


def update_buttons_state(buttons: dict, enabled: bool) -> None:
    """
    Обновление состояния группы кнопок.
    
    Args:
        buttons: Словарь кнопок {название: объект_кнопки}
        enabled: Включить (True) или отключить (False) кнопки
    """
    state = tk.NORMAL if enabled else tk.DISABLED
    
    for button_name, button in buttons.items():
        if button and hasattr(button, 'config'):
            # Кнопка "Тест без авторизации" всегда активна
            if button_name == 'test_no_auth':
                button.config(state=tk.NORMAL)
            else:
                button.config(state=state)


def setup_gui_styles(style_obj: Any) -> None:
    """
    Настройка стилей для GUI элементов.
    
    Args:
        style_obj: Объект ttk.Style для настройки стилей
    """
    style_obj.theme_use('clam')
    
    # Настройка цветовых схем для кнопок
    button_styles = {
        'Success.TButton': {'foreground': 'white', 'background': '#28a745'},
        'Warning.TButton': {'foreground': 'white', 'background': '#ffc107'},
        'Danger.TButton': {'foreground': 'white', 'background': '#dc3545'},
        'Primary.TButton': {'foreground': 'white', 'background': '#007bff'}
    }
    
    for style_name, style_config in button_styles.items():
        style_obj.configure(style_name, **style_config)


def extract_login_from_selection(selected_value: str) -> Optional[str]:
    """
    Извлечение логина из строки выбора вида "login (role)".
    
    Args:
        selected_value: Выбранное значение из combobox
        
    Returns:
        Логин пользователя или None если не удалось извлечь
    """
    if not selected_value or not selected_value.strip():
        return None
    
    try:
        if ' (' in selected_value:
            login = selected_value.split(' (')[0].strip()
            return login if login and login != "None" else None
        else:
            # Если формат не соответствует ожидаемому
            return None
    except Exception:
        return None


def format_user_info(user: dict) -> str:
    """
    Форматирование информации о пользователе для отображения.
    
    Args:
        user: Данные пользователя
        
    Returns:
        Отформатированная строка с информацией
    """
    info_lines = [
        f"Логин: {user.get('login') or user.get('username', 'N/A')}",
        f"Роль: {user.get('role', 'N/A')}",
        f"Email: {user.get('email', 'N/A')}",
        f"ID: {user.get('id', 'N/A')}"
    ]
    
    return "\n".join(info_lines)


def format_datetime(timestamp: Any) -> str:
    """
    Форматирование временной метки для отображения.
    
    Args:
        timestamp: Временная метка (timestamp, строка или None)
        
    Returns:
        Отформатированная дата или статус
    """
    if not timestamp or timestamp == 'Не авторизован':
        return 'Не авторизован'
    
    try:
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')
        elif isinstance(timestamp, str):
            return timestamp
        else:
            return str(timestamp)
    except Exception:
        return 'Неизвестно'
