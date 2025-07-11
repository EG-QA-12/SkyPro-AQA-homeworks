@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo   ВИЗУАЛЬНАЯ массовая авторизация
echo   Файл: D:\Bll_tests\secrets\bulk_users.csv
echo   Режим: GUI (браузер будет виден)
echo ==========================================
echo.

cd /d "%~dp0"

if not exist "D:\Bll_tests\secrets\bulk_users.csv" (
    echo ОШИБКА: Файл D:\Bll_tests\secrets\bulk_users.csv не найден!
    echo Убедитесь, что файл существует в директории D:\Bll_tests\secrets\
    pause
    exit /b 1
)

echo ВНИМАНИЕ: В этом режиме браузер будет ВИДЕН на экране!
echo Вы сможете наблюдать процесс авторизации каждого пользователя.
echo Не закрывайте окна браузера вручную - это может нарушить процесс.
echo.
echo Для большого количества пользователей это займет много времени
echo и может быть ресурсозатратно для системы.
echo.
set /p choice="Продолжить с видимым браузером? (y/n): "
if /i not "%choice%"=="y" if /i not "%choice%"=="yes" (
    echo Операция отменена.
    pause
    exit /b 0
)

echo.
echo [%time%] Запуск авторизации с видимым браузером...
echo ВНИМАНИЕ: НЕ закрывайте окна браузера вручную!
echo.

python scripts\authorize_users_from_csv.py "D:\Bll_tests\secrets\bulk_users.csv" --visual

echo.
echo [%time%] Визуальная авторизация завершена!
pause
