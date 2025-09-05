# Справочник API системы авторизации

## Общая информация

Этот документ содержит описание API компонентов системы авторизации.

## AuthCookieProvider

`AuthCookieProvider` - основной провайдер авторизационных кук. Он реализует стратегию получения куки `test_joint_session` из различных источников в порядке приоритета:

1. **Переменные окружения**: `SESSION_COOKIE_{ROLE}` или `SESSION_COOKIE`
2. **Локальные файлы**: `cookies/{role}_session.txt` или `cookies/{role}_cookies.json`
3. **API-логин**: автоматический логин через `APIAuthManager`

### Методы

#### get_auth_cookie
```python
def get_auth_cookie(role: str = "admin", use_api_login: bool = True) -> Optional[str]
```
Возвращает значение куки `test_joint_session` для указанной роли.

**Параметры:**
- `role` (str): Роль пользователя (например, "admin")
- `use_api_login` (bool): Флаг, разрешающий fallback на API-логин

**Возвращает:**
- `Optional[str]`: Строка со значением куки или `None`, если получить не удалось

#### _get_cookie_from_env
```python
def _get_cookie_from_env(role: str) -> Optional[str]
```
Пытается прочитать куку из переменных окружения.

**Параметры:**
- `role` (str): Роль пользователя

**Возвращает:**
- `Optional[str]`: Значение куки из переменных окружения или `None`

#### _get_cookie_from_files
```python
def _get_cookie_from_files(role: str) -> Optional[str]
```
Пытается прочитать куку из артефактов прошлых запусков.

**Параметры:**
- `role` (str): Роль пользователя

**Возвращает:**
- `Optional[str]`: Значение куки из файлов или `None`

#### _get_cookie_via_api_login
```python
def _get_cookie_via_api_login(role: str) -> Optional[str]
```
Выполняет API-логин для указанной роли.

**Параметры:**
- `role` (str): Роль пользователя

**Возвращает:**
- `Optional[str]`: Значение куки, полученное через API-логин, или `None`

## APIAuthManager

`APIAuthManager` обеспечивает быструю и надежную авторизацию через HTTP запросы, минуя проблемы браузерной автоматизации и антибот защиты. Он поддерживает параллельную обработку для максимальной производительности.

### Методы

#### login_user
```python
def login_user(
    username: str, 
    password: str, 
    user_index: int = 0, 
    total_users: int = 1
) -> AuthResult
```
Авторизация одного пользователя через API.

**Параметры:**
- `username` (str): Логин пользователя
- `password` (str): Пароль пользователя
- `user_index` (int): Индекс пользователя для отображения прогресса
- `total_users` (int): Общее количество пользователей

**Возвращает:**
- `AuthResult`: Результат авторизации с куками и статусом

#### mass_authorize_users
```python
def mass_authorize_users(
    users: List[Dict[str, str]], 
    save_to_files: bool = True, 
    update_database: bool = True, 
    max_workers: int = 5
) -> Tuple[List[AuthResult], Dict[str, Any]]
```
Массовая авторизация списка пользователей через API с параллельной обработкой.

**Параметры:**
- `users` (List[Dict[str, str]]): Список пользователей с ключами 'login', 'password', 'name'
- `save_to_files` (bool): Сохранять ли куки в файлы
- `update_database` (bool): Обновлять ли информацию в базе данных
- `max_workers` (int): Максимальное количество потоков (по умолчанию 5)

**Возвращает:**
- `Tuple[List[AuthResult], Dict[str, Any]]`: Результаты авторизации и статистика

## SmartAuthManager

`SmartAuthManager` управляет авторизацией, проверяя валидность кук и обновляя их только при необходимости. Он обеспечивает интеллектуальное кэширование и автоматическое обновление сессий.

### Методы

#### get_valid_session_cookie
```python
def get_valid_session_cookie(
    role: str, 
    force_refresh: bool = False
) -> Optional[str]
```
Получает валидную сессионную куку, при необходимости выполняя API-логин.

**Параметры:**
- `role` (str): Роль пользователя
- `force_refresh` (bool): Принудительное обновление куки

**Возвращает:**
- `Optional[str]`: Валидная сессионная кука или `None`

#### _perform_api_login
```python
def _perform_api_login(role: str) -> Optional[str]
```
Выполняет API-логин и полностью обновляет сессию менеджера.

**Параметры:**
- `role` (str): Роль пользователя

**Возвращает:**
- `Optional[str]`: Значение куки, полученное через API-логин, или `None`