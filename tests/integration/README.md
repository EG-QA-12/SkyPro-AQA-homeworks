# Интеграционные тесты

Данная директория содержит основную тестовую базу для интеграционного тестирования компонентов BLL.

## Структура
- `redirect_tests/` — тесты проверки редиректов (были перенесены из e2e)
- `sso/` — тесты SSO-авторизации (были перенесены из e2e)
- `infrastructure/` — инфраструктурные и вспомогательные интеграционные тесты

## Запуск всех интеграционных тестов
```bash
pytest tests/integration/ -v
```

Для запуска отдельных групп тестов используйте соответствующие подпапки. 

## Отправка вопросов (`test_question_submission_optimized.py`)

Этот тест предназначен для имитации отправки вопросов через API. Он поддерживает параметризацию для отправки нескольких вопросов.

### Параметры запуска
Количество отправляемых вопросов контролируется переменной окружения `NUM_QUESTIONS`.

*   **Отправить 1 вопрос (по умолчанию):**
    ```bash
    python -m pytest tests/integration/test_question_submission_optimized.py -v -s
    ```

*   **Отправить N вопросов (например, 5):**
    ```bash
    NUM_QUESTIONS=5 python -m pytest tests/integration/test_question_submission_optimized.py -v -s
    ```

### Отчетность
Каждый отправленный вопрос будет отображаться как отдельный тестовый кейс в отчете Allure, 
обеспечивая высокую детализацию.

---

## Публикация вопросов (`test_publish_question_api.py`)

Этот тест предназначен для имитации публикации вопросов через административный API. Он поддерживает массовую публикацию и выбор конкретных вопросов.

### Параметры запуска
Количество публикуемых вопросов контролируется переменной окружения `NUM_QUESTIONS_TO_PUBLISH`.

*   **Опубликовать 1 вопрос (по умолчанию):**
    ```bash
    python -m pytest tests/integration/test_publish_question_api.py -v -s
    ```

*   **Опубликовать 5 вопросов:**
    ```bash
    NUM_QUESTIONS_TO_PUBLISH=5 python -m pytest tests/integration/test_publish_question_api.py -v -s
    ```

*   **Опубликовать 10 вопросов:**
    ```bash
    NUM_QUESTIONS_TO_PUBLISH=10 python -m pytest tests/integration/test_publish_question_api.py -v -s
    ```

### Выбор конкретных вопросов
Помимо массовой публикации, вы можете управлять выбором конкретного вопроса с помощью следующих 
переменных окружения (они переопределяют поведение по умолчанию):

*   `PUBLISH_MODE`: Определяет критерий выбора вопроса.
    *   `latest` (по умолчанию): Самый свежий неопубликованный вопрос.
    *   `by_marker`: Поиск вопроса по текстовому маркеру (см. `PUBLISH_MARKER`).
    *   `by_user`: Поиск вопроса по имени пользователя (см. `PUBLISH_USER`).
*   `PUBLISH_MARKER`: Фрагмент текста для поиска в вопросе (используется с `PUBLISH_MODE=by_marker`).
*   `PUBLISH_USER`: Имя пользователя, задавшего вопрос (используется с `PUBLISH_MODE=by_user`).

**Примеры запуска с выбором:**

*   **Опубликовать вопрос с конкретным маркером:**
    ```bash
    PUBLISH_MODE=by_marker PUBLISH_MARKER="MARKER_12345" python -m pytest tests/integration/test_publish_question_api.py -v -s
    ```

*   **Опубликовать вопрос от конкретного пользователя:**
    ```bash
    PUBLISH_MODE=by_user PUBLISH_USER="admin" python -m pytest tests/integration/test_publish_question_api.py -v -s
    ```

### Отчетность
<<<<<<< HEAD
Каждая операция публикации вопроса будет отображаться как отдельный тестовый кейс в отчете Allure, 
что обеспечивает высокую детализацию. 

---
=======
Каждая операция публикации вопроса будет отображаться как отдельный тестовый кейс в отчете Allure,
что обеспечивает высокую детализацию.
>>>>>>> docs/improve-documentation

## Отправка ответов (`test_answer_submission.py`)

Этот тест предназначен для имитации отправки ответов на вопросы экспертом и проверки их появления в панели модерации.

### Параметры запуска
Количество отправляемых ответов контролируется переменной окружения `NUM_ANSWERS_TO_SUBMIT`.

*   **Отправить 1 ответ для каждого из 3-х сценариев (всего 3 тест-кейса):**
    ```bash
    python -m pytest tests/integration/test_answer_submission.py
    ```

*   **Отправить N ответов для каждого сценария (например, 5):**
    ```bash
    NUM_ANSWERS_TO_SUBMIT=5 python -m pytest tests/integration/test_answer_submission.py
    ```

### Критерии выбора вопроса
Тест поддерживает три критерия выбора вопроса для ответа (параметризация):
- `latest`: Ответить на самый свежий вопрос.
- `zero_answers`: Ответить на вопрос без ответов.
- `by_author`: Ответить на вопрос от указанного автора (требует установки `TARGET_ANSWER_USER`).

### Отчетность
Каждый отправленный ответ будет отображаться как отдельный тестовый кейс в отчете Allure.

<<<<<<< HEAD
---

=======
>>>>>>> docs/improve-documentation
## Публикация ответов (`test_publish_answer_api.py`)

Этот тест предназначен для имитации публикации (модерации) ответов через административный API. Он поддерживает выбор типа публикации и ответа по различным критериям.

### Параметры запуска
*   **Режим публикации (`PUBLISH_ANSWER_MODE`):** Определяет тип публикации ответа.
    *   `default` (по умолчанию): Стандартный ответ (`ANSWER`).
    *   `supportive`: Поддерживающий ответ (`SUPPORTIVE`).
    *   `maximum`: Максимально полный ответ (`MAXIMUM`).
    *   `other`: Другой тип ответа (`OTHER`).
    *   `random`: Случайный тип из доступных.
    *   `all`: Запуск теста для всех типов ответов (4 тест-кейса).
<<<<<<< HEAD
*   **Критерий выбора ответа (`PUBLISH_ANSWER_SELECTOR`):** 
=======
*   **Критерий выбора ответа (`PUBLISH_ANSWER_SELECTOR`):**
>>>>>>> docs/improve-documentation
    *   `latest` (по умолчанию): Самый свежий ответ.
    *   `by_user`: Поиск по имени пользователя (требует `TARGET_ANSWER_USER`).
    *   `by_marker`: Поиск по текстовому маркеру (требует `TARGET_ANSWER_MARKER`).

### Примеры запуска
*   **Публикация ответа стандартного типа:**
    ```bash
    python -m pytest tests/integration/test_publish_answer_api.py
    ```

*   **Публикация ответа с выбором по маркеру:**
    ```bash
    PUBLISH_ANSWER_SELECTOR=by_marker TARGET_ANSWER_MARKER="MARKER_123" python -m pytest tests/integration/test_publish_answer_api.py
    ```

*   **Публикация всех типов ответов:**
    ```bash
    PUBLISH_ANSWER_MODE=all python -m pytest tests/integration/test_publish_answer_api.py
    ```

### Отчетность
<<<<<<< HEAD
Каждая операция публикации ответа будет отображаться как отдельный тестовый кейс в отчете Allure. 
=======
Каждая операция публикации ответа будет отображаться как отдельный тестовый кейс в отчете Allure.
>>>>>>> docs/improve-documentation
