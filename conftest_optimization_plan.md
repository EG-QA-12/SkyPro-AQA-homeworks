# ПЛАН ОПТИМИЗАЦИИ CONFTEST.PY ФАЙЛОВ

## 1. Консолидация sys.path логики
Все манипуляции с sys.path должны быть в корневом conftest.py:
   • conftest.py: 4 манипуляций
   • tests\e2e\conftest.py: 2 манипуляций

## 2. Дублирующиеся функции
   • pytest_addoption:
     - projects\auth_management\tests\conftest.py
     - projects\conftest.py
   • http_session:
     - tests\e2e\redirect_tests\conftest.py
     - tests\integration\conftest.py
     - tests\integration\infrastructure\conftest.py

## 3. Дублирующиеся фикстуры
   • http_session:
     - tests\e2e\redirect_tests\conftest.py
     - tests\integration\conftest.py
     - tests\integration\infrastructure\conftest.py

## 4. Рекомендации по оптимизации
### Действия по консолидации:
1. Перенести всю sys.path логику в корневой conftest.py
2. Оставить специфичные фикстуры в локальных conftest.py
3. Удалить избыточные файлы
4. Обновить импорты в тестах