#!/usr/bin/env python3
"""
Комплексный тест авторизации через куки.
Проверяет работу авторизации с множественными файлами куки и создает отчет.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Добавляем корень проекта в PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.logger import setup_logger

logger = setup_logger(__name__)

class CookieAuthTester:
    """
    Класс для комплексного тестирования авторизации через куки.
    Предназначен для Junior QA как обучающий материал.
    """
    
    def __init__(self, cookies_dir: Path):
        """
        Инициализирует тестер куки.
        
        Args:
            cookies_dir: Директория с файлами куки
        """
        self.cookies_dir = cookies_dir
        self.results = {
            'test_start_time': datetime.now().isoformat(),
            'total_files_tested': 0,
            'successful_authentications': 0,
            'failed_authentications': 0,
            'skipped_files': 0,
            'detailed_results': [],
            'summary': {}
        }
        
    def validate_cookie_file(self, cookie_file: Path) -> Dict[str, Any]:
        """
        Проверяет валидность файла куки.
        
        Args:
            cookie_file: Путь к файлу куки
            
        Returns:
            Результат валидации
        """
        validation_result = {
            'file_path': str(cookie_file),
            'file_name': cookie_file.name,
            'user_id': cookie_file.stem.replace('_cookies', ''),
            'is_valid': False,
            'file_size_kb': 0,
            'total_cookies': 0,
            'auth_cookies': [],
            'validation_errors': []
        }
        
        try:
            # Проверяем существование файла
            if not cookie_file.exists():
                validation_result['validation_errors'].append('Файл не существует')
                return validation_result
                
            # Проверяем размер файла
            file_size = cookie_file.stat().st_size
            validation_result['file_size_kb'] = round(file_size / 1024, 2)
            
            if file_size == 0:
                validation_result['validation_errors'].append('Файл пустой')
                return validation_result
                
            # Проверяем JSON структуру
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
                
            if not isinstance(cookies, list):
                validation_result['validation_errors'].append('Неверная структура JSON: ожидается список')
                return validation_result
                
            validation_result['total_cookies'] = len(cookies)
            
            # Анализируем куки авторизации
            current_time = datetime.now().timestamp()
            auth_keywords = ['remember', 'session', 'auth', 'login', 'token', 'xsrf']
            
            for cookie in cookies:
                cookie_name = cookie.get('name', '')
                cookie_domain = cookie.get('domain', '')
                cookie_expires = cookie.get('expires', -1)
                
                # Ищем куки авторизации
                if any(keyword in cookie_name.lower() for keyword in auth_keywords):
                    # Определяем статус куки
                    if cookie_expires == -1:
                        status = 'session'
                    elif cookie_expires > current_time:
                        status = 'valid'
                    else:
                        status = 'expired'
                        
                    validation_result['auth_cookies'].append({
                        'name': cookie_name,
                        'domain': cookie_domain,
                        'status': status,
                        'size': len(cookie.get('value', '')),
                        'expires': cookie_expires
                    })
            
            # Определяем общую валидность
            has_valid_auth_cookies = any(
                c['status'] in ['valid', 'session'] for c in validation_result['auth_cookies']
            )
            
            if validation_result['total_cookies'] > 0 and has_valid_auth_cookies:
                validation_result['is_valid'] = True
            else:
                validation_result['validation_errors'].append(
                    'Нет действующих куки авторизации'
                )
                
        except json.JSONDecodeError as e:
            validation_result['validation_errors'].append(f'Ошибка парсинга JSON: {e}')
        except Exception as e:
            validation_result['validation_errors'].append(f'Неожиданная ошибка: {e}')
            
        return validation_result
    
    def simulate_authentication(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Симулирует процесс авторизации на основе анализа куки.
        
        Args:
            validation_result: Результат валидации куки
            
        Returns:
            Результат симуляции авторизации
        """
        auth_result = {
            'user_id': validation_result['user_id'],
            'authentication_successful': False,
            'authentication_method': 'unknown',
            'session_type': 'unknown',
            'security_level': 'low',
            'recommendations': [],
            'auth_details': {}
        }
        
        if not validation_result['is_valid']:
            auth_result['recommendations'].append(
                'Файл куки невалиден или поврежден - требуется повторная авторизация'
            )
            return auth_result
            
        # Анализируем типы куки авторизации
        remember_cookies = [c for c in validation_result['auth_cookies'] 
                          if 'remember' in c['name'].lower()]
        session_cookies = [c for c in validation_result['auth_cookies'] 
                         if 'session' in c['name'].lower()]
        xsrf_cookies = [c for c in validation_result['auth_cookies'] 
                       if 'xsrf' in c['name'].lower() or 'csrf' in c['name'].lower()]
        
        # Определяем метод авторизации
        if remember_cookies:
            # Проверяем действительность "remember me" куки
            valid_remember = [c for c in remember_cookies if c['status'] in ['valid', 'session']]
            if valid_remember:
                auth_result['authentication_successful'] = True
                auth_result['authentication_method'] = 'remember_me'
                auth_result['session_type'] = 'persistent'
                auth_result['security_level'] = 'medium'
                auth_result['auth_details']['remember_cookie'] = valid_remember[0]
                
                # Рекомендации для Junior QA
                auth_result['recommendations'].extend([
                    'Пользователь использует функцию "Запомнить меня"',
                    'Сессия сохраняется между закрытиями браузера',
                    'Проверьте срок действия куки для оценки безопасности'
                ])
                
        elif session_cookies:
            # Проверяем сессионные куки
            valid_session = [c for c in session_cookies if c['status'] in ['valid', 'session']]
            if valid_session:
                auth_result['authentication_successful'] = True
                auth_result['authentication_method'] = 'session'
                auth_result['session_type'] = 'temporary'
                auth_result['security_level'] = 'high'
                auth_result['auth_details']['session_cookie'] = valid_session[0]
                
                auth_result['recommendations'].extend([
                    'Пользователь авторизован через временную сессию',
                    'Сессия завершится при закрытии браузера',
                    'Более безопасный тип авторизации'
                ])
        
        # Проверяем наличие CSRF защиты
        if xsrf_cookies:
            valid_xsrf = [c for c in xsrf_cookies if c['status'] in ['valid', 'session']]
            if valid_xsrf:
                auth_result['security_level'] = 'high'
                auth_result['auth_details']['csrf_protection'] = True
                auth_result['recommendations'].append(
                    'Обнаружена CSRF защита - хороший уровень безопасности'
                )
        
        # Если нет специфичных куки, но есть другие валидные куки авторизации
        if not auth_result['authentication_successful']:
            other_auth_cookies = [c for c in validation_result['auth_cookies'] 
                                if c['status'] in ['valid', 'session']]
            if other_auth_cookies:
                auth_result['authentication_successful'] = True
                auth_result['authentication_method'] = 'generic_auth'
                auth_result['session_type'] = 'unknown'
                auth_result['auth_details']['generic_cookies'] = other_auth_cookies
                
                auth_result['recommendations'].append(
                    'Обнаружены куки авторизации неизвестного типа - требует дополнительного анализа'
                )
        
        return auth_result
    
    def test_all_cookie_files(self, max_files: Optional[int] = None) -> None:
        """
        Тестирует все файлы куки в директории.
        
        Args:
            max_files: Максимальное количество файлов для тестирования (None = все)
        """
        print(f"🚀 Начало комплексного тестирования авторизации через куки")
        print(f"📁 Директория: {self.cookies_dir}")
        print("=" * 80)
        
        # Находим все файлы куки
        cookie_files = list(self.cookies_dir.glob("*_cookies.json"))
        
        if not cookie_files:
            print("❌ Файлы куки не найдены")
            return
            
        # Сортируем по времени модификации (новые первыми)
        cookie_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Ограничиваем количество файлов, если указано
        if max_files:
            cookie_files = cookie_files[:max_files]
            
        print(f"🎯 Найдено файлов куки для тестирования: {len(cookie_files)}")
        print()
        
        # Тестируем каждый файл
        for i, cookie_file in enumerate(cookie_files, 1):
            print(f"📋 ТЕСТ {i}/{len(cookie_files)}: {cookie_file.name}")
            print(f"   📅 Изменен: {datetime.fromtimestamp(cookie_file.stat().st_mtime)}")
            
            # Валидация файла куки
            validation_result = self.validate_cookie_file(cookie_file)
            
            if validation_result['is_valid']:
                print(f"   ✅ Файл валиден")
                print(f"   📊 Куки: {validation_result['total_cookies']} (авторизация: {len(validation_result['auth_cookies'])})")
                
                # Симуляция авторизации
                auth_result = self.simulate_authentication(validation_result)
                
                if auth_result['authentication_successful']:
                    print(f"   🔐 Авторизация: УСПЕШНА")
                    print(f"   🎯 Метод: {auth_result['authentication_method']}")
                    print(f"   🛡️ Безопасность: {auth_result['security_level']}")
                    print(f"   ⏱️ Тип сессии: {auth_result['session_type']}")
                    self.results['successful_authentications'] += 1
                else:
                    print(f"   ❌ Авторизация: НЕУСПЕШНА")
                    self.results['failed_authentications'] += 1
                    
                # Показываем рекомендации
                if auth_result['recommendations']:
                    print(f"   💡 Рекомендации:")
                    for rec in auth_result['recommendations'][:2]:  # Показываем первые 2
                        print(f"      • {rec}")
                        
            else:
                print(f"   ❌ Файл невалиден: {', '.join(validation_result['validation_errors'])}")
                self.results['skipped_files'] += 1
                auth_result = {'authentication_successful': False, 'user_id': validation_result['user_id']}
            
            # Сохраняем детальные результаты
            self.results['detailed_results'].append({
                'validation': validation_result,
                'authentication': auth_result
            })
            
            self.results['total_files_tested'] += 1
            print()
            
            # Небольшая пауза для наглядности
            time.sleep(0.1)
    
    def generate_final_report(self) -> None:
        """
        Генерирует итоговый отчет тестирования.
        """
        print("=" * 80)
        print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ АВТОРИЗАЦИИ")
        print("=" * 80)
        
        # Основная статистика
        total_tested = self.results['total_files_tested']
        successful = self.results['successful_authentications']
        failed = self.results['failed_authentications']
        skipped = self.results['skipped_files']
        
        success_rate = (successful / total_tested * 100) if total_tested > 0 else 0
        
        print(f"📈 СТАТИСТИКА ТЕСТИРОВАНИЯ:")
        print(f"   🎯 Всего протестировано файлов: {total_tested}")
        print(f"   ✅ Успешных авторизаций: {successful}")
        print(f"   ❌ Неуспешных авторизаций: {failed}")
        print(f"   ⏭️ Пропущено файлов: {skipped}")
        print(f"   📊 Процент успеха: {success_rate:.1f}%")
        
        # Анализ методов авторизации
        auth_methods = {}
        security_levels = {}
        session_types = {}
        
        for result in self.results['detailed_results']:
            auth = result['authentication']
            if auth['authentication_successful']:
                method = auth.get('authentication_method', 'unknown')
                security = auth.get('security_level', 'unknown')
                session = auth.get('session_type', 'unknown')
                
                auth_methods[method] = auth_methods.get(method, 0) + 1
                security_levels[security] = security_levels.get(security, 0) + 1
                session_types[session] = session_types.get(session, 0) + 1
        
        if auth_methods:
            print(f"\n🔐 МЕТОДЫ АВТОРИЗАЦИИ:")
            for method, count in auth_methods.items():
                print(f"   • {method}: {count} пользователей")
                
        if security_levels:
            print(f"\n🛡️ УРОВНИ БЕЗОПАСНОСТИ:")
            for level, count in security_levels.items():
                print(f"   • {level}: {count} пользователей")
                
        if session_types:
            print(f"\n⏱️ ТИПЫ СЕССИЙ:")
            for session_type, count in session_types.items():
                print(f"   • {session_type}: {count} пользователей")
        
        # Рекомендации для команды
        print(f"\n💡 РЕКОМЕНДАЦИИ ДЛЯ КОМАНДЫ QA:")
        print(f"   1. Обратите внимание на пользователей с 'remember_me' авторизацией")
        print(f"   2. Проверьте сроки действия persistent сессий для безопасности")
        print(f"   3. Убедитесь, что CSRF защита работает корректно")
        print(f"   4. Мониторьте пользователей с низким уровнем безопасности")
        print(f"   5. Регулярно очищайте просроченные куки из тестовых данных")
        
        # Сохраняем отчет в файл
        report_file = project_root / "logs" / f"cookie_auth_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2, default=str)
            
        print(f"\n📄 Детальный отчет сохранен: {report_file}")

def main():
    """Основная функция тестирования."""
    print("🍪 Комплексное тестирование авторизации через куки")
    print("=" * 80)
    
    # Инициализируем тестер
    cookies_dir = Path("D:/Bll_tests/cookies")
    tester = CookieAuthTester(cookies_dir)
    
    # Запускаем тестирование (ограничиваем 15 файлами для демонстрации)
    tester.test_all_cookie_files(max_files=15)
    
    # Генерируем итоговый отчет
    tester.generate_final_report()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
