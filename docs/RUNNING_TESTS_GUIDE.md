# Руководство по запуску тестов

## Введение

Это руководство описывает различные способы запуска тестов в проекте,
включая локальный запуск, запуск с Allure отчетами и различные конфигурации.

## Быстрый старт

### Запуск всех тестов
```bash
# Запуск всех тестов
pytest

# Запуск с подробным выводом
pytest -v

# Запуск с выводом print() и логов
pytest -s
```

### Запуск smoke тестов
```bash
# Запуск только smoke тестов
pytest -m smoke
```

### Запуск API тестов
```bash
# Запуск всех API тестов
pytest -m api

# Запуск API тестов с отчетами
pytest -m api --alluredir=allure-results
```

## Конфигурация запуска

### Переменные окружения
```bash
# Количество вопросов для параметризированных тестов
export NUM_QUESTIONS=5

# Таймауты для панели модерации
export PANEL_DELAYS="0,1,2,4"
export PANEL_LIMIT=100
export PANEL_FRESH_MINUTES=3

# Роль пользователя для тестов
export TEST_ROLE=admin

# Режим отладки
export DEBUG_MODE=true
```

### Конфигурационные файлы
- `pytest.ini` - основная конфигурация pytest
- `config/.env` - переменные окружения
- `config/.env.test` - тестовые переменные окружения

## Запуск с Allure отчетами

### Установка Allure
```bash
# Windows (через Chocolatey)
choco install allure

# macOS (через Homebrew)  
brew install allure

# Linux (через snap)
sudo snap install allure
```

### Запуск с генерацией отчетов
```bash
# Запуск тестов с генерацией результатов
pytest --alluredir=allure-results

# Генерация и открытие отчета
allure generate allure-results --clean
allure open

# Или одной командой
allure serve allure-results
```

### Автоматизированный запуск
```bash
# Использование скрипта
./scripts/run_tests_allure.bat

# Или вручную
pytest --alluredir=allure-results -v
allure serve allure-results
```

## Маркеры тестов

### Стандартные маркеры
```bash
# Smoke тесты
pytest -m smoke

# Регрессионные тесты
pytest -m regression

# API тесты
pytest -m api

# UI тесты
pytest -m ui

# Тесты вопросов
pytest -m question

# Тесты модерации
pytest -m moderation

# Тесты безопасности
pytest -m security
```

### Комбинации маркеров
```bash
# API тесты вопросов
pytest -m "api and question"

# Smoke тесты API
pytest -m "api and smoke"

# Все кроме UI тестов
pytest -m "not ui"
```

## Параметризованные тесты

### Управление количеством итераций
```bash
# Отправка 10 вопросов вместо 1
NUM_QUESTIONS=10 pytest tests/integration/test_question_submission_optimized.py

# Отправка 100 вопросов
NUM_QUESTIONS=100 pytest tests/integration/test_question_submission_optimized.py -v
```

### Настройка таймаутов
```bash
# Быстрая проверка (меньше ожидание)
PANEL_DELAYS="0,0.5,1" pytest -m smoke

# Тщательная проверка (больше ожидание)
PANEL_DELAYS="0,2,5,10" pytest -m regression
```

## Параллельный запуск

### Запуск тестов параллельно
```bash
# Установка плагина xdist
pip install pytest-xdist

# Запуск с 4 воркерами
pytest -n 4

# Запуск с автоматическим определением количества ядер
pytest -n auto

# Запуск smoke тестов параллельно
pytest -n auto -m smoke
```

### Ограничения параллельного запуска
- Тесты должны быть изолированы
- Не использовать общие ресурсы без синхронизации
- Учитывать ограничения API по количеству запросов

## Отладка тестов

### Режим отладки
```bash
# Запуск с отладочным выводом
DEBUG_MODE=true pytest -s -v

# Запуск конкретного теста с отладкой
pytest tests/integration/test_new_framework_example.py::TestQuestionManagement::test_create_question_via_api -s -v
```

### Логирование
```bash
# Уровень логирования
pytest --log-cli-level=INFO

# Логирование в файл
pytest --log-file=tests.log --log-file-level=DEBUG
```

## Профилирование

### Измерение времени выполнения
```bash
# Установка плагина
pip install pytest-benchmark

# Запуск с измерением производительности
pytest --benchmark-only

# Сохранение результатов
pytest --benchmark-save=results
```

### Анализ покрытия кода
```bash
# Установка coverage
pip install coverage

# Запуск с измерением покрытия
coverage run -m pytest

# Генерация отчета
coverage report
coverage html  # HTML отчет
```

## CI/CD интеграция

### GitHub Actions
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest -m smoke --alluredir=allure-results
    - name: Upload results
      uses: actions/upload-artifact@v2
      if: always()
      with:
        name: allure-results
        path: allure-results
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'pytest -m api --alluredir=allure-results'
            }
            post {
                always {
                    publishHtml([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'allure-results',
                        reportFiles: 'index.html',
                        reportName: 'Allure Report'
                    ])
                }
            }
        }
    }
}
```

## Скрипты запуска

### Готовые скрипты
```bash
# Быстрый запуск smoke тестов
./scripts/run_tests_quick.bat

# Запуск с Allure отчетами
./scripts/run_tests_allure.bat

# Параллельный запуск
./scripts/run_tests_parallel.bat

# Запуск SSO тестов
./scripts/run_sso_tests_fast.bat
```

### Создание собственных скриптов
```bash
#!/bin/bash
# custom_run.sh
echo "Запуск тестов с кастомной конфигурацией"
export NUM_QUESTIONS=25
export PANEL_DELAYS="0,1,3,6"
pytest -m "api and question" --alluredir=allure-results -v
allure serve allure-results
```

## Решение проблем

### Частые ошибки

#### 1. "Module not found"
```bash
# Решение: Убедитесь что находитесь в корне проекта
cd /path/to/project
pytest

# Или добавьте путь в PYTHONPATH
export PYTHONPATH=/path/to/project:$PYTHONPATH
```

#### 2. "No tests collected"
```bash
# Решение: Проверьте маркеры и пути
pytest --collect-only  # Посмотреть какие тесты найдены
pytest -m "not skip"   # Исключить пропущенные тесты
```

#### 3. "Allure not found"
```bash
# Решение: Установите Allure
# Windows: choco install allure
# macOS: brew install allure
# Linux: sudo snap install allure
```

#### 4. "Connection refused"
```bash
# Решение: Проверьте доступность сервисов
curl -v https://bll.by  # Проверка доступности сайта
```

### Отладка авторизации
```bash
# Проверка наличия файлов кук
ls cookies/

# Проверка валидности кук
python -c "from framework.utils.auth_cookie_provider import check_cookie_validity; print(check_cookie_validity('admin'))"

# Обновление кук
python scripts/maintenance/cookie_tester.py --update-all
```

## Мониторинг и метрики

### Сбор метрик производительности
```bash
# Запуск с метриками
pytest --benchmark-only --benchmark-sort=mean

# Сравнение с предыдущими запусками
pytest --benchmark-compare --benchmark-sort=mean
```

### Мониторинг стабильности
```bash
# Запуск с повторами для нестабильных тестов
pytest --reruns 3 --reruns-delay 1

# Отчет о flaky тестах
pytest --json-report --json-report-file=report.json
```

## Рекомендации

### 1. Регулярный запуск
- Ежедневный запуск smoke тестов
- Еженедельный запуск регрессионных тестов
- Ежемесячный полный запуск всех тестов

### 2. Мониторинг результатов
- Анализ отчетов Allure
- Отслеживание flaky тестов
- Мониторинг времени выполнения

### 3. Оптимизация
- Параллельный запуск где возможно
- Кэширование результатов
- Оптимизация таймаутов

## Поддержка

При возникновении проблем с запуском тестов:
1. Проверьте логи и сообщения об ошибках
2. Убедитесь что все зависимости установлены
3. Проверьте конфигурационные файлы
4. Обратитесь к команде QA
