@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   ПАРАЛЛЕЛЬНАЯ авторизация (5 потоков)
echo   Файл: D:\Bll_tests\secrets\bulk_users.csv
echo   Потоки: 5
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

echo ВНИМАНИЕ: Запуск в 5 потоков для ускорения процесса!
echo Это должно сократить время выполнения в ~5 раз...
echo.
set /p choice="Продолжить? (y/n): "
if /i not "%choice%"=="y" if /i not "%choice%"=="yes" (
    echo Операция отменена.
    pause
    exit /b 0
)

echo.
echo [%time%] Запуск параллельной авторизации в 5 потоков...

python scripts\parallel_auth.py "D:\Bll_tests\secrets\bulk_users.csv" --threads 5 --headless --relogin

echo.
echo [%time%] Параллельная авторизация завершена!
pause
