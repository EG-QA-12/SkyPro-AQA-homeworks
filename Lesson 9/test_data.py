"""Тестовые данные для тестов БД."""

TEST_TEACHERS = [
    {
        'teacher_id': 12133,
        'email': 'teacher_inna@mail.com',
        'group_id': 345,
        'new_email': 'new-email@mail.com'
    },
    {
        'teacher_id': 12134,
        'email': 'teacher_anna@mail.com',
        'group_id': 346,
        'new_email': 'anna-new@mail.com'
    }
]

INVALID_EMAILS = [
    'invalid_email',     # Некорректный формат
    'test@',            # Нет домена
    '@test.com',        # Нет локальной части
    'test@test',        # Нет доменной зоны
    '',                 # Пустая строка
    None,               # Значение None
    'a' * 256 + '@test.com'  # Слишком длинный email
]

INVALID_IDS = [-1, 0, None]
INVALID_GROUP_IDS = [-1, 0, None, 'abc']
