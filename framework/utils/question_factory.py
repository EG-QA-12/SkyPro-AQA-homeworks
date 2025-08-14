import random


class QuestionFactory:
    def __init__(self):
        self.categories = {
            "регистрация": [
                "Как зарегистрироваться на сайте?",
                "Нужно ли подтверждать email при регистрации?",
                "Можно ли зарегистрироваться через социальные сети?",
            ],
            "вход": [
                "Я забыл пароль, что делать?",
                "Почему я не могу войти в аккаунт?",
            ],
            "платежи": [
                "Какие способы оплаты вы принимаете?",
                "Как отменить подписку?",
            ]
        }

    def generate_question(self, category: str = "регистрация") -> str:
        questions = self.categories.get(category, [])
        if not questions:
            return "Вопрос по умолчанию"
        return random.choice(questions)
