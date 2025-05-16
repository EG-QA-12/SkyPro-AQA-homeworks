from faker import Faker

fake = Faker('ru_RU')

def generate_teacher():
    return {
        'teacher_id': fake.random_int(min=10000, max=99999),
        'email': fake.email(),
        'group_id': fake.random_int(min=100, max=999),
        'new_email': fake.email()
    }

def generate_teachers(n=5):
    return [generate_teacher() for _ in range(n)]
