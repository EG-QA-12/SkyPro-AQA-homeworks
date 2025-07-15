"""
Упрощенный тест редиректов с использованием threading.

Заменяет 20 тестов на 1-2, используя только стандартные библиотеки.
"""
from __future__ import annotations

import requests
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
import allure

from framework.utils.reporting.allure_utils import ui_test


# Конфигурация URL для проверки
REDIRECT_CONFIG = {
    # URL без редиректа (ожидаем 200-299)
    "no_redirect": [
        "https://bll.by/",
        "https://expert.bll.by/", 
        "https://cp.bll.by/"
    ],
    # URL с редиректом (ожидаем 302 -> ca.bll.by)
    "with_redirect": [
        "https://gz.bll.by/",
        "https://bonus.bll.by/"
    ]
}

TARGET_REDIRECT_PREFIX = "https://ca.bll.by/"


def check_single_url(url: str, expect_redirect: bool) -> Dict:
    """
    Проверяет один URL и возвращает результат.
    
    Args:
        url: URL для проверки
        expect_redirect: ожидается ли редирект
        
    Returns:
        Словарь с результатами проверки
    """
    try:
        response = requests.head(url, allow_redirects=False, timeout=10)
        
        result = {
            'url': url,
            'status_code': response.status_code,
            'location': response.headers.get('Location', ''),
            'expect_redirect': expect_redirect,
            'success': False,
            'message': ''
        }
        
        if expect_redirect:
            # Ожидаем редирект 302 на ca.bll.by
            if response.status_code == 302 and result['location'].startswith(TARGET_REDIRECT_PREFIX):
                result['success'] = True
                result['message'] = f"✅ {url} корректно редиректит (302) → {result['location']}"
            else:
                result['message'] = f"❌ {url} НЕ редиректит (статус: {response.status_code}, location: {result['location']})"
        else:
            # Ожидаем НЕТ редиректа, статус 200-299
            if response.status_code != 302 and 200 <= response.status_code < 300:
                result['success'] = True
                result['message'] = f"✅ {url} корректен без редиректа (статус: {response.status_code})"
            else:
                result['message'] = f"❌ {url} неожиданно редиректит (статус: {response.status_code})"
                
        return result
        
    except Exception as e:
        return {
            'url': url,
            'status_code': None,
            'location': '',
            'expect_redirect': expect_redirect,
            'success': False,
            'message': f"❌ {url} недоступен: {str(e)}"
        }


@ui_test(
    title="Оптимизированная проверка всех редиректов",
    description="Проверяет все URL параллельно через ThreadPoolExecutor",
    feature="HTTP Redirects"
)
def test_all_redirects_optimized() -> None:
    """
    Оптимизированный тест всех редиректов.
    
    Заменяет 20 отдельных тестов одним быстрым.
    Использует многопоточность для ускорения.
    """
    print("\n🚀 Оптимизированная проверка редиректов")
    print("="*60)
    
    # Подготавливаем задачи
    tasks = []
    
    # Добавляем URL без редиректа
    for url in REDIRECT_CONFIG['no_redirect']:
        tasks.append((url, False))
    
    # Добавляем URL с редиректом  
    for url in REDIRECT_CONFIG['with_redirect']:
        tasks.append((url, True))
    
    results = []
    
    # Выполняем проверки параллельно
    print(f"📡 Проверяем {len(tasks)} URL в {min(len(tasks), 5)} потоках...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {
            executor.submit(check_single_url, url, expect_redirect): (url, expect_redirect)
            for url, expect_redirect in tasks
        }
        
        for future in as_completed(future_to_task):
            result = future.result()
            results.append(result)
    
    # Анализируем результаты
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"\n📊 Результаты проверки:")
    for result in sorted(results, key=lambda x: x['url']):
        print(f"   {result['message']}")
    
    # Добавляем в Allure
    with allure.step(f"Проверено {len(results)} URL"):
        allure.attach(
            f"Успешных: {successful}\nНеудачных: {failed}",
            "Статистика",
            allure.attachment_type.TEXT
        )
    
    print(f"\n🎯 Итоговая статистика:")
    print(f"   ✅ Успешных: {successful}")
    print(f"   ❌ Неудачных: {failed}")
    print(f"   📈 Процент успеха: {(successful/len(results)*100):.1f}%")
    
    # Проверяем что все прошли успешно
    if failed > 0:
        failed_urls = [r['url'] for r in results if not r['success']]
        pytest.fail(f"Обнаружены проблемы с {failed} URL: {failed_urls}")
    
    print(f"\n🏆 Все {successful} URL работают корректно!")


@ui_test(
    title="Быстрая проверка доступности сервисов",
    description="Проверяет что все сервисы отвечают на запросы",
    feature="Infrastructure"
)
def test_basic_connectivity() -> None:
    """
    Быстрая проверка доступности всех сервисов.
    """
    all_urls = REDIRECT_CONFIG['no_redirect'] + REDIRECT_CONFIG['with_redirect']
    
    print(f"\n🌐 Проверка доступности {len(all_urls)} сервисов...")
    
    unavailable = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(requests.head, url, timeout=5): url for url in all_urls}
        
        for future in as_completed(futures):
            url = futures[future]
            try:
                response = future.result()
                if not (200 <= response.status_code < 500):
                    unavailable.append(f"{url} (статус: {response.status_code})")
                else:
                    print(f"   ✅ {url} доступен")
            except Exception as e:
                unavailable.append(f"{url} (ошибка: {str(e)})")
                print(f"   ❌ {url} недоступен: {e}")
    
    if unavailable:
        pytest.fail(f"Недоступные сервисы: {unavailable}")
    
    print(f"\n✅ Все {len(all_urls)} сервисов доступны!") 