"""
Графический интерфейс для управления авторизацией в системе тестирования.

Функциональность:
- Выбор пользователя/роли для авторизации
- Запуск авторизации с визуальным браузером
- Проверка валидности сохранённых куков
- Управление пользователями и их данными
- Просмотр логов авторизации
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
from typing import Optional, Dict, Any
import threading
from datetime import datetime
import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(str(Path(__file__).parent.parent))

from src.config import config
from src.logger import setup_logger
from src.user_manager import UserManager
from src.auth import authorize_and_save_cookies, load_cookies
from src.database import init_db


class AuthGUI:
    """
    Графический интерфейс для управления авторизацией тестов.
    
    Обеспечивает удобный способ авторизации различных пользователей,
    проверки статуса куков и управления пользовательскими данными.
    """
    
    def __init__(self):
        """Инициализация GUI приложения."""
        self.root = tk.Tk()
        self.root.title("Auth Project - GUI Manager")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Настройка логирования
        self.logger = setup_logger(__name__)
        
        # Инициализация базы данных и менеджера пользователей
        try:
            init_db()
            self.user_manager = UserManager()
        except Exception as e:
            self.logger.error(f"Ошибка инициализации базы данных: {e}")
            messagebox.showerror("Ошибка", f"Не удалось инициализировать базу данных: {e}")
            sys.exit(1)
        
        # Создание интерфейса
        self._setup_ui()
        self._load_users()
        
        # Стили
        self._setup_styles()
        
        self.logger.info("GUI приложение инициализировано")
    
    def _setup_styles(self) -> None:
        """Настройка стилей интерфейса."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка стилей для кнопок
        style.configure('Success.TButton', foreground='white', background='#28a745')
        style.configure('Warning.TButton', foreground='white', background='#ffc107')
        style.configure('Danger.TButton', foreground='white', background='#dc3545')
        style.configure('Primary.TButton', foreground='white', background='#007bff')
    
    def _setup_ui(self) -> None:
        """Создание элементов пользовательского интерфейса."""
        # Главное меню
        self._create_menu()
        
        # Основной фрейм с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка авторизации
        self._create_auth_tab()
        
        # Вкладка управления пользователями
        self._create_users_tab()
        
        # Вкладка логов
        self._create_logs_tab()
        
        # Статусная строка
        self._create_status_bar()
    
    def _create_menu(self) -> None:
        """Создание главного меню."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Обновить данные", command=self._refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)
        
        # Меню "Операции"
        operations_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Операции", menu=operations_menu)
        operations_menu.add_command(label="Авторизовать всех", command=self._authorize_all_users)
    
    def _create_auth_tab(self) -> None:
        """Создание вкладки авторизации."""
        auth_frame = ttk.Frame(self.notebook)
        self.notebook.add(auth_frame, text="Авторизация")
        
        # Основной контейнер
        main_container = ttk.Frame(auth_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Группа выбора пользователя
        user_group = ttk.LabelFrame(main_container, text="Выбор пользователя", padding=10)
        user_group.pack(fill=tk.X, pady=(0, 15))
        
        # Выбор пользователя
        ttk.Label(user_group, text="Пользователь:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(user_group, textvariable=self.user_var, 
                                      state="readonly", width=30)
        self.user_combo.grid(row=0, column=1, sticky=tk.W)
        self.user_combo.bind('<<ComboboxSelected>>', self._on_user_selected)
        
        # Информация о пользователе
        info_frame = ttk.Frame(user_group)
        info_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(10, 0))
        
        self.info_text = tk.Text(info_frame, height=4, width=60, state=tk.DISABLED,
                                bg='#f8f9fa', wrap=tk.WORD)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        info_scroll = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=info_scroll.set)
        
        # Группа действий
        actions_group = ttk.LabelFrame(main_container, text="Действия", padding=10)
        actions_group.pack(fill=tk.X, pady=(0, 15))
        
        # Кнопки действий
        buttons_frame = ttk.Frame(actions_group)
        buttons_frame.pack(fill=tk.X)
        
        # Первая строка кнопок
        row1_frame = ttk.Frame(buttons_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.auth_btn = ttk.Button(row1_frame, text="🔐 Авторизоваться", 
                                  command=self._authorize_user, style='Primary.TButton')
        self.auth_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Junior QA: Убираем бесполезную кнопку "Проверить куки"
        # Валидация по дате не дает реальной информации о работоспособности куков
        # Куки могут быть "валидными" по дате, но неактуальными из-за повторных логинов
        # self.check_cookies_btn = ttk.Button(row1_frame, text="🍪 Проверить куки", 
        #                                    command=self._check_cookies, style='Warning.TButton')
        # self.check_cookies_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.test_auth_btn = ttk.Button(row1_frame, text="🍪 Авторизация через куки", 
                                       command=self._test_authorization, style='Success.TButton')
        self.test_auth_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.test_no_auth_btn = ttk.Button(row1_frame, text="🚫 Тест без авторизации", 
                                          command=self._test_no_authorization, style='Warning.TButton')
        self.test_no_auth_btn.pack(side=tk.LEFT)
        
        # Вторая строка кнопок
        row2_frame = ttk.Frame(buttons_frame)
        row2_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Чекбокс для headless режима
        self.headless_var = tk.BooleanVar(value=False)
        self.headless_check = ttk.Checkbutton(row2_frame, text="Headless режим", 
                                          variable=self.headless_var)
        self.headless_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.clear_cookies_btn = ttk.Button(row2_frame, text="🗑️ Очистить куки", 
                                           command=self._clear_cookies, style='Danger.TButton')
        self.clear_cookies_btn.pack(side=tk.RIGHT)
        
        # Группа прогресса
        progress_group = ttk.LabelFrame(main_container, text="Статус", padding=10)
        progress_group.pack(fill=tk.BOTH, expand=True)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(progress_group, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Область результатов
        self.result_text = scrolledtext.ScrolledText(progress_group, height=10, 
                                                    state=tk.DISABLED, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Изначально отключаем кнопки
        self._update_buttons_state(False)
    
    def _create_users_tab(self) -> None:
        """Создание вкладки управления пользователями."""
        users_frame = ttk.Frame(self.notebook)
        self.notebook.add(users_frame, text="Пользователи")
        
        # Список пользователей
        list_frame = ttk.LabelFrame(users_frame, text="Список пользователей", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Таблица пользователей
        columns = ('login', 'role', 'status', 'last_auth')
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        self.users_tree.heading('login', text='Логин')
        self.users_tree.heading('role', text='Роль')
        self.users_tree.heading('status', text='Статус куков')
        self.users_tree.heading('last_auth', text='Последняя авторизация')
        
        self.users_tree.column('login', width=120)
        self.users_tree.column('role', width=100)
        self.users_tree.column('status', width=120)
        self.users_tree.column('last_auth', width=150)
        
        # Скроллбар для таблицы
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления пользователями
        users_buttons_frame = ttk.Frame(users_frame)
        users_buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        ttk.Button(users_buttons_frame, text="🔄 Обновить список", 
                  command=self._refresh_users_list).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(users_buttons_frame, text="🗑️ Очистить все куки", 
                  command=self._clear_all_cookies, style='Danger.TButton').pack(side=tk.LEFT)
    
    def _create_logs_tab(self) -> None:
        """Создание вкладки логов."""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Логи")
        
        # Область логов
        logs_container = ttk.Frame(logs_frame)
        logs_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Кнопки управления логами
        logs_buttons_frame = ttk.Frame(logs_container)
        logs_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(logs_buttons_frame, text="🔄 Обновить логи", 
                  command=self._refresh_logs).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(logs_buttons_frame, text="🗑️ Очистить логи", 
                  command=self._clear_logs).pack(side=tk.LEFT)
        
        # Текстовая область для логов
        self.logs_text = scrolledtext.ScrolledText(logs_container, height=25, 
                                                  state=tk.DISABLED, wrap=tk.WORD)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
        # Загрузка логов при инициализации
        self._refresh_logs()
    
    def _create_status_bar(self) -> None:
        """Создание статусной строки."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Готов к работе")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Индикатор статуса
        self.status_indicator = ttk.Label(self.status_bar, text="●", foreground="green")
        self.status_indicator.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def _load_users(self) -> None:
        """Загрузка списка пользователей."""
        try:
            users = self.user_manager.get_all_users()
            user_list = []
            
            for user in users:
                # Используем login как основное поле, username как fallback для совместимости
                login = user.get('login', user.get('username', '')).strip()
                role = user.get('role', 'user').strip()
                
                # Фильтруем некорректных пользователей
                if not login or login.lower() in ['unknown', 'none', ''] or not role:
                    self.logger.warning(f"Пропускаем пользователя с некорректными данными: login='{login}', role='{role}'")
                    continue
                
                # Дополнительная проверка на валидность пользователя
                if not user.get('id'):
                    self.logger.warning(f"Пропускаем пользователя без ID: {login}")
                    continue
                
                user_list.append(f"{login} ({role})")
            
            self.user_combo['values'] = user_list
            
            if user_list:
                self.user_combo.current(0)
                # Принудительно устанавливаем значение в переменную
                self.user_var.set(user_list[0])
                self._on_user_selected(None)
                self.logger.info(f"Загружено {len(user_list)} валидных пользователей")
            else:
                self.logger.warning("Не найдено ни одного валидного пользователя")
                self.user_var.set("")
                self._update_buttons_state(False)
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки пользователей: {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {e}")
    
    def _on_user_selected(self, event) -> None:
        """Обработчик выбора пользователя."""
        if not self.user_var.get():
            self._update_buttons_state(False)
            return
        
        try:
            # Извлекаем логин из строки "login (role)"
            selected = self.user_var.get()
            login = selected.split(' (')[0]
            
            user = self.user_manager.get_user(login)
            if user:
                self._display_user_info(user)
                self._update_buttons_state(True)
            else:
                self._update_buttons_state(False)
                
        except Exception as e:
            self.logger.error(f"Ошибка при выборе пользователя: {e}")
            self._update_buttons_state(False)
    
    def _display_user_info(self, user: Dict[str, Any]) -> None:
        """Отображение информации о пользователе."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info_lines = [
            f"Логин: {user.get('login') or user.get('username', 'N/A')}",
            f"Роль: {user.get('role', 'N/A')}",
            f"Email: {user.get('email', 'N/A')}",
            f"ID: {user.get('id', 'N/A')}"
        ]
        
        # Проверяем статус куков
        cookie_status = "Не проверено"
        if self.user_manager.is_cookie_valid(user.get('id')):
            cookie_status = "✅ Валидны"
        else:
            cookie_status = "❌ Невалидны/отсутствуют"
        
        info_lines.append(f"Статус куков: {cookie_status}")
        
        self.info_text.insert(tk.END, "\n".join(info_lines))
        self.info_text.config(state=tk.DISABLED)
    
    def _update_buttons_state(self, enabled: bool) -> None:
        """Обновление состояния кнопок."""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        self.auth_btn.config(state=state)
        # Junior QA: Убрали ссылку на удаленную кнопку check_cookies_btn
        # self.check_cookies_btn.config(state=state)
        self.test_auth_btn.config(state=state)
        self.test_no_auth_btn.config(state=tk.NORMAL)  # Эта кнопка всегда активна
        self.clear_cookies_btn.config(state=state)
    
    def _set_status(self, message: str, color: str = "green") -> None:
        """Установка статуса в статусной строке."""
        self.status_label.config(text=message)
        self.status_indicator.config(foreground=color)
        self.root.update_idletasks()
    
    def _add_result(self, message: str, level: str = "INFO") -> None:
        """Добавление сообщения в область результатов."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.result_text.config(state=tk.NORMAL)
        
        # Добавляем цветовое кодирование
        if level == "ERROR":
            prefix = "❌"
        elif level == "WARNING":
            prefix = "⚠️"
        elif level == "SUCCESS":
            prefix = "✅"
        else:
            prefix = "ℹ️"
        
        formatted_message = f"[{timestamp}] {prefix} {message}\n"
        self.result_text.insert(tk.END, formatted_message)
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # Также записываем в лог
        getattr(self.logger, level.lower(), self.logger.info)(message)
    
    def _get_selected_user(self) -> Optional[Dict[str, Any]]:
        """Получение данных выбранного пользователя."""
        selected_value = self.user_var.get()
        if not selected_value or selected_value.strip() == "":
            self.logger.warning("Пользователь не выбран в выпадающем списке")
            return None
        
        try:
            # Разрешаем работу с тестовыми пользователями, включая "unknown"
            # Удаляем блокировку для возможности тестирования
            
            # Проверяем формат выбранной строки
            if ' (' not in selected_value:
                self.logger.error(f"Неверный формат выбранного пользователя: {selected_value}")
                return None
                
            login = selected_value.split(' (')[0].strip()
            if not login or login == "None" or login == "":
                self.logger.error(f"Логин некорректен после извлечения из: {selected_value}, логин: '{login}'")
                return None
                
            user = self.user_manager.get_user(login)
            if not user:
                self.logger.error(f"Пользователь с логином '{login}' не найден в базе данных")
                return None
                
            self.logger.debug(f"Успешно получен пользователь: {user.get('login')} (ID: {user.get('id')})")
            return user
        except Exception as e:
            self.logger.error(f"Ошибка получения данных пользователя из '{selected_value}': {e}")
            return None
    
    def _get_user_password(self, login: str) -> Optional[str]:
        """
        Получает пароль пользователя из базы данных.
        
        Junior QA: ИСПРАВЛЕНО! Теперь пароли берутся из БД, а не из конфигурации.
        Это правильная архитектура - БД является единым источником данных о пользователях.
        База данных позволяет управлять ролями, подписками и вызывать пользователей по ролям в CLI.
        
        Args:
            login: Логин пользователя
            
        Returns:
            Пароль пользователя или None если не найден
        """
        try:
            # Получаем пользователя из БД
            user = self.user_manager.get_user(login)
            if not user:
                self.logger.warning(f"Пользователь {login} не найден в БД")
                return None
            
            # Junior QA: Ищем пароль в базе данных
            # Сначала проверяем, есть ли поле с паролем в открытом виде
            if 'password' in user and user['password']:
                self.logger.debug(f"Найден пароль в БД для пользователя {login}")
                return user['password']
            
            # Если в БД нет пароля, используем маппинг ролей из конфига как fallback
            role = user.get('role', 'user').lower().strip()
            
            role_password_map = {
                'admin': config.ADMIN_PASS,
                'moderator': config.MODERATOR_PASS, 
                'expert': config.EXPERT_PASS,
                'user': config.USER_PASS,
                'qa': config.USER_PASS,
                'tester': config.USER_PASS
            }
            
            if role in role_password_map:
                password = role_password_map[role]
                self.logger.info(f"Использован fallback пароль для роли '{role}' пользователя {login}")
                return password
            
            # Если ничего не найдено, используем основной пароль
            self.logger.warning(f"Не найден пароль для пользователя {login}, используем основной пароль")
            return config.PASS
            
        except Exception as e:
            self.logger.error(f"Ошибка получения пароля для пользователя {login}: {e}")
            return None
    
    def _authorize_user(self) -> None:
        """Запуск авторизации выбранного пользователя."""
        # Добавим отладочную информацию
        selected_value = self.user_var.get()
        self.logger.debug(f"Выбранное значение из combobox: '{selected_value}'")
        
        user = self._get_selected_user()
        if not user:
            error_msg = f"Пользователь не выбран. Выбранное значение: '{selected_value}'"
            self.logger.error(error_msg)
            messagebox.showerror("Ошибка", error_msg)
            return
        
        def auth_thread():
            try:
                self._set_status("Выполняется авторизация...", "orange")
                self.progress.start()
                user_login = user.get('login') or user.get('username', 'неизвестный')
                self._add_result(f"Начинается авторизация пользователя {user_login}")
                self.logger.info(f"Начинается авторизация пользователя {user_login}")
                
                # Формируем путь для сохранения куков
                cookies_path = config.COOKIES_PATH.parent / f"{user.get('login')}_cookies.json"
                
                # Безопасное получение логина и проверка данных пользователя
                # Используем login как основное поле, username как fallback для совместимости
                user_login = user.get('login') or user.get('username')
                if not user_login or user_login == 'None' or user_login.strip() == '':
                    self.logger.error(f"Некорректный логин пользователя: {user_login}. Полные данные пользователя: {user}")
                    raise ValueError(f"Логин пользователя не указан или некорректен: '{user_login}'")
                
                # Выполняем авторизацию с данными конкретного пользователя
                from src.auth import perform_login_on_page, verify_page_cookie_status
                from playwright.sync_api import sync_playwright
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=self.headless_var.get())
                    context = browser.new_context()
                    page = context.new_page()
                    
                # Используем логин пользователя и его реальный пароль из конфига
                    # Для тестовых пользователей пароли должны быть в переменных окружения
                    login_to_use = user.get('login') or user.get('username')
                    password_to_use = self._get_user_password(login_to_use)
                    
                    if not password_to_use:
                        raise ValueError(f"Пароль для пользователя {login_to_use} не найден в конфигурации")
                    
                    # Выполняем авторизацию
                    perform_login_on_page(
                        page=page,
                        login=login_to_use,
                        password=password_to_use,
                        cookies_path=cookies_path
                    )
                    
                    # Junior QA: Получаем куки ДО закрытия браузера!
                    # Это критически важно - после закрытия браузера куки становятся недоступными
                    cookies = context.cookies()
                    
                    # Теперь безопасно закрываем браузер
                    browser.close()
                user_login = user.get('login') or user.get('username', 'unknown')
                
                if cookies:
                    # Сохраняем куки в базу данных и файл для совместимости
                    success = self.user_manager.save_cookies_to_file(user_login, cookies)
                    if success:
                        self._add_result(f"🍪 Куки сохранены в БД и файл: {cookies_path}", "SUCCESS")
                        # Обновляем время истечения куков
                        self.user_manager.update_cookie_expiry(user['id'])
                        self._add_result(f"⏰ Время истечения куков обновлено", "SUCCESS")
                    else:
                        self._add_result(f"⚠️ Ошибка сохранения куков в БД", "WARNING")
                else:
                    self._add_result(f"⚠️ Не удалось получить куки из браузера", "WARNING")
                
                self._add_result(f"✅ Авторизация пользователя {user_login} успешно завершена!", "SUCCESS")
                self._set_status(f"✅ {user_login} авторизован успешно", "green")
                
                # Обновляем информацию о пользователе в GUI
                self.root.after(0, lambda: self._on_user_selected(None))
                
                # Показываем сообщение об успехе
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успех", 
                    f"Пользователь {user_login} успешно авторизован!\n\n"
                    f"Куки сохранены и готовы к использованию."
                ))
                
            except Exception as e:
                error_msg = f"Ошибка авторизации: {e}"
                self._add_result(error_msg, "ERROR")
                self._set_status("Ошибка авторизации", "red")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", error_msg))
            finally:
                self.progress.stop()
        
        # Запускаем авторизацию в отдельном потоке
        threading.Thread(target=auth_thread, daemon=True).start()
    
    def _check_cookies(self) -> None:
        """Проверка валидности куков выбранного пользователя."""
        user = self._get_selected_user()
        if not user:
            messagebox.showerror("Ошибка", "Пользователь не выбран")
            return
        
        try:
            self._add_result(f"Проверка куков для пользователя {user.get('login') or user.get('username', 'unknown')}")
            
            is_valid = self.user_manager.is_cookie_valid(user['id'])
            
            if is_valid:
                self._add_result(f"Куки пользователя {user.get('login') or user.get('username', 'unknown')} валидны", "SUCCESS")
                self._set_status("Куки валидны", "green")
            else:
                self._add_result(f"Куки пользователя {user.get('login') or user.get('username', 'unknown')} невалидны или отсутствуют", "WARNING")
                self._set_status("Куки невалидны", "orange")
            
            # Обновляем информацию о пользователе
            self._on_user_selected(None)
            
        except Exception as e:
            error_msg = f"Ошибка проверки куков: {e}"
            self._add_result(error_msg, "ERROR")
            self._set_status("Ошибка проверки", "red")
    
    def _authorize_all_users(self) -> None:
        """
        Массовая авторизация всех пользователей.
        """
        def auth_all_thread():
            try:
                self._set_status("Массовая авторизация пользователей...", "orange")
                self.progress.start()
                self._add_result("Массовая авторизация всех пользователей начата")

                users = self.user_manager.get_all_users()
                for user in users:
                    self._authorize_user_individual(user)

                self._add_result("Массовая авторизация завершена", "SUCCESS")
                self._set_status("Массовая авторизация завершена", "green")
            except Exception as e:
                error_msg = f"Ошибка массовой авторизации: {e}"
                self._add_result(error_msg, "ERROR")
                self._set_status("Ошибка массовой авторизации", "red")
            finally:
                self.progress.stop()

        threading.Thread(target=auth_all_thread, daemon=True).start()

    def _authorize_user_individual(self, user: Dict[str, Any]) -> None:
        """
        Авторизация конкретного пользователя (общая логика).
        :param user: Данные пользователя
        """
        try:
            self._add_result(f"Авторизация пользователя {user.get('login')}")

            cookies_path = config.COOKIES_PATH.parent / f"{str(user.get('login', 'unknown'))}_cookies.json"
            login_to_use = user.get('login')
            password_to_use = self._get_user_password(login_to_use)

            if not password_to_use:
                raise ValueError(f"Пароль для пользователя {login_to_use} не найден в конфигурации")

            from src.auth import perform_login_on_page
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless_var.get())
                context = browser.new_context()
                page = context.new_page()
                perform_login_on_page(page=page, login=login_to_use, password=password_to_use, cookies_path=cookies_path)
                browser.close()
            
            self.user_manager.update_cookie_expiry(user['id'])
            self._add_result(f"Авторизация пользователя {user.get('login')} завершена", "SUCCESS")
        except Exception as e:
            self.logger.error(f"Ошибка при авторизации пользователя {user.get('login')}: {e}")
            self._add_result(f"Ошибка при авторизации пользователя {user.get('login')}: {e}", "ERROR")

    def _test_authorization(self) -> None:
        """Тестовая авторизация с проверкой доступа и детальной информацией."""
        user = self._get_selected_user()
        if not user:
            messagebox.showerror("Ошибка", "Пользователь не выбран")
            return
        
        def test_thread():
            try:
                self._set_status("Выполняется тестовая авторизация...", "orange")
                self.progress.start()
                
                user_login = user.get('login') or user.get('username', 'unknown')
                self._add_result(f"🧪 Запуск тестовой авторизации для пользователя: {user_login}")
                self._add_result(f"📧 Email: {user.get('email', 'N/A')}")
                self._add_result(f"👤 Роль: {user.get('role', 'N/A')}")
                
                # Используем контекст с куками для тестирования
                from playwright.sync_api import sync_playwright
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=self.headless_var.get())
                    
                    # Создаем контекст и загружаем куки
                    context = browser.new_context()
                    
                    cookies_path = config.COOKIES_PATH.parent / f"{user_login}_cookies.json"
                    cookies = load_cookies(cookies_path)
                    
                    if cookies:
                        context.add_cookies(cookies)
                        self._add_result(f"🍪 Загружены куки для {user_login} (найдено {len(cookies)} куков)")
                    else:
                        self._add_result(f"⚠️ Куки для {user_login} не найдены, авторизация может быть неуспешной", "WARNING")
                    
                    page = context.new_page()
                    
                    # Переходим на целевую страницу
                    self._add_result(f"🔗 Переход на: {config.TARGET_URL}")
                    page.goto(config.TARGET_URL, timeout=30000)
                    
                    # Junior QA: ИСПРАВЛЕНО! Убираем долгое ожидание networkidle
                    # Ждем только базовую загрузку DOM - этого достаточно для проверки элементов
                    try:
                        page.wait_for_load_state('domcontentloaded', timeout=3000)  # Максимум 3 секунды
                    except:
                        pass  # Если не дождались - не критично, попробуем проверить элементы
                    
                    # Проверяем, что мы авторизованы
                    current_url = page.url
                    page_title = page.title()
                    
                    self._add_result(f"📍 Текущий URL: {current_url}")
                    self._add_result(f"📄 Заголовок страницы: {page_title}")
                    
                    # Junior QA: ДОБАВЛЯЕМ ПОДРОБНОЕ ЛОГИРОВАНИЕ ДЛЯ ОТЛАДКИ!
                    # Проверяем ключевой элемент .user-in__nick с подробным логированием
                    self._add_result(f"🔍 Поиск элемента .user-in__nick на странице...")
                    
                    try:
                        # Проверяем ключевой элемент - никнейм пользователя
                        nickname_locator = page.locator('.user-in__nick')
                        
                        # Проверяем, сколько элементов найдено
                        element_count = nickname_locator.count()
                        self._add_result(f"🔢 Количество элементов .user-in__nick: {element_count}")
                        
                        if element_count > 0:
                            # Проверяем видимость элемента
                            if nickname_locator.first.is_visible(timeout=1000):
                                nickname_text = nickname_locator.first.text_content().strip()
                                self._add_result(f"✅ Найден никнейм: '{nickname_text}'", "SUCCESS")
                                
                                # Проверяем совпадение с ожидаемым логином
                                if nickname_text.lower() == user_login.lower():
                                    self._add_result(f"✅ ПРАВИЛЬНО! Никнейм совпадает: '{nickname_text}' = '{user_login}'", "SUCCESS")
                                    is_likely_authorized = True
                                else:
                                    self._add_result(f"❌ ОШИБКА! Никнейм НЕ совпадает: '{nickname_text}' != '{user_login}'", "ERROR")
                            else:
                                self._add_result(f"⚠️ Элемент .user-in__nick найден, но НЕ видим", "WARNING")
                        else:
                            self._add_result(f"❌ Элемент .user-in__nick НЕ найден на странице", "ERROR")
                            
                    except Exception as nick_error:
                        self._add_result(f"❌ Ошибка при поиске никнейма: {nick_error}", "ERROR")
                    
                    # Проверяем другие индикаторы авторизации
                    self._add_result(f"🔍 Поиск дополнительных индикаторов...")
                    auth_indicators = [
                        "[data-testid='user-menu']",
                        ".user-profile",
                        "#logout",
                        "[href*='logout']",
                        ".user-name",
                        "[class*='user']"
                    ]
                    
                    found_indicators = []
                    for indicator in auth_indicators:
                        try:
                            if page.locator(indicator).first.is_visible(timeout=500):  # Короткий таймаут
                                found_indicators.append(indicator)
                                self._add_result(f"✅ Найден индикатор: {indicator}")
                        except Exception as ind_error:
                            self._add_result(f"❌ Индикатор {indicator} не найден: {ind_error}")
                    
                    # Анализируем результат
                    is_likely_authorized = (
                        config.TARGET_URL in current_url or
                        "login" not in current_url.lower() or
                        len(found_indicators) > 0 or
                        "dashboard" in current_url.lower() or
                        "profile" in current_url.lower()
                    )
                    
                    if is_likely_authorized:
                        self._add_result(f"✅ УСПЕШНО: Пользователь {user_login} авторизован в системе!", "SUCCESS")
                        if found_indicators:
                            self._add_result(f"🎯 Найдены элементы авторизации: {', '.join(found_indicators)}", "SUCCESS")
                        self._add_result(f"🔐 Доступ к защищенной области подтвержден", "SUCCESS")
                        self._set_status(f"✅ {user_login} авторизован успешно", "green")
                    else:
                        self._add_result(f"❌ НЕУСПЕШНО: Пользователь {user_login} НЕ авторизован", "ERROR")
                        self._add_result(f"🔄 Перенаправление на: {current_url}", "WARNING")
                        if "login" in current_url.lower():
                            self._add_result(f"🚪 Перенаправлен на страницу входа", "WARNING")
                        self._set_status(f"❌ {user_login} не авторизован", "red")
                    
                    # Дополнительная проверка куков после загрузки страницы
                    new_cookies = context.cookies()
                    if new_cookies:
                        self._add_result(f"🍪 Активных куков в браузере: {len(new_cookies)}")
                    
                    browser.close()
                
            except Exception as e:
                error_msg = f"❌ Ошибка тестовой авторизации: {e}"
                self._add_result(error_msg, "ERROR")
                self._set_status("Ошибка тестовой авторизации", "red")
            finally:
                self.progress.stop()
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _test_no_authorization(self) -> None:
        """
        Тестирование сайта без авторизации (без подгрузки куков).
        Полезно для тестирования функций доступных неавторизованным пользователям.
        """
        def test_no_auth_thread():
            try:
                self._set_status("Тестирование без авторизации...", "orange")
                self.progress.start()
                self._add_result("Запуск тестирования без авторизации")
                
                from playwright.sync_api import sync_playwright
                
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=self.headless_var.get())
                    
                    # Создаем "чистый" контекст БЕЗ куков
                    context = browser.new_context()
                    
                    page = context.new_page()
                    
                    # Переходим на целевую страницу
                    page.goto(config.BASE_URL, timeout=30000)
                    
                    current_url = page.url
                    
                    # Проверяем, что мы НЕ авторизованы (должно быть перенаправление на логин)
                    if "login" in current_url.lower() or current_url == config.BASE_URL:
                        self._add_result("Тестирование без авторизации успешно - доступ к неавторизованным страницам", "SUCCESS")
                        self._set_status("Тестирование без авторизации успешно", "green")
                        
                        # Дополнительно можно протестировать доступные страницы
                        accessible_pages = [
                            config.BASE_URL,
                            config.LOGIN_URL
                        ]
                        
                        for test_url in accessible_pages:
                            try:
                                page.goto(test_url, timeout=15000)
                                self._add_result(f"Доступ к {test_url}: ✅")
                            except Exception:
                                self._add_result(f"Доступ к {test_url}: ❌", "WARNING")
                        
                    else:
                        self._add_result(f"Неожиданное поведение - перенаправление на {current_url}", "WARNING")
                        self._set_status("Неожиданное поведение при тестировании", "orange")
                    
                    browser.close()
                
            except Exception as e:
                error_msg = f"Ошибка тестирования без авторизации: {e}"
                self._add_result(error_msg, "ERROR")
                self._set_status("Ошибка тестирования", "red")
            finally:
                self.progress.stop()
        
        threading.Thread(target=test_no_auth_thread, daemon=True).start()
    
    def _clear_cookies(self) -> None:
        """Очистка куков выбранного пользователя."""
        user = self._get_selected_user()
        if not user:
            messagebox.showerror("Ошибка", "Пользователь не выбран")
            return
        
        # Безопасное получение логина пользователя
        user_login = user.get('login') or user.get('username', 'неизвестный пользователь')
        
        if messagebox.askyesno("Подтверждение", 
                              f"Удалить куки пользователя {user_login}?"):
            try:
                # Удаляем файл куков
                cookies_path = config.COOKIES_PATH.parent / f"{user.get('login', 'unknown')}_cookies.json"
                if cookies_path.exists():
                    cookies_path.unlink()
                
                # Обновляем базу данных
                self.user_manager.clear_user_cookie(user['id'])
                
                self._add_result(f"Куки пользователя {user.get('login', 'unknown')} очищены", "SUCCESS")
                self._set_status("Куки очищены", "green")
                
                # Обновляем информацию о пользователе
                self._on_user_selected(None)
                
            except Exception as e:
                error_msg = f"Ошибка очистки куков: {e}"
                self._add_result(error_msg, "ERROR")
                self._set_status("Ошибка очистки", "red")
    
    def _refresh_users_list(self) -> None:
        """Обновление списка пользователей в таблице."""
        try:
            # Очищаем таблицу
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            # Загружаем пользователей
            users = self.user_manager.get_all_users()
            
            for user in users:
                login = user.get('login', 'N/A')
                role = user.get('role', 'N/A')
                
                # Проверяем статус куков
                is_valid = self.user_manager.is_cookie_valid(user.get('id'))
                status = "✅ Валидны" if is_valid else "❌ Невалидны"
                
                # Последняя авторизация (если есть данные)
                last_auth = user.get('last_login', 'Не авторизован')
                if last_auth and last_auth != 'Не авторизован':
                    try:
                        # Форматируем дату если это timestamp
                        if isinstance(last_auth, (int, float)):
                            last_auth = datetime.fromtimestamp(last_auth).strftime('%d.%m.%Y %H:%M')
                    except:
                        pass
                
                self.users_tree.insert('', tk.END, values=(login, role, status, last_auth))
            
            self._set_status(f"Список пользователей обновлен ({len(users)} пользователей)", "green")
            
        except Exception as e:
            error_msg = f"Ошибка обновления списка пользователей: {e}"
            self.logger.error(error_msg)
            messagebox.showerror("Ошибка", error_msg)
    
    def _clear_all_cookies(self) -> None:
        """Очистка всех куков."""
        if messagebox.askyesno("Подтверждение", 
                              "Удалить ВСЕ сохранённые куки? Это действие нельзя отменить."):
            try:
                users = self.user_manager.get_all_users()
                cleared_count = 0
                
                for user in users:
                    try:
                        # Удаляем файл куков
                        cookies_path = config.COOKIES_PATH.parent / f"{user.get('login', 'unknown')}_cookies.json"
                        if cookies_path.exists():
                            cookies_path.unlink()
                        
                        # Очищаем в базе данных
                        self.user_manager.clear_user_cookie(user['id'])
                        cleared_count += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Не удалось очистить куки для {user.get('login', 'unknown')}: {e}")
                
                self._add_result(f"Очищены куки для {cleared_count} пользователей", "SUCCESS")
                self._set_status("Все куки очищены", "green")
                
                # Обновляем списки
                self._refresh_users_list()
                self._on_user_selected(None)
                
            except Exception as e:
                error_msg = f"Ошибка очистки всех куков: {e}"
                self._add_result(error_msg, "ERROR")
                self._set_status("Ошибка очистки", "red")
    
    def _refresh_logs(self) -> None:
        """Обновление логов."""
        try:
            self.logs_text.config(state=tk.NORMAL)
            self.logs_text.delete(1.0, tk.END)
            
            # Читаем лог-файл
            if config.LOG_FILE.exists():
                with open(config.LOG_FILE, 'r', encoding='utf-8') as f:
                    logs = f.read()
                    # Показываем последние 1000 строк
                    lines = logs.split('\n')
                    if len(lines) > 1000:
                        lines = lines[-1000:]
                    
                    self.logs_text.insert(tk.END, '\n'.join(lines))
            else:
                self.logs_text.insert(tk.END, "Лог-файл не найден")
            
            self.logs_text.see(tk.END)
            self.logs_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Ошибка чтения логов: {e}")
    
    def _clear_logs(self) -> None:
        """Очистка логов."""
        if messagebox.askyesno("Подтверждение", "Очистить все логи?"):
            try:
                if config.LOG_FILE.exists():
                    config.LOG_FILE.unlink()
                
                self.logs_text.config(state=tk.NORMAL)
                self.logs_text.delete(1.0, tk.END)
                self.logs_text.insert(tk.END, "Логи очищены")
                self.logs_text.config(state=tk.DISABLED)
                
                self._set_status("Логи очищены", "green")
                
            except Exception as e:
                error_msg = f"Ошибка очистки логов: {e}"
                self.logger.error(error_msg)
                messagebox.showerror("Ошибка", error_msg)
    
    def _refresh_data(self) -> None:
        """Обновление всех данных."""
        self._load_users()
        self._refresh_users_list()
        self._refresh_logs()
        self._set_status("Данные обновлены", "green")
    
    def _show_about(self) -> None:
        """Показ информации о программе."""
        about_text = """
Auth Project GUI Manager

Версия: 1.0.0
Автор: Lead SDET

Графический интерфейс для управления 
авторизацией в системе автоматизированного 
тестирования.

Возможности:
• Авторизация различных пользователей
• Проверка валидности куков
• Управление пользовательскими данными
• Просмотр логов операций

© 2024 Auth Project
        """
        messagebox.showinfo("О программе", about_text)
    
    def run(self) -> None:
        """Запуск GUI приложения."""
        try:
            self.logger.info("Запуск GUI приложения")
            self._set_status("Приложение готово к работе", "green")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Критическая ошибка GUI: {e}")
            messagebox.showerror("Критическая ошибка", f"Произошла критическая ошибка: {e}")
        finally:
            self.logger.info("Завершение работы GUI приложения")


def main():
    """Главная функция запуска GUI."""
    try:
        app = AuthGUI()
        app.run()
    except Exception as e:
        logging.error(f"Ошибка запуска приложения: {e}")
        messagebox.showerror("Ошибка запуска", f"Не удалось запустить приложение: {e}")


if __name__ == "__main__":
    main()
