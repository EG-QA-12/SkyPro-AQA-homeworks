@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   ТЕСТ: Визуальная авторизация
echo   Файл: data\visual_test.csv (3 пользователя)
echo   Режим: GUI (браузер будет виден)
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "data\visual_test.csv" (
    echo ОШИБКА: Файл data\visual_test.csv не найден!
    pause
    exit /b 1
)

echo ТЕСТ: Авторизация 3 пользователей с видимым браузером
echo Вы увидите как открывается браузер и происходит автоматический ввод данных.
echo НЕ закрывайте окна браузера вручную!
echo.
set /p choice="Запустить тест? (y/n): "
if /i not "%choice%"=="y" if /i not "%choice%"=="yes" (
    echo Тест отменен.
    pause
    exit /b 0
)

echo.
echo [%time%] Запуск ТЕСТА с видимым браузером...
echo.

python scripts\authorize_users_from_csv.py "data\visual_test.csv" --relogin

echo.
echo [%time%] Тест завершен!
pause
