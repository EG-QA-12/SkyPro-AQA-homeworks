#!/usr/bin/env python3
"""
Быстрая проверка качества кук пользователей.
"""
import json
from pathlib import Path


def check_user_cookies():
    """Проверяет качество кук всех пользователей."""
    cookies_dir = Path("cookies")
    cookie_files = list(cookies_dir.glob("*_cookies.json"))
    
    print("АНАЛИЗ КУК ПОЛЬЗОВАТЕЛЕЙ:")
    print("-" * 40)
    
    results = []
    
    for cookie_file in sorted(cookie_files):
        username = cookie_file.stem.replace("_cookies", "")
        
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            auth_cookies = [c for c in data if c.get('name') == 'test_joint_session']
            
            if auth_cookies:
                cookie_len = len(auth_cookies[0].get('value', ''))
                status = "✅ ХОРОШАЯ" if cookie_len > 200 else "⚠️ КОРОТКАЯ" if cookie_len > 50 else "❌ ПЛОХАЯ"
                results.append((username, cookie_len, status))
                print(f"{username:12} | {cookie_len:3} символов | {status}")
            else:
                results.append((username, 0, "❌ НЕТ КУКИ"))
                print(f"{username:12} | --- символов | ❌ НЕТ КУКИ")
                
        except Exception as e:
            results.append((username, 0, "❌ ОШИБКА"))
            print(f"{username:12} | --- символов | ❌ ОШИБКА: {e}")
    
    print("\nРЕКОМЕНДАЦИИ:")
    good_users = [r for r in results if r[1] > 200]
    if good_users:
        good_users.sort(key=lambda x: x[1], reverse=True)
        print("Лучшие пользователи для тестов:")
        for user, length, status in good_users[:5]:
            print(f"  {user} ({length} символов)")
    
    bad_users = [r for r in results if r[1] < 100]
    if bad_users:
        print("Проблемные пользователи:")
        for user, length, status in bad_users:
            print(f"  {user} - {status}")


if __name__ == "__main__":
    check_user_cookies() 