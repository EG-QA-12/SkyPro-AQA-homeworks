#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладочная версия для выяснения проблемы с подстановкой кук

Проблема: Playwright не может подставить куку так же, как это делается вручную
Цель: Найти точную причину и исправить подстановку

Автор: SDET-Архитектор
"""

import json
import asyncio
import urllib.parse
from pathlib import Path
from typing import Dict, Optional
from playwright.async_api import async_playwright


class DebugCookieTester:
    """
    Отладочный класс для поиска проблемы с подстановкой кук
    """
    
    def __init__(self, cookies_dir: str = "D:\\Bll_tests\\cookies"):
        self.cookies_dir = Path(cookies_dir)
        self.target_cookie_name = "test_joint_session"
        self.login_url = "https://ca.bll.by/login"
        self.main_url = "https://ca.bll.by"
        
    def extract_target_cookie(self, file_path: Path) -> Optional[Dict]:
        """Извлекает куку из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            for cookie in cookies_data:
                if cookie.get('name') == self.target_cookie_name:
                    return cookie
                    
            return None
            
        except Exception as e:
            print(f"❌ Ошибка чтения файла {file_path.name}: {e}")
            return None

    async def debug_cookie_methods(self, file_name: str = "474_cookies.json"):
        """
        Тестирует разные способы подстановки кук
        """
        print(f"🔍 ОТЛАДКА ПОДСТАНОВКИ КУК для файла: {file_name}")
        print("=" * 70)
        
        # Извлекаем куку
        file_path = self.cookies_dir / file_name
        cookie_data = self.extract_target_cookie(file_path)
        if cookie_data is None:
            print(f"❌ Кука не найдена в файле {file_name}")
            return
        
        print(f"✅ Кука найдена:")
        print(f"   📋 Name: {cookie_data['name']}")
        print(f"   📋 Value: {cookie_data['value'][:50]}...")
        print(f"   🌐 Domain: {cookie_data.get('domain', 'не указан')}")
        print(f"   📁 Path: {cookie_data.get('path', 'не указан')}")
        print(f"   🔒 HttpOnly: {cookie_data.get('httpOnly', 'не указан')}")
        print(f"   🛡️  Secure: {cookie_data.get('secure', 'не указан')}")
        print(f"   🔄 SameSite: {cookie_data.get('sameSite', 'не указан')}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=2000,  # Еще больше замедляем
                args=['--start-maximized']
            )
            
            context = await browser.new_context(
                viewport=None,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            try:
                print("\n🌐 Открываем страницу логина...")
                await page.goto(self.login_url, wait_until='networkidle')
                await asyncio.sleep(3)
                
                print("\n🧹 Очищаем существующие куки...")
                await context.clear_cookies()
                
                # Проверяем, что куки действительно очищены
                existing_cookies = await context.cookies()
                print(f"✅ Кук после очистки: {len(existing_cookies)}")
                
                print("\n🔬 ТЕСТИРУЕМ РАЗНЫЕ СПОСОБЫ ПОДСТАНОВКИ КУК:")
                print("-" * 50)
                
                # СПОСОБ 1: Стандартный add_cookies
                print("\n📌 СПОСОБ 1: context.add_cookies() - стандартный")
                
                # Декодируем значение куки
                decoded_value = urllib.parse.unquote(cookie_data['value'])
                print(f"   🔓 Декодированное значение: {decoded_value[:50]}...")
                
                playwright_cookie_v1 = {
                    'name': cookie_data['name'],
                    'value': decoded_value,  # Используем декодированное значение
                    'domain': 'ca.bll.by',  # Убираем точку в начале
                    'path': '/',
                    'httpOnly': False,
                    'secure': True,
                    'sameSite': 'Lax'
                }
                
                await context.add_cookies([playwright_cookie_v1])
                
                # Проверяем, что кука добавилась
                cookies_after_add = await context.cookies()
                print(f"   ✅ Кук после добавления: {len(cookies_after_add)}")
                
                target_cookie = None
                for c in cookies_after_add:
                    if c['name'] == self.target_cookie_name:
                        target_cookie = c
                        break
                
                if target_cookie:
                    print(f"   ✅ Целевая кука найдена в браузере:")
                    print(f"      📋 Name: {target_cookie['name']}")
                    print(f"      📋 Value: {target_cookie['value'][:50]}...")
                    print(f"      🌐 Domain: {target_cookie['domain']}")
                else:
                    print("   ❌ Целевая кука НЕ найдена в браузере!")
                
                print("\n🔄 Обновляем страницу...")
                await page.reload(wait_until='networkidle')
                await asyncio.sleep(3)
                
                # Проверяем результат
                current_url = page.url
                print(f"📍 URL после обновления: {current_url}")
                
                if '/login' not in current_url:
                    print("🎉 УСПЕХ! Произошел редирект - авторизация работает!")
                else:
                    print("❌ Остались на странице логина")
                    
                    # СПОСОБ 2: Попробуем через JavaScript
                    print("\n📌 СПОСОБ 2: Подстановка через JavaScript")
                    
                    js_cookie_script = f"""
                    document.cookie = '{cookie_data['name']}={cookie_data['value']}; path=/; domain=.bll.by; secure; samesite=lax';
                    console.log('Cookie set via JS:', document.cookie);
                    """
                    
                    await page.evaluate(js_cookie_script)
                    await asyncio.sleep(2)
                    
                    print("🔄 Обновляем страницу после JS...")
                    await page.reload(wait_until='networkidle')
                    await asyncio.sleep(3)
                    
                    current_url_v2 = page.url
                    print(f"📍 URL после JS: {current_url_v2}")
                    
                    if '/login' not in current_url_v2:
                        print("🎉 УСПЕХ! JavaScript подстановка сработала!")
                    else:
                        print("❌ JavaScript подстановка тоже не сработала")
                        
                        # СПОСОБ 3: Точное копирование оригинальных параметров
                        print("\n📌 СПОСОБ 3: Точное копирование оригинала")
                        
                        exact_cookie = {
                            'name': cookie_data['name'],
                            'value': cookie_data['value'],  # Без декодирования!
                            'domain': cookie_data['domain'],  # Точно как в файле
                            'path': cookie_data['path'],
                            'httpOnly': cookie_data.get('httpOnly', False),
                            'secure': cookie_data.get('secure', True),
                            'sameSite': cookie_data.get('sameSite', 'Lax')
                        }
                        
                        await context.clear_cookies()
                        await context.add_cookies([exact_cookie])
                        
                        print("🔄 Обновляем страницу с точной копией...")
                        await page.reload(wait_until='networkidle')
                        await asyncio.sleep(3)
                        
                        current_url_v3 = page.url
                        print(f"📍 URL после точной копии: {current_url_v3}")
                        
                        if '/login' not in current_url_v3:
                            print("🎉 УСПЕХ! Точная копия сработала!")
                        else:
                            print("❌ Даже точная копия не работает")
                
                print(f"\n💡 Браузер остается открытым для анализа...")
                print(f"🔍 Попробуйте вручную подставить куку и посмотрите разницу")
                print(f"📋 Кука для ручной подстановки:")
                print(f"   Name: {cookie_data['name']}")
                print(f"   Value: {cookie_data['value']}")
                input("Нажмите Enter после анализа...")
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                input("Нажмите Enter для завершения...")
            
            finally:
                await browser.close()


async def main():
    """Запуск отладки"""
    tester = DebugCookieTester()
    await tester.debug_cookie_methods("474_cookies.json")


if __name__ == "__main__":
    asyncio.run(main())
