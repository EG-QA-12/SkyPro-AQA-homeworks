#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для массовой проверки кук test_joint_session на сайте ca.bll.by

Этот скрипт позволяет автоматизировать процесс проверки авторизации
с использованием кук из файлов в папке cookies. Вместо ручной подстановки
через DevTools, скрипт автоматически извлекает нужную куку и тестирует её.

Автор: SDET-Архитектор
Цель: Обучение и автоматизация для Junior QA команды
"""

import json
import os
import sys
import requests
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote


class CookieTester:
    """
    Класс для тестирования кук test_joint_session на сайте ca.bll.by
    
    Основная задача класса - автоматизировать процесс проверки авторизации
    пользователей через куки, сохраненные в JSON-файлах.
    
    Attributes:
        cookies_dir (Path): Путь к папке с файлами кук
        target_cookie_name (str): Имя куки для поиска ('test_joint_session')
        test_url (str): URL для проверки авторизации
        session (requests.Session): HTTP-сессия для запросов
    """
    
    def __init__(self, cookies_dir: str = "D:\\Bll_tests\\cookies"):
        """
        Инициализация тестера кук
        
        Args:
            cookies_dir (str): Путь к папке с JSON-файлами кук
        """
        self.cookies_dir = Path(cookies_dir)
        self.target_cookie_name = "test_joint_session"
        self.test_url = "https://ca.bll.by"
        self.session = requests.Session()
        
        # Настройка заголовков для имитации реального браузера
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def get_cookie_files(self) -> List[Path]:
        """
        Получает список всех JSON-файлов с куками из папки
        
        Returns:
            List[Path]: Отсортированный список путей к файлам кук
            
        Raises:
            FileNotFoundError: Если папка с куками не найдена
        """
        if not self.cookies_dir.exists():
            raise FileNotFoundError(f"Папка с куками не найдена: {self.cookies_dir}")
        
        # Находим все JSON-файлы в папке
        cookie_files = list(self.cookies_dir.glob("*.json"))
        
        # Сортируем файлы для предсказуемого порядка
        # Используем естественную сортировку для правильного порядка номеров
        def natural_sort_key(path: Path) -> List:
            """Функция для естественной сортировки файлов по номерам"""
            return [int(text) if text.isdigit() else text.lower() 
                   for text in re.split('([0-9]+)', path.name)]
        
        cookie_files.sort(key=natural_sort_key)
        return cookie_files

    def extract_target_cookie(self, file_path: Path) -> Optional[Dict[str, str]]:
        """
        Извлекает целевую куку test_joint_session из JSON-файла
        
        Args:
            file_path (Path): Путь к JSON-файлу с куками
            
        Returns:
            Optional[Dict[str, str]]: Словарь с данными куки или None, если не найдена
            
        Note:
            Функция ищет куку с именем 'test_joint_session' в массиве кук.
            Возвращает полные данные куки включая value, domain, path и т.д.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # Ищем нужную куку в списке
            for cookie in cookies_data:
                if cookie.get('name') == self.target_cookie_name:
                    return cookie
                    
            return None
            
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"❌ Ошибка чтения файла {file_path.name}: {e}")
            return None
        except Exception as e:
            print(f"❌ Неожиданная ошибка при обработке {file_path.name}: {e}")
            return None

    def test_cookie_authorization(self, cookie_data: Dict[str, str], file_name: str) -> Tuple[bool, str]:
        """
        Тестирует авторизацию с использованием куки на сайте ca.bll.by
        
        Args:
            cookie_data (Dict[str, str]): Данные куки для тестирования
            file_name (str): Имя файла для логирования
            
        Returns:
            Tuple[bool, str]: (успех_авторизации, детали_ответа)
            
        Note:
            Функция отправляет GET-запрос на ca.bll.by с установленной кукой
            и анализирует ответ для определения успешности авторизации.
        """
        try:
            # Очищаем сессию от предыдущих кук
            self.session.cookies.clear()
            
            # Декодируем значение куки если оно URL-encoded
            cookie_value = unquote(cookie_data['value'])
            
            # Устанавливаем куку в сессию
            self.session.cookies.set(
                name=cookie_data['name'],
                value=cookie_value,
                domain=cookie_data.get('domain', '.bll.by').lstrip('.'),
                path=cookie_data.get('path', '/')
            )
            
            # Отправляем запрос на сайт
            response = self.session.get(self.test_url, timeout=10)
            
            # Анализируем ответ для определения авторизации
            # Эти проверки могут потребовать корректировки в зависимости от сайта
            auth_indicators = [
                'logout',  # Кнопка выхода
                'profile',  # Профиль пользователя  
                'dashboard',  # Панель управления
                'Выйти',  # Кнопка выхода на русском
                'Профиль'  # Профиль на русском
            ]
            
            response_text = response.text.lower()
            is_authorized = any(indicator.lower() in response_text for indicator in auth_indicators)
            
            # Дополнительная проверка: отсутствие форм логина
            has_login_form = any(login_term in response_text for login_term in ['login', 'войти', 'авторизация'])
            
            if is_authorized and not has_login_form:
                return True, f"✅ Авторизация успешна (код: {response.status_code})"
            elif response.status_code == 200:
                return False, f"❌ Авторизация не удалась - пользователь не авторизован (код: {response.status_code})"
            else:
                return False, f"❌ Ошибка HTTP: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, f"❌ Таймаут запроса к {self.test_url}"
        except requests.exceptions.ConnectionError:
            return False, f"❌ Ошибка соединения с {self.test_url}"
        except Exception as e:
            return False, f"❌ Неожиданная ошибка: {e}"

    def display_file_menu(self, files: List[Path]) -> List[Path]:
        """
        Отображает интерактивное меню для выбора файлов
        
        Args:
            files (List[Path]): Список всех доступных файлов
            
        Returns:
            List[Path]: Список выбранных для обработки файлов
        """
        print(f"\n📁 Найдено {len(files)} файлов с куками")
        print("\n" + "="*60)
        print("МЕНЮ ВЫБОРА ФАЙЛОВ")
        print("="*60)
        print("1. 🔄 Обработать ВСЕ файлы")
        print("2. 📊 Обработать ДИАПАЗОН файлов (например, 1-50)")
        print("3. 🎯 Обработать КОНКРЕТНЫЕ файлы (например, 1,5,10)")
        print("4. 📋 Показать список всех файлов")
        print("5. ❌ Выход")
        print("="*60)
        
        while True:
            choice = input("\n👆 Выберите опцию (1-5): ").strip()
            
            if choice == "1":
                return files
            
            elif choice == "2":
                return self._select_range(files)
            
            elif choice == "3":
                return self._select_specific(files)
            
            elif choice == "4":
                self._display_all_files(files)
                continue
            
            elif choice == "5":
                print("👋 До свидания!")
                sys.exit(0)
            
            else:
                print("❌ Неверный выбор. Пожалуйста, выберите от 1 до 5.")

    def _select_range(self, files: List[Path]) -> List[Path]:
        """Выбор диапазона файлов"""
        while True:
            try:
                range_input = input(f"\n📊 Введите диапазон (1-{len(files)}, например '1-50'): ").strip()
                
                if '-' not in range_input:
                    print("❌ Неверный формат. Используйте формат '1-50'")
                    continue
                
                start_str, end_str = range_input.split('-', 1)
                start = int(start_str.strip())
                end = int(end_str.strip())
                
                if start < 1 or end > len(files) or start > end:
                    print(f"❌ Неверный диапазон. Доступны файлы от 1 до {len(files)}")
                    continue
                
                selected_files = files[start-1:end]
                print(f"✅ Выбрано {len(selected_files)} файлов для обработки")
                return selected_files
                
            except ValueError:
                print("❌ Ошибка ввода. Используйте числа в формате '1-50'")

    def _select_specific(self, files: List[Path]) -> List[Path]:
        """Выбор конкретных файлов"""
        while True:
            try:
                specific_input = input(f"\n🎯 Введите номера файлов через запятую (1-{len(files)}, например '1,5,10'): ").strip()
                
                indices = [int(x.strip()) for x in specific_input.split(',')]
                
                # Проверяем корректность индексов
                invalid_indices = [i for i in indices if i < 1 or i > len(files)]
                if invalid_indices:
                    print(f"❌ Неверные номера файлов: {invalid_indices}. Доступны от 1 до {len(files)}")
                    continue
                
                selected_files = [files[i-1] for i in indices]
                print(f"✅ Выбрано {len(selected_files)} файлов для обработки")
                return selected_files
                
            except ValueError:
                print("❌ Ошибка ввода. Используйте числа через запятую, например '1,5,10'")

    def _display_all_files(self, files: List[Path]):
        """Отображает список всех файлов"""
        print(f"\n📋 СПИСОК ВСЕХ ФАЙЛОВ ({len(files)} штук):")
        print("-" * 60)
        
        for i, file_path in enumerate(files, 1):
            print(f"{i:3d}. {file_path.name}")
            
            # Пауза каждые 20 файлов для удобства чтения
            if i % 20 == 0 and i < len(files):
                input("\n⏸️  Нажмите Enter для продолжения...")
        
        print("-" * 60)

    def run_batch_test(self, selected_files: List[Path]) -> None:
        """
        Запускает массовое тестирование выбранных файлов
        
        Args:
            selected_files (List[Path]): Список файлов для тестирования
        """
        print(f"\n🚀 НАЧИНАЕМ МАССОВОЕ ТЕСТИРОВАНИЕ")
        print(f"📂 Файлов к обработке: {len(selected_files)}")
        print("=" * 80)
        
        # Статистика результатов
        stats = {
            'total': 0,
            'found_cookies': 0,
            'successful_auth': 0,
            'failed_auth': 0,
            'no_cookie': 0,
            'errors': 0
        }
        
        successful_auths = []  # Список успешных авторизаций
        
        for i, file_path in enumerate(selected_files, 1):
            stats['total'] += 1
            
            print(f"\n[{i}/{len(selected_files)}] 🔍 Обрабатываем: {file_path.name}")
            
            # Извлекаем куку из файла
            cookie_data = self.extract_target_cookie(file_path)
            
            if cookie_data is None:
                print(f"  ⚠️  Кука '{self.target_cookie_name}' не найдена")
                stats['no_cookie'] += 1
                continue
            
            stats['found_cookies'] += 1
            print(f"  ✅ Кука найдена, value: {cookie_data['value'][:50]}...")
            
            # Тестируем авторизацию
            is_success, details = self.test_cookie_authorization(cookie_data, file_path.name)
            
            if is_success:
                stats['successful_auth'] += 1
                successful_auths.append(file_path.name)
                print(f"  {details}")
            else:
                stats['failed_auth'] += 1
                print(f"  {details}")
        
        # Выводим итоговую статистику
        self._print_final_statistics(stats, successful_auths)

    def _print_final_statistics(self, stats: Dict[str, int], successful_auths: List[str]) -> None:
        """Выводит итоговую статистику тестирования"""
        print("\n" + "=" * 80)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 80)
        print(f"📁 Всего файлов обработано: {stats['total']}")
        print(f"🍪 Файлов с кукой '{self.target_cookie_name}': {stats['found_cookies']}")
        print(f"✅ Успешных авторизаций: {stats['successful_auth']}")
        print(f"❌ Неудачных авторизаций: {stats['failed_auth']}")
        print(f"⚠️  Файлов без нужной куки: {stats['no_cookie']}")
        
        # Вычисляем процент успеха
        if stats['found_cookies'] > 0:
            success_rate = (stats['successful_auth'] / stats['found_cookies']) * 100
            print(f"📈 Процент успешных авторизаций: {success_rate:.1f}%")
        
        # Показываем список успешных файлов
        if successful_auths:
            print(f"\n🎉 ФАЙЛЫ С УСПЕШНОЙ АВТОРИЗАЦИЕЙ:")
            for auth_file in successful_auths:
                print(f"  ✅ {auth_file}")
        
        print("=" * 80)


def main():
    """
    Главная функция для запуска скрипта
    
    Эта функция координирует весь процесс:
    1. Создает экземпляр тестера
    2. Получает список файлов
    3. Позволяет пользователю выбрать файлы
    4. Запускает тестирование
    """
    print("🍪 МАССОВЫЙ ТЕСТЕР КУК test_joint_session")
    print("=" * 50)
    print("Скрипт для автоматической проверки авторизации")
    print("на сайте ca.bll.by с использованием сохраненных кук")
    print("=" * 50)
    
    try:
        # Инициализируем тестер
        tester = CookieTester()
        
        # Получаем список файлов с куками
        cookie_files = tester.get_cookie_files()
        
        if not cookie_files:
            print("❌ Файлы с куками не найдены в папке D:\\Bll_tests\\cookies\\")
            return
        
        # Показываем меню выбора и получаем выбранные файлы
        selected_files = tester.display_file_menu(cookie_files)
        
        # Запускаем тестирование
        tester.run_batch_test(selected_files)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("💡 Обратитесь к техническому лидеру за помощью")


if __name__ == "__main__":
    main()
