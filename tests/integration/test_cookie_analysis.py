#!/usr/bin/env python3
"""
Локальный тест для анализа куки без подключения к серверу.
Проверяет содержимое, валидность и структуру сохраненных куки.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.logger import setup_logger

logger = setup_logger(__name__)

def analyze_cookie_file(cookie_file_path: Path) -> Dict[str, Any]:
    """
    Анализирует файл куки и возвращает детальную информацию.
    
    Args:
        cookie_file_path: Путь к файлу с куками
        
    Returns:
        Словарь с результатами анализа
    """
    try:
        if not cookie_file_path.exists():
            return {
                'success': False,
                'error': f'Файл не найден: {cookie_file_path}'
            }
            
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            
        if not isinstance(cookies, list):
            return {
                'success': False,
                'error': 'Неверный формат файла: ожидается список куки'
            }
            
        current_time = datetime.now().timestamp()
        analysis = {
            'success': True,
            'file_path': str(cookie_file_path),
            'user_login': cookie_file_path.stem.replace('_cookies', ''),
            'file_size_kb': round(cookie_file_path.stat().st_size / 1024, 2),
            'total_cookies': len(cookies),
            'valid_cookies': 0,
            'expired_cookies': 0,
            'session_cookies': 0,
            'auth_cookies': [],
            'important_cookies': [],
            'domains': set(),
            'cookie_details': []
        }
        
        # Ключевые слова для поиска куки авторизации
        auth_keywords = ['remember', 'session', 'auth', 'login', 'token', 'jwt', 'csrf']
        
        for cookie in cookies:
            cookie_name = cookie.get('name', '')
            cookie_value = cookie.get('value', '')
            cookie_domain = cookie.get('domain', '')
            cookie_expires = cookie.get('expires', -1)
            
            # Добавляем домен в набор
            analysis['domains'].add(cookie_domain)
            
            # Анализируем срок действия
            if cookie_expires == -1:
                analysis['session_cookies'] += 1
                status = 'session'
            elif cookie_expires > current_time:
                analysis['valid_cookies'] += 1
                status = 'valid'
            else:
                analysis['expired_cookies'] += 1
                status = 'expired'
                
            # Ищем куки авторизации
            is_auth_cookie = any(keyword in cookie_name.lower() for keyword in auth_keywords)
            if is_auth_cookie:
                analysis['auth_cookies'].append({
                    'name': cookie_name,
                    'domain': cookie_domain,
                    'status': status,
                    'size': len(cookie_value),
                    'expires': cookie_expires
                })
                
            # Ищем важные куки
            if is_auth_cookie or 'bll.by' in cookie_domain:
                analysis['important_cookies'].append({
                    'name': cookie_name,
                    'domain': cookie_domain,
                    'status': status,
                    'value_preview': cookie_value[:50] + '...' if len(cookie_value) > 50 else cookie_value
                })
                
            # Детальная информация для всех куки
            analysis['cookie_details'].append({
                'name': cookie_name,
                'domain': cookie_domain,
                'status': status,
                'secure': cookie.get('secure', False),
                'httpOnly': cookie.get('httpOnly', False),
                'sameSite': cookie.get('sameSite', 'None'),
                'size': len(cookie_value)
            })
        
        # Преобразуем set в list для JSON сериализации
        analysis['domains'] = list(analysis['domains'])
        
        return analysis
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Ошибка анализа файла {cookie_file_path}: {e}'
        }

def test_multiple_cookie_files(cookies_dir: Path, max_files: int = 5) -> Dict[str, Any]:
    """
    Тестирует несколько файлов куки.
    
    Args:
        cookies_dir: Директория с куками
        max_files: Максимальное количество файлов для анализа
        
    Returns:
        Результаты анализа всех файлов
    """
    print(f"🔍 Анализ куки в директории: {cookies_dir}")
    print("=" * 80)
    
    # Находим файлы куки
    cookie_files = list(cookies_dir.glob("*_cookies.json"))
    
    if not cookie_files:
        print("❌ Файлы куки не найдены")
        return {'success': False, 'error': 'Файлы куки не найдены'}
    
    print(f"📁 Найдено {len(cookie_files)} файлов куки")
    
    # Сортируем по времени последнего изменения (самые свежие первыми)
    cookie_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Берем только нужное количество файлов
    files_to_analyze = cookie_files[:max_files]
    print(f"🎯 Анализируем {len(files_to_analyze)} самых свежих файлов:")
    
    results = {
        'success': True,
        'total_files_found': len(cookie_files),
        'analyzed_files': len(files_to_analyze),
        'results': []
    }
    
    for i, cookie_file in enumerate(files_to_analyze, 1):
        print(f"\n📋 ФАЙЛ {i}: {cookie_file.name}")
        print(f"   📅 Последнее изменение: {datetime.fromtimestamp(cookie_file.stat().st_mtime)}")
        
        analysis = analyze_cookie_file(cookie_file)
        results['results'].append(analysis)
        
        if analysis['success']:
            print(f"   👤 Пользователь: {analysis['user_login']}")
            print(f"   📊 Всего куки: {analysis['total_cookies']}")
            print(f"   ✅ Валидных: {analysis['valid_cookies']}")
            print(f"   ⏰ Сессионных: {analysis['session_cookies']}")
            print(f"   ❌ Просроченных: {analysis['expired_cookies']}")
            print(f"   🔑 Куки авторизации: {len(analysis['auth_cookies'])}")
            print(f"   🌐 Домены: {', '.join(analysis['domains'])}")
            
            # Показываем важные куки авторизации
            if analysis['auth_cookies']:
                print(f"   🔐 Куки авторизации:")
                for auth_cookie in analysis['auth_cookies']:
                    status_emoji = "✅" if auth_cookie['status'] == 'valid' else "⏰" if auth_cookie['status'] == 'session' else "❌"
                    print(f"      {status_emoji} {auth_cookie['name']} ({auth_cookie['domain']}) - {auth_cookie['size']} байт")
        else:
            print(f"   ❌ Ошибка: {analysis['error']}")
    
    return results

def generate_summary_report(results: Dict[str, Any]) -> None:
    """
    Генерирует итоговый отчет по анализу куки.
    
    Args:
        results: Результаты анализа всех файлов
    """
    print("\n" + "=" * 80)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ПО АНАЛИЗУ КУКИ")
    print("=" * 80)
    
    if not results['success']:
        print(f"❌ Анализ не удался: {results.get('error', 'Неизвестная ошибка')}")
        return
    
    successful_analyses = [r for r in results['results'] if r['success']]
    failed_analyses = [r for r in results['results'] if not r['success']]
    
    print(f"📁 Всего найдено файлов куки: {results['total_files_found']}")
    print(f"🔍 Проанализировано файлов: {results['analyzed_files']}")
    print(f"✅ Успешных анализов: {len(successful_analyses)}")
    print(f"❌ Неудачных анализов: {len(failed_analyses)}")
    
    if successful_analyses:
        # Статистика по всем файлам
        total_cookies = sum(r['total_cookies'] for r in successful_analyses)
        total_valid = sum(r['valid_cookies'] for r in successful_analyses)
        total_session = sum(r['session_cookies'] for r in successful_analyses)
        total_expired = sum(r['expired_cookies'] for r in successful_analyses)
        total_auth_cookies = sum(len(r['auth_cookies']) for r in successful_analyses)
        
        print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
        print(f"   🍪 Всего куки: {total_cookies}")
        print(f"   ✅ Валидных куки: {total_valid}")
        print(f"   ⏰ Сессионных куки: {total_session}")
        print(f"   ❌ Просроченных куки: {total_expired}")
        print(f"   🔑 Куки авторизации: {total_auth_cookies}")
        
        # Находим пользователей с действующими куками авторизации
        users_with_valid_auth = []
        for analysis in successful_analyses:
            valid_auth_cookies = [c for c in analysis['auth_cookies'] if c['status'] in ['valid', 'session']]
            if valid_auth_cookies:
                users_with_valid_auth.append({
                    'user': analysis['user_login'],
                    'auth_cookies_count': len(valid_auth_cookies),
                    'file_path': analysis['file_path']
                })
        
        if users_with_valid_auth:
            print(f"\n🎯 ПОЛЬЗОВАТЕЛИ С ДЕЙСТВУЮЩИМИ КУКАМИ АВТОРИЗАЦИИ:")
            for user_info in users_with_valid_auth:
                print(f"   ✅ {user_info['user']} - {user_info['auth_cookies_count']} куки авторизации")
                print(f"      📁 Файл: {Path(user_info['file_path']).name}")
        else:
            print(f"\n⚠️ НЕ НАЙДЕНО ПОЛЬЗОВАТЕЛЕЙ С ДЕЙСТВУЮЩИМИ КУКАМИ АВТОРИЗАЦИИ")
    
    if failed_analyses:
        print(f"\n❌ ОШИБКИ АНАЛИЗА:")
        for analysis in failed_analyses:
            print(f"   ❌ {analysis.get('error', 'Неизвестная ошибка')}")

def main():
    """Основная функция тестирования куки."""
    print("🚀 Запуск анализа куки без подключения к серверу")
    print("=" * 80)
    
    # Путь к директории с куками
    cookies_dir = Path("D:/Bll_tests/cookies")
    
    if not cookies_dir.exists():
        print(f"❌ Директория с куками не найдена: {cookies_dir}")
        return False
    
    # Анализируем файлы куки
    results = test_multiple_cookie_files(cookies_dir, max_files=10)
    
    # Генерируем итоговый отчет
    generate_summary_report(results)
    
    # Рекомендации для тестирования
    print(f"\n💡 РЕКОМЕНДАЦИИ ДЛЯ JUNIOR QA:")
    print(f"   1. Обратите внимание на куки с 'remember' в названии - это куки 'Запомнить меня'")
    print(f"   2. Сессионные куки (expires: -1) действуют только до закрытия браузера")
    print(f"   3. Валидные куки с длительным сроком позволяют автоматически входить в систему")
    print(f"   4. Куки для домена '.bll.by' - самые важные для авторизации на сайте")
    print(f"   5. Большой размер куки (>1000 байт) обычно указывает на токены авторизации")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
