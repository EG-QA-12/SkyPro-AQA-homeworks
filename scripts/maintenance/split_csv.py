#!/usr/bin/env python3
"""
Простой скрипт для разделения CSV файла на части для параллельной обработки.
"""

import csv
import sys
from pathlib import Path

def split_csv(input_file: str, num_parts: int = 5):
    """Разделяет CSV файл на указанное количество частей."""
    
    # Читаем все строки
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    
    total_rows = len(rows)
    rows_per_part = max(1, total_rows // num_parts)
    
    print(f"Всего строк: {total_rows}")
    print(f"Строк в части: {rows_per_part}")
    print(f"Создаем {num_parts} частей...")
    
    # Создаем части
    for i in range(num_parts):
        start_idx = i * rows_per_part
        if i == num_parts - 1:  # Последняя часть получает все оставшиеся строки
            end_idx = total_rows
        else:
            end_idx = start_idx + rows_per_part
            
        part_rows = rows[start_idx:end_idx]
        
        if part_rows:  # Создаем файл только если есть строки
            output_file = f"D:/Bll_tests/secrets/bulk_users_part_{i+1}.csv"
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(part_rows)
            
            print(f"✅ Создан файл {output_file} ({len(part_rows)} строк)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python scripts/split_csv.py D:/Bll_tests/secrets/bulk_users.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not Path(input_file).exists():
        print(f"Файл не найден: {input_file}")
        sys.exit(1)
    
    split_csv(input_file)
