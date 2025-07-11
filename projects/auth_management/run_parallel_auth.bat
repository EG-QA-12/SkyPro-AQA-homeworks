@echo off
echo ========================================
echo     Параллельная авторизация пользователей
echo ========================================

REM Проверяем наличие CSV файла
if not exist "D:\Bll_tests\secrets\bulk_users.csv" (
    echo ❌ Файл D:\Bll_tests\secrets\bulk_users.csv не найден!
    echo Создайте CSV файл с пользователями в формате:
    echo login,password,role,email,phone
    pause
    exit /b 1
)

echo 🚀 Запуск параллельной авторизации...
echo 📁 CSV файл: D:\Bll_tests\secrets\bulk_users.csv
echo 🧵 Количество потоков: 10
echo 🖥️ Режим: headless
echo 🔄 Принудительная переавторизация: да
echo.

python scripts\parallel_auth.py "D:\Bll_tests\secrets\bulk_users.csv" --threads 10 --headless --relogin

echo.
echo Готово! Нажмите любую клавишу для выхода...
pause > nul
