#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенная отладка подстановки кук без таймаутов
"""

import json
import asyncio
import urllib.parse
from pathlib import Path
from typing import Dict, Optional
from playwright.async_api import async_playwright


async def test_cookie_simple():
    """Простая отладка подстановки кук"""
    
    # Читаем куку из файла
    cookies_dir = Path("D:/Bll_tests/cookies")
    file_path = cookies_dir / "474_cookies.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        cookies_data = json.load(f)
    
    target_cookie = None
    for cookie in cookies_data:
        if cookie.get('name') == 'test_joint_session':
            target_cookie = cookie
            break
    
    if not target_cookie:
        print("❌ Кука не найдена")
        return
    
    print(f"✅ Кука найдена: {target_cookie['value'][:50]}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=1000,
            args=['--start-maximized']
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌐 Переходим на страницу логина...")
            await page.goto("https://ca.bll.by/login", timeout=60000)
            await asyncio.sleep(2)
            
            print("🧹 Очищаем куки...")
            await context.clear_cookies()
            
            print("🍪 Добавляем куку через Playwright...")
            
            # Пробуем несколько вариантов
            variants = [
                # Вариант 1: Точная копия
                {
                    'name': target_cookie['name'],
                    'value': target_cookie['value'],
                    'domain': '.bll.by',
                    'path': '/',
                    'httpOnly': False,
                    'secure': True,
                    'sameSite': 'Lax'
                },
                # Вариант 2: Без точки в домене
                {
                    'name': target_cookie['name'],
                    'value': target_cookie['value'], 
                    'domain': 'ca.bll.by',
                    'path': '/',
                    'httpOnly': False,
                    'secure': True,
                    'sameSite': 'Lax'
                },
                # Вариант 3: Декодированное значение
                {
                    'name': target_cookie['name'],
                    'value': urllib.parse.unquote(target_cookie['value']),
                    'domain': 'ca.bll.by',
                    'path': '/',
                    'httpOnly': False,
                    'secure': True,
                    'sameSite': 'Lax'
                }
            ]
            
            for i, variant in enumerate(variants, 1):
                print(f"\n📌 Тестируем вариант {i}...")
                print(f"   Domain: {variant['domain']}")
                print(f"   Value decoded: {'Да' if variant['value'] != target_cookie['value'] else 'Нет'}")
                
                # Очищаем и добавляем куку
                await context.clear_cookies()
                await context.add_cookies([variant])
                
                # Проверяем, что кука добавилась
                cookies = await context.cookies()
                found = any(c['name'] == 'test_joint_session' for c in cookies)
                print(f"   Кука добавлена: {'Да' if found else 'Нет'}")
                
                # Обновляем страницу
                await page.reload()
                await asyncio.sleep(2)
                
                current_url = page.url
                print(f"   Результат: {current_url}")
                
                if '/login' not in current_url:
                    print(f"🎉 ВАРИАНТ {i} СРАБОТАЛ!")
                    break
                else:
                    print(f"❌ Вариант {i} не сработал")
            
            # Если ничего не сработало, попробуем JavaScript
            print(f"\n📌 Тестируем JavaScript...")
            js_script = f"""
            document.cookie = '{target_cookie['name']}={target_cookie['value']}; domain=.bll.by; path=/; secure; samesite=lax';
            console.log('Cookie set:', document.cookie);
            """
            
            await page.evaluate(js_script)
            await asyncio.sleep(1)
            await page.reload()
            await asyncio.sleep(2)
            
            final_url = page.url
            print(f"   JavaScript результат: {final_url}")
            
            if '/login' not in final_url:
                print("🎉 JAVASCRIPT СРАБОТАЛ!")
            else:
                print("❌ JavaScript тоже не сработал")
            
            print(f"\n💡 Браузер открыт для ручного тестирования")
            print(f"📋 Данные куки:")
            print(f"   Name: {target_cookie['name']}")  
            print(f"   Value: {target_cookie['value']}")
            print(f"🔍 Попробуйте добавить куку вручную и посмотрите, что изменится")
            
            input("Нажмите Enter после анализа...")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            input("Enter для завершения...")
        
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_cookie_simple())
