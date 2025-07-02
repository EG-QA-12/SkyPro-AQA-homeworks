#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI тестер кук test_joint_session на Playwright

Этот скрипт точно повторяет ваши ручные действия:
1. Открывает браузер в GUI режиме
2. Переходит на ca.bll.by
3. Очищает все куки  
4. Переходит на ca.bll.by/login
5. Подставляет только куку test_joint_session
6. Проверяет результат авторизации

Автор: SDET-Архитектор
Цель: Отладка и повторение ручного процесса для всех участников команды
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Optional
from playwright.async_api import async_playwright, Page, BrowserContext, Browser


class PlaywrightCookieTester:
    """
    Класс для тестирования кук с использованием Playwright в GUI режиме
    
    Полностью повторяет ручной процесс:
    - Открытие браузера с GUI
    - Очистка всех кук
    - Подстановка только test_joint_session
    - Визуальная проверка результата
    """
    
    def __init__(self, cookies_dir: str = "D:\\Bll_tests\\cookies"):
        """
        Инициализация тестера на Playwright
        
        Args:
            cookies_dir (str): Путь к папке с JSON-файлами кук
        """
        self.cookies_dir = Path(cookies_dir)
        self.target_cookie_name = "test_joint_session"
        self.login_url = "https://ca.bll.by/login"
        self.main_url = "https://ca.bll.by"
        
    def extract_target_cookie(self, file_path: Path) -> Optional[Dict]:
        """
        Извлекает куку test_joint_session из JSON-файла
        
        Args:
            file_path (Path): Путь к JSON-файлу с куками
            
        Returns:
            Optional[Dict]: Данные куки или None если не найдена
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # Ищем нужную куку
            for cookie in cookies_data:
                if cookie.get('name') == self.target_cookie_name:
                    return cookie
                    
            return None
            
        except Exception as e:
            print(f"❌ Ошибка чтения файла {file_path.name}: {e}")
            return None

    async def test_cookie_with_gui(self, file_name: str) -> None:
        """
        Тестирует куку в GUI режиме, точно повторяя ваши действия
        
        Args:
            file_name (str): Имя файла с кукой для тестирования
        """
        print(f"🚀 Начинаем GUI тестирование файла: {file_name}")
        print("👀 Браузер откроется в видимом режиме для наблюдения")
        
        # Извлекаем куку из файла
        file_path = self.cookies_dir / file_name
        if not file_path.exists():
            print(f"❌ Файл {file_name} не найден")
            return
            
        cookie_data = self.extract_target_cookie(file_path)
        if cookie_data is None:
            print(f"⚠️  Кука '{self.target_cookie_name}' не найдена в файле {file_name}")
            return
        
        print(f"✅ Кука найдена: {cookie_data['value'][:50]}...")
        
        async with async_playwright() as p:
            # Запускаем браузер в GUI режиме (НЕ headless)
            print("🌐 Открываем браузер Chrome в видимом режиме...")
            browser = await p.chromium.launch(
                headless=False,  # Видимый режим!
                slow_mo=1000,    # Замедляем действия для наблюдения
                args=[
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            context = await browser.new_context(
                viewport=None,  # Используем размер окна браузера
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            try:
                # Шаг 1: Переходим на главную страницу
                print("📍 Шаг 1: Переходим на ca.bll.by")
                await page.goto(self.main_url, wait_until='load')
                await asyncio.sleep(2)  # Пауза для наблюдения
                
                # Шаг 2: Очищаем ВСЕ куки
                print("🧹 Шаг 2: Очищаем все куки")
                await context.clear_cookies()
                print("✅ Все куки очищены")
                
                # Шаг 3: Обновляем страницу для проверки (должна быть неавторизованная)
                print("🔄 Шаг 3: Обновляем страницу (должна быть неавторизованная)")
                await page.reload(wait_until='load')
                await asyncio.sleep(2)
                
                # Шаг 4: Переходим на страницу логина
                print("🔐 Шаг 4: Переходим на страницу логина")
                await page.goto(self.login_url, wait_until='load')
                await asyncio.sleep(2)
                
                # Шаг 5: Подставляем ТОЛЬКО куку test_joint_session
                print("🍪 Шаг 5: Подставляем куку test_joint_session")
                
                # Формируем куку в формате Playwright
                playwright_cookie = {
                    'name': cookie_data['name'],
                    'value': cookie_data['value'],
                    'domain': cookie_data.get('domain', '.bll.by').lstrip('.'),
                    'path': cookie_data.get('path', '/'),
                    'httpOnly': cookie_data.get('httpOnly', False),
                    'secure': cookie_data.get('secure', True),
                    'sameSite': cookie_data.get('sameSite', 'Lax')
                }
                
                # Добавляем куку
                await context.add_cookies([playwright_cookie])
                print(f"✅ Кука добавлена: {cookie_data['name']}")
                
                # Шаг 6: Обновляем страницу для применения куки
                print("🔄 Шаг 6: Обновляем страницу для применения куки")
                await page.reload(wait_until='load')
                await asyncio.sleep(3)
                
                # Шаг 7: Проверяем результат
                print("🔍 Шаг 7: Проверяем результат авторизации")
                
                # Получаем текущий URL
                current_url = page.url
                print(f"📍 Текущий URL: {current_url}")
                
                # Проверяем наличие индикаторов авторизации
                auth_indicators = [
                    'logout', 'выйти', 'profile', 'профиль', 
                    'dashboard', 'панель', 'settings', 'настройки'
                ]
                
                page_content = await page.content()
                page_text = page_content.lower()
                
                found_indicators = [indicator for indicator in auth_indicators if indicator in page_text]
                
                # Проверяем редирект (успешная авторизация часто ведет к редиректу)
                redirected = '/login' not in current_url
                
                print("\n" + "="*60)
                print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
                print("="*60)
                print(f"🌐 Финальный URL: {current_url}")
                print(f"🔄 Произошел редирект: {'Да' if redirected else 'Нет'}")
                print(f"🔍 Найдены индикаторы авторизации: {found_indicators}")
                
                if redirected or found_indicators:
                    print("🎉 УСПЕХ! Авторизация прошла успешно!")
                    print("✅ Кука работает корректно")
                else:
                    print("❌ Авторизация не удалась")
                    print("⚠️  Пользователь остался на странице логина")
                
                print("\n💡 Браузер останется открытым для вашего анализа.")
                print("🔍 Проверьте страницу визуально и нажмите Enter для завершения...")
                
                # Ждем ввода пользователя для анализа
                input()
                
            except Exception as e:
                print(f"❌ Ошибка во время тестирования: {e}")
                print("🔍 Браузер останется открытым для анализа ошибки")
                input("Нажмите Enter для завершения...")
            
            finally:
                await browser.close()

    async def run_interactive_test(self) -> None:
        """
        Запускает интерактивное тестирование с выбором файла
        """
        print("🍪 PLAYWRIGHT GUI ТЕСТЕР КУК test_joint_session")
        print("=" * 60)
        print("Этот скрипт откроет браузер в видимом режиме")
        print("и повторит ваши ручные действия шаг за шагом")
        print("=" * 60)
        
        # Показываем доступные файлы с test_joint_session
        print("\n🔍 Поиск файлов с кукой test_joint_session...")
        
        available_files = []
        for file_path in self.cookies_dir.glob("*.json"):
            cookie_data = self.extract_target_cookie(file_path)
            if cookie_data:
                available_files.append(file_path.name)
        
        if not available_files:
            print("❌ Файлы с кукой test_joint_session не найдены")
            return
        
        print(f"\n📁 Найдено {len(available_files)} файлов с нужной кукой:")
        for i, file_name in enumerate(available_files, 1):
            print(f"{i:2d}. {file_name}")
        
        # Предлагаем тестировать 474_cookies.json по умолчанию
        print(f"\n🎯 По умолчанию тестируем: 474_cookies.json")
        choice = input("Нажмите Enter для продолжения или введите другое имя файла: ").strip()
        
        if choice:
            file_name = choice if choice.endswith('.json') else f"{choice}.json"
        else:
            file_name = "474_cookies.json"
        
        await self.test_cookie_with_gui(file_name)


async def main():
    """
    Главная функция для запуска GUI тестирования
    """
    tester = PlaywrightCookieTester()
    await tester.run_interactive_test()


if __name__ == "__main__":
    asyncio.run(main())
