"""
Скрипт для автоматической настройки системы управления секретами.

Этот скрипт:
- Устанавливает необходимые зависимости
- Создает файлы конфигурации из шаблонов
- Проверяет правильность настройки .gitignore
- Выполняет валидацию безопасности
- Предоставляет интерактивное руководство по настройке

Автор: Lead SDET Architect
Дата создания: 2025-06-27
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
import shutil


class Color:
    """ANSI цвета для консольного вывода."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class SecretsSetup:
    """Установщик системы управления секретами."""
    
    def __init__(self) -> None:
        """Инициализация установщика."""
        self.project_root = Path.cwd()
        self.config_dir = self.project_root / "config"
        
        # Файлы, которые должны быть созданы
        self.required_files = [
            self.config_dir / "secrets_manager.py",
            self.config_dir / ".env.template",
            self.config_dir / ".gitignore",
            self.project_root / "secure_auth_utils.py"
        ]
        
        # Зависимости Python
        self.required_packages = [
            "python-dotenv",
            "playwright"
        ]
    
    def print_header(self, title: str) -> None:
        """Печать заголовка секции."""
        print(f"\n{Color.BLUE}{Color.BOLD}{'='*60}{Color.END}")
        print(f"{Color.BLUE}{Color.BOLD}{title.center(60)}{Color.END}")
        print(f"{Color.BLUE}{Color.BOLD}{'='*60}{Color.END}\n")
    
    def print_success(self, message: str) -> None:
        """Печать сообщения об успехе."""
        print(f"{Color.GREEN}✅ {message}{Color.END}")
    
    def print_warning(self, message: str) -> None:
        """Печать предупреждения."""
        print(f"{Color.YELLOW}⚠️  {message}{Color.END}")
    
    def print_error(self, message: str) -> None:
        """Печать ошибки."""
        print(f"{Color.RED}❌ {message}{Color.END}")
    
    def print_info(self, message: str) -> None:
        """Печать информационного сообщения."""
        print(f"{Color.BLUE}ℹ️  {message}{Color.END}")
    
    def check_python_version(self) -> bool:
        """Проверка версии Python."""
        if sys.version_info < (3, 8):
            self.print_error("Требуется Python 3.8 или выше")
            return False
        
        self.print_success(f"Python версия: {sys.version.split()[0]}")
        return True
    
    def install_dependencies(self) -> bool:
        """Установка зависимостей Python."""
        self.print_info("Проверка и установка зависимостей...")
        
        for package in self.required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.print_success(f"Пакет {package} уже установлен")
            except ImportError:
                self.print_info(f"Установка пакета {package}...")
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", package
                    ])
                    self.print_success(f"Пакет {package} установлен")
                except subprocess.CalledProcessError:
                    self.print_error(f"Не удалось установить пакет {package}")
                    return False
        
        return True
    
    def create_config_directory(self) -> bool:
        """Создание директории конфигурации."""
        try:
            self.config_dir.mkdir(exist_ok=True)
            self.print_success(f"Директория конфигурации создана: {self.config_dir}")
            return True
        except Exception as e:
            self.print_error(f"Не удалось создать директорию: {e}")
            return False
    
    def check_required_files(self) -> List[Path]:
        """Проверка наличия обязательных файлов."""
        missing_files = []
        
        for file_path in self.required_files:
            if not file_path.exists():
                missing_files.append(file_path)
            else:
                self.print_success(f"Файл найден: {file_path.name}")
        
        if missing_files:
            self.print_warning("Отсутствующие файлы:")
            for file_path in missing_files:
                print(f"  - {file_path}")
        
        return missing_files
    
    def create_env_file_from_template(self) -> bool:
        """Создание .env файла из шаблона."""
        template_path = self.config_dir / ".env.template"
        env_path = self.config_dir / ".env"
        
        if not template_path.exists():
            self.print_error("Шаблон .env.template не найден")
            return False
        
        if env_path.exists():
            self.print_warning(".env файл уже существует")
            response = input("Перезаписать? (y/N): ").lower()
            if response != 'y':
                return True
        
        try:
            shutil.copy2(template_path, env_path)
            self.print_success("Создан файл .env из шаблона")
            self.print_info(f"Отредактируйте файл {env_path} и заполните реальными данными")
            return True
        except Exception as e:
            self.print_error(f"Не удалось создать .env файл: {e}")
            return False
    
    def check_gitignore(self) -> bool:
        """Проверка настройки .gitignore."""
        main_gitignore = self.project_root / ".gitignore"
        config_gitignore = self.config_dir / ".gitignore"
        
        # Проверяем основной .gitignore
        if main_gitignore.exists():
            try:
                content = main_gitignore.read_text(encoding='utf-8')
                if '.env' in content:
                    self.print_success("Основной .gitignore настроен правильно")
                else:
                    self.print_warning("В основном .gitignore отсутствует правило для .env файлов")
            except Exception as e:
                self.print_error(f"Не удалось прочитать .gitignore: {e}")
        else:
            self.print_warning("Основной .gitignore не найден")
        
        # Проверяем .gitignore в config/
        if config_gitignore.exists():
            self.print_success("Конфигурационный .gitignore найден")
        else:
            self.print_warning("Конфигурационный .gitignore не найден")
        
        return True
    
    def validate_configuration(self) -> bool:
        """Валидация конфигурации."""
        try:
            # Пытаемся импортировать и инициализировать менеджер секретов
            sys.path.insert(0, str(self.project_root))
            
            from config.secrets_manager import SecretsManager
            
            manager = SecretsManager()
            summary = manager.get_masked_config_summary()
            
            self.print_success("Менеджер секретов работает корректно")
            
            # Показываем статус конфигурации
            print("\n📋 Статус конфигурации:")
            for key, value in summary.items():
                status_icon = "✅" if value else "❌"
                print(f"  {status_icon} {key}: {value}")
            
            return True
            
        except ImportError as e:
            self.print_error(f"Не удалось импортировать модули: {e}")
            return False
        except Exception as e:
            self.print_warning(f"Конфигурация неполная: {e}")
            self.print_info("Это нормально при первом запуске. Заполните .env файл.")
            return True
    
    def show_next_steps(self) -> None:
        """Показ следующих шагов настройки."""
        self.print_header("СЛЕДУЮЩИЕ ШАГИ")
        
        print("1. 📝 Заполните файл конфигурации:")
        print(f"   Отредактируйте: {self.config_dir / '.env'}")
        print("   Укажите реальные значения для:")
        print("   - AUTH_USERNAME (имя пользователя)")
        print("   - AUTH_PASSWORD (пароль)")
        print("   - AUTH_DOMAIN (домен сайта)")
        
        print("\n2. 🔒 Проверьте безопасность:")
        print("   git status  # убедитесь, что .env не отслеживается")
        print("   git add .   # добавьте только шаблоны и код")
        
        print("\n3. ✅ Протестируйте настройку:")
        print("   python config/secrets_manager.py")
        print("   python secure_auth_utils.py")
        
        print("\n4. 🔄 Обновите существующие тесты:")
        print("   Замените импорты:")
        print("   from framework.utils.auth_utils\1 save_cookie, load_cookie")
        print("   на:")
        print("   from secure_auth_utils import save_cookie, load_cookie")
        
        print(f"\n{Color.BOLD}ВАЖНО:{Color.END}")
        print("❌ НИКОГДА не коммитьте файлы .env с реальными данными!")
        print("✅ Используйте только тестовые учетные данные")
        print("✅ Регулярно меняйте пароли тестовых аккаунтов")
    
    def run_interactive_setup(self) -> bool:
        """Интерактивная настройка."""
        self.print_header("ИНТЕРАКТИВНАЯ НАСТРОЙКА СЕКРЕТОВ")
        
        print("Этот мастер поможет настроить систему управления секретами.")
        print("Процесс займет несколько минут.")
        
        response = input(f"\n{Color.BOLD}Продолжить? (Y/n): {Color.END}").lower()
        if response == 'n':
            print("Настройка отменена.")
            return False
        
        steps = [
            ("Проверка версии Python", self.check_python_version),
            ("Установка зависимостей", self.install_dependencies),
            ("Создание директории конфигурации", self.create_config_directory),
            ("Проверка обязательных файлов", lambda: len(self.check_required_files()) == 0),
            ("Создание .env файла", self.create_env_file_from_template),
            ("Проверка .gitignore", self.check_gitignore),
            ("Валидация конфигурации", self.validate_configuration)
        ]
        
        all_success = True
        
        for step_name, step_func in steps:
            self.print_info(f"Выполнение: {step_name}")
            try:
                success = step_func()
                if not success:
                    all_success = False
                    self.print_error(f"Ошибка в шаге: {step_name}")
                else:
                    self.print_success(f"Завершено: {step_name}")
            except Exception as e:
                all_success = False
                self.print_error(f"Исключение в шаге '{step_name}': {e}")
        
        if all_success:
            self.print_success("Базовая настройка завершена успешно!")
        else:
            self.print_warning("Настройка завершена с предупреждениями")
        
        self.show_next_steps()
        return all_success


def main() -> None:
    """Главная функция установщика."""
    setup = SecretsSetup()
    
    try:
        success = setup.run_interactive_setup()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Настройка прервана пользователем{Color.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Color.RED}Критическая ошибка: {e}{Color.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
