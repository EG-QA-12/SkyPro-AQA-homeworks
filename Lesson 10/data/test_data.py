"""Тестовые данные для тестов БД и API."""

# Валидные тестовые данные учителей
VALID_TEACHERS = [
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

# Невалидные email для негативных тестов
INVALID_EMAILS = [
    'invalid_email',     # Некорректный формат
    'test@',            # Нет домена
    '@test.com',         # Нет локальной части
    'test@test',         # Нет доменной зоны
    '',                  # Пустая строка
    None,                # Значение None
    'a' * 256 + '@test.com'  # Слишком длинный email
]

# Невалидные ID для негативных тестов
INVALID_IDS = [-1, 0, None]

# Невалидные ID групп для негативных тестов
INVALID_GROUP_IDS = [-1, 0, None, 'abc']

# Данные для формы
FORM_VALID_DATA = {
    'first_name': 'Иван',
    'last_name': 'Петров',
    'address': 'Ленина, 55-3',
    'city': 'Москва',
    'country': 'Россия',
    'email': 'test@skypro.com',
    'phone': '+7985899998787',
    'job_position': 'QA',
    'company': 'SkyPro'
}

# Данные для калькулятора
CALCULATOR_TEST_DATA = [
    {
        'first_number': '7',
        'operator': '+',
        'second_number': '8',
        'expected_result': '15',
        'delay': '45'
    },
    {
        'first_number': '10',
        'operator': '-',
        'second_number': '3',
        'expected_result': '7',
        'delay': '30'
    },
    {
        'first_number': '5',
        'operator': '*',
        'second_number': '6',
        'expected_result': '30',
        'delay': '20'
    }
]

# Данные для интернет-магазина
SHOPPING_TEST_DATA = {
    'products': [
        'Sauce Labs Backpack',
        'Sauce Labs Bolt T-Shirt',
        'Sauce Labs Onesie'
    ],
    'user_info': {
        'first_name': 'Evgeny',
        'last_name': 'Gusinets',
        'postal_code': '246006'
    },
    'expected_total': '58.29'
}
