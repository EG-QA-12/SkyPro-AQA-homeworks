@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   Массовая авторизация пользователей
echo   Файл: D:\Bll_tests\secrets\bulk_users.csv
echo   Режим: СКРЫТЫЙ (headless)
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "D:\Bll_tests\secrets\bulk_users.csv" (
    echo ОШИБКА: Файл D:\Bll_tests\secrets\bulk_users.csv не найден!
    echo Убедитесь, что файл существует в директории D:\Bll_tests\secrets\
    pause
    exit /b 1
)

echo Запуск авторизации в СКРЫТОМ режиме...
echo Окна браузера НЕ будут показываться.
echo Процесс может занять несколько минут...
echo.

python scripts\authorize_users_from_csv.py "D:\Bll_tests\secrets\bulk_users.csv" --headless

echo.
echo ==========================================
echo   Авторизация завершена!
echo ==========================================
pause
