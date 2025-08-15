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

    def generate_answer_text(self) -> str:
        """Генерирует случайный текст ответа для теста."""
        templates = [
            "Согласно текущему законодательству, вам следует...",
            "В вашей ситуации рекомендуется предпринять следующие шаги:",
            "Наиболее оптимальным решением будет...",
            "На основании предоставленной информации, можно сделать вывод, что...",
        ]
        unique_part = random.randint(1000, 9999)
        return f"{random.choice(templates)} (тех. ID {unique_part})"