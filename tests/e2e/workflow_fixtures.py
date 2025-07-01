"""Временные фикстуры-заглушки для интеграционных workflow-тестов.

Эти фикстуры нужны только для того, чтобы **сборка тестов** проходила без
ошибок импорта.  Фактическая логика будет разработана позднее.

Пока каждая фикстура вызывает ``pytest.skip`` — это значит, что при запуске
тест автоматически помечается как *пропущенный*, что лучше, чем падение при
коллекции.

Junior note: ``pytest.skip`` внутри фикстуры пропускает **все** тесты, которые
зависят от неё.  Мы используем это, когда функциональность ещё не готова, но
нужно поддерживать зелёную сборку.
"""
import pytest

# ---- Вспомогательный объект-контейнер ---------------------------------------
class _WorkflowContext:
    """Простейший key-value store, заменяющий полноценный context manager."""

    def __init__(self) -> None:
        self._store: dict[str, object] = {}

    # For junior engineers: тип `object` означает, что мы можем хранить любое
    # значение без уточнения конкретного типа.

    def set(self, key: str, value: object) -> None:
        """Сохраняет значение по ключу."""
        self._store[key] = value

    def get(self, key: str, default: object | None = None) -> object | None:
        """Возвращает сохранённое значение или *default*.
        Эта функция не бросает исключение, если ключа нет, чтобы не ронять
        тесты на раннем этапе.
        """
        return self._store.get(key, default)


# ---- Фикстуры-заглушки -------------------------------------------------------
@pytest.fixture(scope="session")
def workflow_context() -> _WorkflowContext:  # type: ignore[name-defined]
    """Общий контекст для обмена данными между шагами workflow-теста."""
    pytest.skip("Workflow fixtures are under construction — skipping.")


@pytest.fixture
def user_page():
    pytest.skip("User page fixture is under construction — skipping.")


@pytest.fixture
def moderator_page():
    pytest.skip("Moderator page fixture is under construction — skipping.")


@pytest.fixture
def admin_page():
    pytest.skip("Admin page fixture is under construction — skipping.")


@pytest.fixture
def expert_page():
    pytest.skip("Expert page fixture is under construction — skipping.")
