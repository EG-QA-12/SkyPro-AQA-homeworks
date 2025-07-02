# Руководство по запуску тестов для конкретных пользователей из cookies

## Обзор

Модуль `test_single_user_cookie_auth.py` позволяет запускать тесты авторизации для одного конкретного пользователя или группы пользователей, используя сохранённые cookies. Это значительно ускоряет тестирование и позволяет фокусироваться на тестировании функциональности под конкретными ролями.

## Доступные способы запуска

### 1. Просмотр доступных пользователей

```bash
# Показать всех пользователей с сохранёнными cookies
pytest tests/e2e/test_single_user_cookie_auth.py::test_list_available_users -v -s
```

### 2. Тест для одного пользователя через переменную окружения

```bash
# Запуск для конкретного пользователя
TARGET_USER=user1 pytest tests/e2e/test_single_user_cookie_auth.py::test_single_user_cookie_auth -v -s

# В headless режиме
HEADLESS=1 TARGET_USER=user2 pytest tests/e2e/test_single_user_cookie_auth.py::test_single_user_cookie_auth -v -s

# PowerShell синтаксис
$env:TARGET_USER = "user1"; pytest tests/e2e/test_single_user_cookie_auth.py::test_single_user_cookie_auth -v -s
```

### 3. Параметризованные тесты для выбранных пользователей

```bash
# Все параметризованные пользователи (admin, 1, 2, 3, EvgenQA, TABCDEFr)
pytest tests/e2e/test_single_user_cookie_auth.py::test_parametrized_user_auth -v -s

# Только конкретный пользователь
pytest "tests/e2e/test_single_user_cookie_auth.py::test_parametrized_user_auth[chromium-admin]" -v -s

# В headless режиме
HEADLESS=1 pytest "tests/e2e/test_single_user_cookie_auth.py::test_parametrized_user_auth[chromium-EvgenQA]" -v -s
```

## Доступные пользователи

По состоянию на последнюю проверку в системе доступны cookies для следующих пользователей:

**Числовые ID (большие файлы ~6974 bytes):**
- 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

**Именованные пользователи (маленькие файлы ~505 bytes):**
- user_admin
- user_qa
- user_test1
- user_test2
- [и другие тестовые аккаунты...]

## Особенности использования

### Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|---------|
| `TARGET_USER` | Имя пользователя для единичного теста | `admin`, `EvgenQA`, `1` |
| `HEADLESS` | Запуск в headless режиме | `1` (включить), `0` (отключить) |
| `NOTGUI` | Альтернативный способ включения headless | `1` (включить) |

### Выбор конкретного пользователя в параметризованном тесте

```bash
# Синтаксис: [browser-username]
pytest "tests/e2e/test_single_user_cookie_auth.py::test_parametrized_user_auth[chromium-admin]" -v

# Для разных пользователей
pytest "tests/e2e/test_single_user_cookie_auth.py::test_parametrized_user_auth[chromium-1]" -v
pytest "tests/e2e/test_single_user_cookie_auth.py::test_parametrized_user_auth[chromium-EvgenQA]" -v
```

## Процесс выполнения теста

1. **Проверка наличия cookies**: Тест проверяет существование файла с cookies для указанного пользователя
2. **Загрузка cookies**: Загружает `test_joint_session` cookie в браузерный контекст
3. **Переход на сайт**: Открывает https://ca.bll.by с загруженной cookie
4. **Проверка авторизации**: Ищет индикаторы авторизованного состояния
5. **Валидация**: Подтверждает сохранность cookie после загрузки страницы

## Индикаторы успешной авторизации

Тесты ищут следующие элементы для подтверждения авторизации:

- `div.profile_ttl:has-text('Мой профиль')`
- `text=Выйти`
- `text=Профиль`  
- `text=Личный кабинет`
- `.user-menu`
- `.profile-link`

## Статусы HTTP

- **200** - Сайт доступен, нормальная работа
- **403** - Ожидаемо для тестового окружения, cookie всё равно загружена
- Другие статусы - могут указывать на проблемы с сетью или сервером

## Примеры использования в CI/CD

```yaml
# GitHub Actions пример
- name: Test specific user authorization
  run: |
    TARGET_USER=admin pytest tests/e2e/test_single_user_cookie_auth.py::test_single_user_cookie_auth
    
- name: Test multiple users in headless mode
  run: |
    HEADLESS=1 pytest tests/e2e/test_single_user_cookie_auth.py::test_parametrized_user_auth
```

## Устранение неполадок

### Ошибка "Файл cookies не найден"
```
Файл cookies для пользователя 'username' не найден: path/to/cookies
```

**Решение**: Сначала запустите тест для сохранения cookies:
```bash
pytest tests/e2e/test_ui_login_and_session_save.py::test_visible_login_and_save_cookies
```

### Ошибка "Cookie не загружена"
```
Cookie test_joint_session не найдена в загруженных cookies
```

**Решение**: Файл cookie повреждён или имеет неправильный формат. Пересоздайте cookies.

### Тест пропускается из-за отсутствия TARGET_USER
```
SKIPPED: Не задана переменная TARGET_USER
```

**Решение**: Установите переменную окружения:
```bash
export TARGET_USER=admin  # Linux/Mac
$env:TARGET_USER = "admin"  # PowerShell
```

## Полезные команды

```bash
# Показать все доступные маркеры
pytest --markers

# Запустить только cookie-тесты
pytest -m cookie_auth

# Запустить только single_user тесты
pytest -m single_user

# Запустить с подробным выводом и остановкой на первой ошибке
pytest tests/e2e/test_single_user_cookie_auth.py -v -s -x

# Запустить в тихом режиме (только результаты)
TARGET_USER=admin pytest tests/e2e/test_single_user_cookie_auth.py::test_single_user_cookie_auth -q
```
