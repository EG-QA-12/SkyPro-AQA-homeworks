@echo off
chcp 65001 > nul
echo.
echo ================================
echo   Многопоточная авторизация
   (Каждый файл - отдельный поток)
echo ================================
echo.

if not exist data\bulk_users_part_1.csv (
    echo Ошибка: данные не были разделены.
    exit /b 1
)

echo Запускаем поток 1...
start "Поток 1" cmd /c python scripts\authorize_users_from_csv.py data\bulk_users_part_1.csv --headless --relogin ^& pause

echo Запускаем поток 2...
start "Поток 2" cmd /c python scripts\authorize_users_from_csv.py data\bulk_users_part_2.csv --headless --relogin ^& pause

echo Запускаем поток 3...
start "Поток 3" cmd /c python scripts\authorize_users_from_csv.py data\bulk_users_part_3.csv --headless --relogin ^& pause

echo Запускаем поток 4...
start "Поток 4" cmd /c python scripts\authorize_users_from_csv.py data\bulk_users_part_4.csv --headless --relogin ^& pause

echo Запускаем поток 5...
start "Поток 5" cmd /c python scripts\authorize_users_from_csv.py data\bulk_users_part_5.csv --headless --relogin ^& pause

echo Все потоки запущены! Каждый поток в отдельном окне.

pause
