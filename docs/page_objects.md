# Руководство по Page Object

Page Object — это паттерн, представляющий каждую страницу веб-приложения отдельным классом. Это избавляет тесты от прямой работы с локаторами: они вызывают методы Page Object, а детали реализации скрыты.

## Где находятся Page Objects

Все классы располагаются в `framework/app/pages/`.

| Класс | Файл | Назначение |
|-------|------|------------|
| `LoginPage` | `login_page.py` | Авторизация пользователя через форму входа |
| `ProfilePage` | `profile_page.py` | Работа с личным кабинетом |
| `ModeratorDashboardPage` | `moderator_dashboard_page.py` | Доступ к панели модератора |

## Базовые принципы

1. **Один класс — одна страница**. Исключение: большие страницы можно разбить на компоненты.
2. **Публичные методы = действия пользователя**. Пример: `fill_credentials()`, `click_submit()`.
3. **Валидация внутри Page Object**. Методы возвращают `bool` или бросают исключение, если ожидание не выполнено.
4. **Повторное использование локаторов**. Локаторы объявлены как свойства класса, чтобы менять их централизованно.
5. **Документирование**. Каждый метод снабжён docstring’ом с примером использования.

## Шаблон Page Object

```python
from playwright.sync_api import Page

class BasePage:
    """Базовый класс для всех страниц: содержит общие вспомогательные методы."""

    def __init__(self, page: Page) -> None:
        self.page = page

class LoginPage(BasePage):
    """Страница входа в систему."""

    _username = "input[name='username']"
    _password = "input[name='password']"
    _submit = "button[type='submit']"

    def fill_credentials(self, username: str, password: str) -> None:
        """Заполняет форму входа."""
        self.page.fill(self._username, username)
        self.page.fill(self._password, password)

    def click_submit(self) -> None:
        """Нажимает кнопку «Войти»."""
        self.page.click(self._submit)

    def is_success_message_visible(self) -> bool:
        """Проверяет, что авторизация прошла успешно."""
        return self.page.is_visible("text=Вы успешно вошли")
```

## Как добавлять новую страницу

1. Создайте файл `my_page.py` в `framework/app/pages/`.
2. Наследуйтесь от `BasePage` или другого общедоступного базового класса.
3. Определите локаторы и публичные методы.
4. Добавьте подробный docstring с примерами.
5. Импортируйте класс в `framework/app/pages/__init__.py` (или используйте механизм auto-import).

## Рекомендации

- Старайтесь избегать `time.sleep()`; вместо этого используйте методы ожидания Playwright.
- Не смешивайте логику нескольких ролей в одном Page Object.
- Если элемент часто используется в тестах, предоставьте в Page Object dedicated метод доступа. 