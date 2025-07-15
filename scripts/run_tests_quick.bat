@echo off
cd /d "%~dp0\.."
echo ⚡ Быстрый запуск тестов (10 потоков, краткий вывод)...
python -m pytest -n 10 -q
pause 