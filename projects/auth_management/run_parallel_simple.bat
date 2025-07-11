@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   ПРОСТАЯ ПАРАЛЛЕЛЬНАЯ АВТОРИЗАЦИЯ
echo   Разделяем bulk_users.csv на 5 частей
echo   Запускаем 5 отдельных окон
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "data\bulk_users.csv" (
    echo ОШИБКА: Файл data\bulk_users.csv не найден!
    pause
    exit /b 1
)

echo ВНИМАНИЕ: Каждый поток будет обрабатывать ~137 пользователей
echo Будет открыто 5 отдельных окон терминала
echo.
set /p choice="Продолжить? (y/n): "
if /i not "%choice%"=="y" if /i not "%choice%"=="yes" (
    echo Операция отменена.
    pause
    exit /b 0
)

echo.
echo [%time%] Разделяем CSV файл на 5 частей...
python scripts\split_csv.py "data\bulk_users.csv"

if errorlevel 1 (
    echo Ошибка при разделении файла!
    pause
    exit /b 1
)

echo.
echo [%time%] Запускаем 5 параллельных потоков...
call run_all_threads.bat

echo.
echo [%time%] Все потоки запущены!
echo Следите за прогрессом в отдельных окнах.
pause
