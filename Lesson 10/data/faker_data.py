"""Генерация тестовых данных через Faker."""

from typing import Dict, List, Any
from faker import Faker


# Инициализация Faker с русской локализацией
fake = Faker('ru_RU')


def generate_teacher() -> Dict[str, Any]:
    """
    Сгенерировать данные для одного учителя.
    
    Returns:
        Dict[str, Any]: Словарь с данными учителя
    """
    return {
        'teacher_id': fake.random_int(min=10000, max=99999),
        'email': fake.email(),
        'group_id': fake.random_int(min=100, max=999),
        'new_email': fake.email()
    }


def generate_teachers(n: int = 5) -> List[Dict[str, Any]]:
    """
    Сгенерировать данные для нескольких учителей.
    
    Args:
        n (int): Количество учителей для генерации
        
    Returns:
        List[Dict[str, Any]]: Список словарей с данными учителей
    """
    return [generate_teacher() for _ in range(n)]


def generate_form_data() -> Dict[str, str]:
    """
    Сгенерировать данные для формы.
    
    Returns:
        Dict[str, str]: Словарь с данными для формы
    """
    return {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'address': fake.address(),
        'city': fake.city(),
        'country': fake.country(),
        'email': fake.email(),
        'phone': fake.phone_number(),
        'job_position': fake.job(),
        'company': fake.company()
    }


def generate_invalid_email() -> str:
    """
    Сгенерировать невалидный email.
    
    Returns:
        str: Невалидный email адрес
    """
    invalid_emails = [
        fake.text(max_length=10),  # Без символа @
        f"{fake.user_name()}@",  # Без домена
        f"@{fake.domain_name()}",  # Без локальной части
        fake.text(max_length=300),  # Слишком длинный
    ]
    return fake.random.choice(invalid_emails)
