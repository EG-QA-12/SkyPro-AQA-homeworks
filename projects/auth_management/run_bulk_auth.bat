@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   Массовая авторизация пользователей
echo   Файл: D:\Bll_tests\secrets\bulk_users.csv
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "D:\Bll_tests\secrets\bulk_users.csv" (
    echo ОШИБКА: Файл D:\Bll_tests\secrets\bulk_users.csv не найден!
    echo Убедитесь, что файл существует в директории D:\Bll_tests\secrets\
    pause
    exit /b 1
)

echo Запуск авторизации в ВИЗУАЛЬНОМ режиме...
echo Будут открываться окна браузера для каждого пользователя.
echo.
echo Для запуска в скрытом режиме используйте: run_bulk_auth_headless.bat
echo.
pause

python scripts\authorize_users_from_csv.py "D:\Bll_tests\secrets\bulk_users.csv"

echo.
echo ==========================================
echo   Авторизация завершена!
echo ==========================================
pause
