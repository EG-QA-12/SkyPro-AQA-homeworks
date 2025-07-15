@echo off
cd /d "%~dp0\.."
echo ========================================
echo 📊 ЗАПУСК ТЕСТОВ С ALLURE ОТЧЕТАМИ
echo ========================================
echo 🧹 Очистка старых результатов...
if exist allure-results rmdir /s /q allure-results
echo 🚀 Запуск тестов (10 потоков)...
python -m pytest -n 10 -v --alluredir=allure-results
echo 📈 Генерация Allure отчета...
allure serve allure-results 