#!/usr/bin/env python3
"""
Скрипт для сравнения ссылок бургер меню из разных источников
"""

import csv
from pathlib import Path
from typing import List, Tuple, Set

def load_csv_links(csv_path: str) -> List[Tuple[str, str]]:
    """Загружает ссылки из CSV файла"""
    links = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        # Определяем формат CSV по наличию заголовков
        first_line = f.readline().strip()
        f.seek(0)
        
        if ',' in first_line and not first_line.startswith('link_text') and not first_line.startswith('Текст ссылки'):
            # Формат без заголовков
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    links.append((row[0].strip(), row[1].strip()))
        else:
            # Формат с заголовками
            reader = csv.DictReader(f)
            for row in reader:
                if 'link_text' in row and 'href' in row:
                    links.append((row['link_text'].strip(), row['href'].strip()))
                elif 'Текст ссылки' in row and 'URL' in row:
                    links.append((row['Текст ссылки'].strip(), row['URL'].strip()))
    
    return links

def normalize_url(url: str) -> str:
    """Нормализует URL для сравнения"""
    # Убираем trailing slash если он есть
    if url.endswith('/'):
        url = url[:-1]
    return url.lower()

def compare_links(existing_links: List[Tuple[str, str]], new_links: List[Tuple[str, str]]) -> dict:
    """Сравнивает два списка ссылок"""
    
    # Создаем множества для сравнения
    existing_dict = {normalize_url(href): (text, href) for text, href in existing_links}
    new_dict = {normalize_url(href): (text, href) for text, href in new_links}
    
    # Находим различия
    only_in_existing = set(existing_dict.keys()) - set(new_dict.keys())
    only_in_new = set(new_dict.keys()) - set(existing_dict.keys())
    in_both = set(existing_dict.keys()) & set(new_dict.keys())
    
    # Проверяем различия в текстах для совпадающих URL
    text_differences = []
    for url in in_both:
        existing_text = existing_dict[url][0]
        new_text = new_dict[url][0]
        if existing_text != new_text:
            text_differences.append((url, existing_text, new_text))
    
    return {
        'only_in_existing': [(existing_dict[url][0], existing_dict[url][1]) for url in only_in_existing],
        'only_in_new': [(new_dict[url][0], new_dict[url][1]) for url in only_in_new],
        'text_differences': text_differences,
        'total_existing': len(existing_links),
        'total_new': len(new_links),
        'in_both': in_both
    }

def main():
    # Пути к файлам
    existing_csv = Path("tests/data/burger_menu_links.csv")
    new_csv = Path("scripts/data/burger_menu_links_admin.csv")
    
    print("=== Сравнение ссылок бургер меню ===\n")
    
    # Проверяем существование файлов
    if not existing_csv.exists():
        print(f"❌ Файл не найден: {existing_csv}")
        return
    
    if not new_csv.exists():
        print(f"❌ Файл не найден: {new_csv}")
        return
    
    # Загружаем ссылки
    existing_links = load_csv_links(str(existing_csv))
    new_links = load_csv_links(str(new_csv))
    
    print(f"📊 Статистика:")
    print(f"   Существующий файл ({existing_csv}): {len(existing_links)} ссылок")
    print(f"   Новый файл ({new_csv}): {len(new_links)} ссылок")
    print()
    
    # Сравниваем
    comparison = compare_links(existing_links, new_links)
    
    # Выводим результаты
    print(f"🔍 Результаты сравнения:")
    print(f"   Совпадающих ссылок: {len(comparison['in_both'])}")
    
    if comparison['only_in_new']:
        print(f"\n🆕 Новые ссылки ({len(comparison['only_in_new'])}):")
        for text, href in comparison['only_in_new']:
            print(f"   + {text} -> {href}")
    
    if comparison['only_in_existing']:
        print(f"\n🗑️  Отсутствующие ссылки ({len(comparison['only_in_existing'])}):")
        for text, href in comparison['only_in_existing']:
            print(f"   - {text} -> {href}")
    
    if comparison['text_differences']:
        print(f"\n📝 Изменения в текстах ({len(comparison['text_differences'])}):")
        for url, old_text, new_text in comparison['text_differences']:
            print(f"   ~ {old_text} -> {new_text} ({url})")
    
    # Рекомендации
    print(f"\n💡 Рекомендации:")
    if comparison['only_in_new']:
        print(f"   Рассмотрите добавление {len(comparison['only_in_new'])} новых ссылок в основной тест")
    if comparison['only_in_existing']:
        print(f"   Проверьте {len(comparison['only_in_existing'])} отсутствующих ссылок - возможно они устарели")
    if comparison['text_differences']:
        print(f"   Проверьте {len(comparison['text_differences'])} изменений в текстах ссылок")

if __name__ == "__main__":
    main()
