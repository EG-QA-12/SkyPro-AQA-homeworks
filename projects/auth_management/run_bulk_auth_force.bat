@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   ПРИНУДИТЕЛЬНАЯ переавторизация
echo   Файл: D:\Bll_tests\secrets\bulk_users.csv
echo   Режим: FORCE (игнорирует существующие куки)
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "D:\Bll_tests\secrets\bulk_users.csv" (
    echo ОШИБКА: Файл D:\Bll_tests\secrets\bulk_users.csv не найден!
    echo Убедитесь, что файл существует в директории D:\Bll_tests\secrets\
    pause
    exit /b 1
)

echo ВНИМАНИЕ: Этот режим ПРИНУДИТЕЛЬНО переавторизует ВСЕХ пользователей!
echo Это может занять значительное время (2-3 часа для всех пользователей)...
echo.
set /p choice="Продолжить? (y/n): "
if /i not "%choice%"=="y" if /i not "%choice%"=="yes" (
    echo Операция отменена.
    pause
    exit /b 0
)

echo.
echo [%time%] Запуск принудительной авторизации...

python scripts\authorize_users_from_csv.py "D:\Bll_tests\secrets\bulk_users.csv" --headless --force

echo.
echo [%time%] Принудительная авторизация завершена!
pause
