"""
Главный класс графического интерфейса для управления авторизацией.

Рефакторированная версия с разделением ответственности:
- Основной класс содержит только инициализацию и координацию
- Компоненты вынесены в отдельные модули
- Операции авторизации изолированы
- Убраны устаревшие комментарии
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Добавляем путь к модулям проекта
sys.path.append(str(Path(__file__).parent.parent))

from projects.auth_management.config import config
from projects.auth_management.logger import setup_logger
from projects.auth_management.user_manager import UserManager
from projects.auth_management.database import init_db
from projects.auth_management.gui.utils.gui_helpers import GUIHelper, setup_gui_styles, extract_login_from_selection, format_user_info
from projects.auth_management.gui.utils.auth_operations import AuthOperations


class AuthGUI:
    """
    Основной класс графического интерфейса для управления авторизацией.
    
    Обеспечивает координацию между компонентами GUI и бизнес-логикой.
    Содержит только основную структуру интерфейса и делегирует операции
    специализированным классам.
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
        
        # Создание элементов интерфейса
        self._setup_ui()
        
        # Инициализация помощников и операций
        self._init_helpers()
        
        # Загрузка данных
        self._load_initial_data()
        
        self.logger.info("GUI приложение инициализировано")
    
    def _setup_ui(self) -> None:
        """Создание основной структуры интерфейса."""
        # Настройка стилей
        style = ttk.Style()
        setup_gui_styles(style)
        
        # Главное меню
        self._create_menu()
        
        # Основной контейнер с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Создание вкладок
        self._create_auth_tab()
        self._create_users_tab()
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
        file_menu.add_command(label="Обновить данные", command=self._refresh_all_data)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Операции"
        operations_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Операции", menu=operations_menu)
        operations_menu.add_command(label="Авторизовать всех", command=self._handle_authorize_all)
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)
    
    def _create_auth_tab(self) -> None:
        """Создание вкладки авторизации."""
        auth_frame = ttk.Frame(self.notebook)
        self.notebook.add(auth_frame, text="Авторизация")
        
        main_container = ttk.Frame(auth_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Группа выбора пользователя
        self._create_user_selection_group(main_container)
        
        # Группа действий
        self._create_actions_group(main_container)
        
        # Группа результатов
        self._create_results_group(main_container)
    
    def _create_user_selection_group(self, parent: tk.Widget) -> None:
        """Создание группы выбора пользователя."""
        user_group = ttk.LabelFrame(parent, text="Выбор пользователя", padding=10)
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
    
    def _create_actions_group(self, parent: tk.Widget) -> None:
        """Создание группы действий."""
        actions_group = ttk.LabelFrame(parent, text="Действия", padding=10)
        actions_group.pack(fill=tk.X, pady=(0, 15))
        
        buttons_frame = ttk.Frame(actions_group)
        buttons_frame.pack(fill=tk.X)
        
        # Первая строка кнопок
        row1_frame = ttk.Frame(buttons_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.auth_btn = ttk.Button(row1_frame, text="🔐 Авторизоваться", 
                                  command=self._handle_authorize_user, style='Primary.TButton')
        self.auth_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.test_auth_btn = ttk.Button(row1_frame, text="🍪 Тест с куками", 
                                       command=self._handle_test_auth, style='Success.TButton')
        self.test_auth_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.test_no_auth_btn = ttk.Button(row1_frame, text="🚫 Тест без авторизации", 
                                          command=self._handle_test_no_auth, style='Warning.TButton')
        self.test_no_auth_btn.pack(side=tk.LEFT)
        
        # Вторая строка
        row2_frame = ttk.Frame(buttons_frame)
        row2_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Настройки
        self.headless_var = tk.BooleanVar(value=False)
        self.headless_check = ttk.Checkbutton(row2_frame, text="Headless режим", 
                                          variable=self.headless_var)
        self.headless_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.clear_cookies_btn = ttk.Button(row2_frame, text="🗑️ Очистить куки", 
                                           command=self._handle_clear_cookies, style='Danger.TButton')
        self.clear_cookies_btn.pack(side=tk.RIGHT)
        
        # Сохраняем кнопки для управления состоянием
        self.buttons = {
            'auth': self.auth_btn,
            'test_auth': self.test_auth_btn,
            'test_no_auth': self.test_no_auth_btn,
            'clear_cookies': self.clear_cookies_btn
        }
    
    def _create_results_group(self, parent: tk.Widget) -> None:
        """Создание группы результатов."""
        progress_group = ttk.LabelFrame(parent, text="Статус", padding=10)
        progress_group.pack(fill=tk.BOTH, expand=True)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(progress_group, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Область результатов
        from tkinter import scrolledtext
        self.result_text = scrolledtext.ScrolledText(progress_group, height=10, 
                                                    state=tk.DISABLED, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)
    
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
                  command=self._handle_clear_all_cookies, style='Danger.TButton').pack(side=tk.LEFT)
    
    def _create_logs_tab(self) -> None:
        """Создание вкладки логов."""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Логи")
        
        logs_container = ttk.Frame(logs_frame)
        logs_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Кнопки управления логами
        logs_buttons_frame = ttk.Frame(logs_container)
        logs_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(logs_buttons_frame, text="🔄 Обновить логи", 
                  command=self._refresh_logs).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(logs_buttons_frame, text="🗑️ Очистить логи", 
                  command=self._handle_clear_logs).pack(side=tk.LEFT)
        
        # Текстовая область для логов
        from tkinter import scrolledtext
        self.logs_text = scrolledtext.ScrolledText(logs_container, height=25, 
                                                  state=tk.DISABLED, wrap=tk.WORD)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_status_bar(self) -> None:
        """Создание статусной строки."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Готов к работе")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.status_indicator = ttk.Label(self.status_bar, text="●", foreground="green")
        self.status_indicator.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def _init_helpers(self) -> None:
        """Инициализация помощников и операций."""
        # Создаем GUI помощника
        self.gui_helper = GUIHelper(
            status_label=self.status_label,
            status_indicator=self.status_indicator,
            result_text=self.result_text,
            logger=self.logger
        )
        
        # Создаем операции авторизации
        self.auth_operations = AuthOperations(
            user_manager=self.user_manager,
            gui_helper=self.gui_helper,
            progress_bar=self.progress
        )
    
    def _load_initial_data(self) -> None:
        """Загрузка начальных данных."""
        self._load_users()
        self._refresh_users_list()
        self._refresh_logs()
        # Не отключаем кнопки принудительно - состояние устанавливается в _load_users
    
    def _load_users(self) -> None:
        """Загрузка списка пользователей в комбобокс."""
        try:
            users = self.user_manager.get_all_users()
            user_list = []
            
            for user in users:
                login = user.get('login', user.get('username', '')).strip()
                role = user.get('role', 'user').strip()
                
                # Фильтруем некорректных пользователей
                if not login or login.lower() in ['unknown', 'none', ''] or not role:
                    self.logger.warning(f"Пропускаем пользователя с некорректными данными: {login}")
                    continue
                
                if not user.get('id'):
                    self.logger.warning(f"Пропускаем пользователя без ID: {login}")
                    continue
                
                user_list.append(f"{login} ({role})")
            
            self.user_combo['values'] = user_list
            
            if user_list:
                self.user_combo.current(0)
                self.user_var.set(user_list[0])
                self._on_user_selected(None)
                self.logger.info(f"Загружено {len(user_list)} пользователей")
            else:
                self.logger.warning("Не найдено валидных пользователей")
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
            login = extract_login_from_selection(self.user_var.get())
            if not login:
                self._update_buttons_state(False)
                return
            
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
        
        info = format_user_info(user)
        
        # Проверяем статус куков
        cookie_status = "✅ Валидны" if self.user_manager.is_cookie_valid(user.get('id')) else "❌ Невалидны"
        info += f"\nСтатус куков: {cookie_status}"
        
        self.info_text.insert(tk.END, info)
        self.info_text.config(state=tk.DISABLED)
    
    def _update_buttons_state(self, enabled: bool) -> None:
        """Обновление состояния кнопок."""
        from projects.auth_management.gui.utils.gui_helpers import update_buttons_state
        update_buttons_state(self.buttons, enabled)
    
    def _get_selected_user(self) -> Optional[Dict[str, Any]]:
        """Получение данных выбранного пользователя."""
        selected_value = self.user_var.get()
        if not selected_value:
            return None
        
        login = extract_login_from_selection(selected_value)
        if not login:
            return None
        
        return self.user_manager.get_user(login)
    
    def _get_user_password(self, login: str) -> Optional[str]:
        """Получение пароля пользователя."""
        try:
            user = self.user_manager.get_user(login)
            if not user:
                return None
            
            # Сначала проверяем БД
            if 'password' in user and user['password']:
                return user['password']
            
            # Fallback на конфигурацию по ролям
            role = user.get('role', 'user').lower().strip()
            role_password_map = {
                'admin': config.ADMIN_PASS,
                'moderator': config.MODERATOR_PASS, 
                'expert': config.EXPERT_PASS,
                'user': config.USER_PASS,
            }
            
            return role_password_map.get(role, config.PASS)
            
        except Exception as e:
            self.logger.error(f"Ошибка получения пароля для {login}: {e}")
            return None
    
    # Обработчики событий
    def _handle_authorize_user(self) -> None:
        """Обработчик авторизации пользователя."""
        user = self._get_selected_user()
        if not user:
            messagebox.showerror("Ошибка", "Пользователь не выбран")
            return
        
        # Получаем логин пользователя
        user_login = user.get('login') or user.get('username')
        
        self.logger.info(f"Начало авторизации пользователя: {user_login}")
        self.gui_helper.add_result(f"🔄 Запускается авторизация пользователя: {user_login}")
        
        # Проверяем пароль
        password = self._get_user_password(user_login)
        if not password:
            error_msg = f"Не удалось получить пароль для пользователя {user_login}"
            self.logger.error(error_msg)
            self.gui_helper.add_result(error_msg, "ERROR")
            messagebox.showerror("Ошибка", error_msg)
            return
            
        self.gui_helper.add_result(f"✅ Пароль для пользователя получен")
        
        self.auth_operations.authorize_user(
            user=user,
            headless=self.headless_var.get(),
            password_func=self._get_user_password
        )
    
    def _handle_test_auth(self) -> None:
        """Обработчик тестирования авторизации."""
        user = self._get_selected_user()
        if not user:
            messagebox.showerror("Ошибка", "Пользователь не выбран")
            return
        
        self.auth_operations.test_authorization_with_cookies(
            user=user,
            headless=self.headless_var.get()
        )
    
    def _handle_test_no_auth(self) -> None:
        """Обработчик тестирования без авторизации."""
        self.auth_operations.test_no_authorization(headless=self.headless_var.get())
    
    def _handle_clear_cookies(self) -> None:
        """Обработчик очистки куков пользователя."""
        user = self._get_selected_user()
        if not user:
            messagebox.showerror("Ошибка", "Пользователь не выбран")
            return
        
        user_login = user.get('login', 'неизвестный')
        
        if messagebox.askyesno("Подтверждение", f"Удалить куки пользователя {user_login}?"):
            try:
                # Удаляем файл куков
                cookies_path = config.COOKIES_PATH.parent / f"{user.get('login', 'unknown')}_cookies.json"
                if cookies_path.exists():
                    cookies_path.unlink()
                
                # Обновляем БД
                self.user_manager.clear_user_cookie(user['id'])
                
                self.gui_helper.add_result(f"Куки пользователя {user_login} очищены", "SUCCESS")
                self.gui_helper.set_status("Куки очищены", "green")
                
                # Обновляем информацию
                self._on_user_selected(None)
                
            except Exception as e:
                error_msg = f"Ошибка очистки куков: {e}"
                self.gui_helper.add_result(error_msg, "ERROR")
                self.gui_helper.set_status("Ошибка очистки", "red")
    
    def _handle_authorize_all(self) -> None:
        """Обработчик массовой авторизации."""
        self.auth_operations.authorize_all_users(password_func=self._get_user_password)
    
    def _handle_clear_all_cookies(self) -> None:
        """Обработчик очистки всех куков."""
        if messagebox.askyesno("Подтверждение", 
                              "Удалить ВСЕ сохранённые куки? Это действие нельзя отменить."):
            try:
                users = self.user_manager.get_all_users()
                cleared_count = 0
                
                for user in users:
                    try:
                        cookies_path = config.COOKIES_PATH.parent / f"{user.get('login', 'unknown')}_cookies.json"
                        if cookies_path.exists():
                            cookies_path.unlink()
                        
                        self.user_manager.clear_user_cookie(user['id'])
                        cleared_count += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Не удалось очистить куки для {user.get('login')}: {e}")
                
                self.gui_helper.add_result(f"Очищены куки для {cleared_count} пользователей", "SUCCESS")
                self.gui_helper.set_status("Все куки очищены", "green")
                
                self._refresh_users_list()
                self._on_user_selected(None)
                
            except Exception as e:
                error_msg = f"Ошибка очистки всех куков: {e}"
                self.gui_helper.add_result(error_msg, "ERROR")
                self.gui_helper.set_status("Ошибка очистки", "red")
    
    def _handle_clear_logs(self) -> None:
        """Обработчик очистки логов."""
        if messagebox.askyesno("Подтверждение", "Очистить все логи?"):
            try:
                if config.LOG_FILE.exists():
                    config.LOG_FILE.unlink()
                
                self.logs_text.config(state=tk.NORMAL)
                self.logs_text.delete(1.0, tk.END)
                self.logs_text.insert(tk.END, "Логи очищены")
                self.logs_text.config(state=tk.DISABLED)
                
                self.gui_helper.set_status("Логи очищены", "green")
                
            except Exception as e:
                error_msg = f"Ошибка очистки логов: {e}"
                self.logger.error(error_msg)
                messagebox.showerror("Ошибка", error_msg)
    
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
                
                # Последняя авторизация
                last_auth = user.get('last_login', 'Не авторизован')
                from projects.auth_management.gui.utils.gui_helpers import format_datetime
                last_auth = format_datetime(last_auth)
                
                self.users_tree.insert('', tk.END, values=(login, role, status, last_auth))
            
            self.gui_helper.set_status(f"Список обновлен ({len(users)} пользователей)", "green")
            
        except Exception as e:
            error_msg = f"Ошибка обновления списка пользователей: {e}"
            self.logger.error(error_msg)
            messagebox.showerror("Ошибка", error_msg)
    
    def _refresh_logs(self) -> None:
        """Обновление логов."""
        try:
            self.logs_text.config(state=tk.NORMAL)
            self.logs_text.delete(1.0, tk.END)
            
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
    
    def _refresh_all_data(self) -> None:
        """Обновление всех данных."""
        self._load_users()
        self._refresh_users_list()
        self._refresh_logs()
        self.gui_helper.set_status("Данные обновлены", "green")
    
    def _show_about(self) -> None:
        """Показ информации о программе."""
        about_text = """
Auth Project GUI Manager

Версия: 2.0.0 (Рефакторированная)
Автор: Lead SDET

Графический интерфейс для управления 
авторизацией в системе автоматизированного 
тестирования.

Возможности:
• Авторизация различных пользователей
• Тестирование авторизации с куками
• Управление пользовательскими данными
• Просмотр логов операций

© 2024 Auth Project
        """
        messagebox.showinfo("О программе", about_text)
    
    def run(self) -> None:
        """Запуск GUI приложения."""
        try:
            self.logger.info("Запуск GUI приложения")
            self.gui_helper.set_status("Приложение готово к работе", "green")
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
