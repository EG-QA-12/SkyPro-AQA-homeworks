@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   УДАЛЕНИЕ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "data\users.db" (
    echo ОШИБКА: База данных не найдена: data\users.db
    echo Возможно, база уже очищена или еще не создана.
    pause
    exit /b 1
)

echo ⚠️  Эта операция удалит ВСЕХ пользователей из базы данных!
echo    (Кроме системных: admin, moderator, expert)
echo.
set /p choice="Продолжить? (y/N): "
if /i not "%choice%"=="y" if /i not "%choice%"=="yes" (
    echo Операция отменена.
    pause
    exit /b 0
)

echo.
echo 🗑️  Удаление пользователей...

python -c "
import sys, os
sys.path.insert(0, '.')
from src.user_manager import UserManager

try:
    user_manager = UserManager()
    all_users = user_manager.get_all_users()
    
    # Системные пользователи, которых НЕ удаляем
    system_users = {'admin', 'moderator', 'expert', 'EvgenQA', 'Xf2gijK8'}
    
    deleted_count = 0
    skipped_count = 0
    
    for user in all_users:
        username = user.get('username') or user.get('login')
        if username and username not in system_users:
            try:
                user_manager.delete_user(username)
                print(f'🗑️  Удален: {username}')
                deleted_count += 1
            except Exception as e:
                print(f'❌ Ошибка удаления {username}: {e}')
        else:
            skipped_count += 1
    
    print(f'\\n✅ Операция завершена:')
    print(f'   Удалено пользователей: {deleted_count}')
    print(f'   Пропущено системных: {skipped_count}')
    
except Exception as e:
    print(f'❌ Критическая ошибка: {e}')
    exit(1)
"

if %ERRORLEVEL% equ 0 (
    echo.
    echo 🗑️  Очистка файлов куков...
    if exist "data\*_cookies.json" (
        for %%f in ("data\*_cookies.json") do (
            echo 🗑️  Удаляем: %%f
            del "%%f"
        )
        echo ✅ Файлы куков очищены
    ) else (
        echo ℹ️  Файлы куков не найдены
    )
    
    echo.
    echo ==========================================
    echo   ПОЛЬЗОВАТЕЛИ УДАЛЕНЫ!
    echo ==========================================
    echo   Системные пользователи сохранены.
    echo   Для добавления новых пользователей:
    echo   python scripts\init_users.py
    echo ==========================================
) else (
    echo.
    echo ❌ Операция завершена с ошибками!
)

pause
