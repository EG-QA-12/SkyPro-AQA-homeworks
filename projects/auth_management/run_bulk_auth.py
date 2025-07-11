#!/usr/bin/env python3
"""
Удобный скрипт для запуска массовой авторизации из стандартного CSV файла.

Использование:
    python run_bulk_auth.py                    # Обычный режим
    python run_bulk_auth.py --headless         # Скрытый режим
    python run_bulk_auth.py --force            # Принудительная переавторизация
    python run_bulk_auth.py --headless --force # Скрытый + принудительный режим
"""

import argparse
import os
import sys
from pathlib import Path

# Добавляем путь к корню проекта
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.user_manager import UserManager
from src.config import config
from src.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(
        description="Удобный запуск массовой авторизации из D:/Bll_tests/secrets/bulk_users.csv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python run_bulk_auth.py                    # Визуальный режим
  python run_bulk_auth.py --headless         # Скрытый режим
  python run_bulk_auth.py --force            # Принудительная переавторизация
  python run_bulk_auth.py --headless --force # Скрытый + принудительный
        """
    )
    
    parser.add_argument(
        "--headless", 
        action="store_true",
        help="Запуск браузера в скрытом режиме (без отображения окон)"
    )
    
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Принудительная переавторизация (игнорировать существующие куки)"
    )
    
    parser.add_argument(
        "--csv-path",
        default=None,
        help="Путь к CSV файлу (по умолчанию: D:/Bll_tests/secrets/bulk_users.csv)"
    )
    
    args = parser.parse_args()
    
    # Определяем путь к CSV файлу
    if args.csv_path:
        csv_path = Path(args.csv_path)
    else:
        csv_path = config.BULK_CSV_PATH
    
    # Проверяем существование файла
    if not csv_path.exists():
        logger.error(f"CSV файл не найден: {csv_path}")
        logger.error("Убедитесь, что файл существует или укажите правильный путь с --csv-path")
        sys.exit(1)
    
    # Выводим информацию о режиме запуска
    mode_info = []
    if args.headless:
        mode_info.append("СКРЫТЫЙ режим")
    else:
        mode_info.append("ВИЗУАЛЬНЫЙ режим")
        
    if args.force:
        mode_info.append("ПРИНУДИТЕЛЬНАЯ переавторизация")
    else:
        mode_info.append("пропуск пользователей с действующими куками")
    
    print("=" * 60)
    print("  МАССОВАЯ АВТОРИЗАЦИЯ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 60)
    print(f"Файл CSV: {csv_path}")
    print(f"Режим: {', '.join(mode_info)}")
    print("=" * 60)
    
    # Подтверждение запуска для принудительного режима
    if args.force:
        print("\n⚠️  ВНИМАНИЕ: Принудительный режим переавторизует ВСЕХ пользователей!")
        print("   Это может занять значительное время...")
        
        response = input("\nПродолжить? (y/N): ").strip().lower()
        if response not in ['y', 'yes', 'да']:
            print("Операция отменена.")
            sys.exit(0)
    
    print(f"\n🚀 Запуск авторизации...")
    print(f"   Браузер: {'скрытый' if args.headless else 'видимый'}")
    print(f"   Переавторизация: {'принудительная' if args.force else 'умная'}")
    print()
    
    try:
        # Создаем менеджер пользователей и запускаем авторизацию
        user_manager = UserManager()
        result = user_manager.authorize_users_from_csv(
            str(csv_path), 
            headless=args.headless, 
            force_reauth=args.force
        )
        
        # Выводим результаты
        success_count = len(result.get('success', {}))
        failed_count = len(result.get('failed', []))
        
        print("\n" + "=" * 60)
        print("  РЕЗУЛЬТАТЫ АВТОРИЗАЦИИ")
        print("=" * 60)
        print(f"✅ Успешно авторизовано: {success_count}")
        print(f"❌ Ошибок: {failed_count}")
        
        if failed_count > 0:
            print("\n❌ Пользователи с ошибками:")
            for failed_user in result.get('failed', []):
                print(f"   - {failed_user}")
        
        print("=" * 60)
        
        if failed_count > 0:
            logger.warning(f"Авторизация завершена с ошибками: {failed_count}")
            sys.exit(1)
        else:
            logger.info("Авторизация завершена успешно!")
            
    except Exception as e:
        logger.error(f"Критическая ошибка во время авторизации: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
