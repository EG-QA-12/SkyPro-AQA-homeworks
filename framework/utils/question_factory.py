#!/usr/bin/env python3
"""
Фабрика тестовых вопросов

Генерирует разнообразные и уникальные вопросы для тестирования
с множественными переменными для максимальной уникальности.
"""

import random
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QuestionTemplate:
    """Шаблон вопроса с переменными"""
    template: str
    variables: Dict[str, List[str]]
    category: str


class QuestionFactory:
    """
    Фабрика для создания разнообразных тестовых вопросов
    
    Генерирует уникальные вопросы с множественными переменными
    для обеспечения максимальной уникальности тестов.
    """
    
    def __init__(self):
        """Инициализация фабрики с шаблонами вопросов"""
        self.templates = [
            QuestionTemplate(
                template="Как зарегистрировать {entity_type} в Беларуси? {procedure_detail} {location} {random_suffix}",
                variables={
                    "entity_type": ["ООО", "ИП", "УП", "ЗАО", "ОАО", "ЧУП"],
                    "procedure_detail": [
                        "Какие документы нужны?",
                        "Сколько времени занимает процедура?",
                        "Какие есть особенности?",
                        "Какие требования предъявляются?",
                        "Какой порядок регистрации?"
                    ],
                    "location": ["в Минске", "в Гомеле", "в Могилеве", "в Витебске", "в Гродно", "в Бресте"],
                    "random_suffix": ["Тест", "Проверка", "Вопрос", "Запрос", "Исследование"]
                },
                category="регистрация"
            ),
            QuestionTemplate(
                template="Какие существуют виды {contract_type} в Беларуси? {aspect} {legal_basis} {random_suffix}",
                variables={
                    "contract_type": ["договоров займа", "лицензий", "разрешений", "соглашений", "контрактов"],
                    "aspect": [
                        "Каков порядок получения?",
                        "Какие требования предъявляются?",
                        "Какие документы нужны?",
                        "Сколько стоит оформление?",
                        "Какие есть ограничения?"
                    ],
                    "legal_basis": [
                        "согласно законодательству",
                        "по действующему праву",
                        "в соответствии с кодексом",
                        "по установленным правилам"
                    ],
                    "random_suffix": ["Тест", "Проверка", "Вопрос", "Запрос", "Исследование"]
                },
                category="договоры"
            ),
            QuestionTemplate(
                template="Процедура {action} {entity} в Беларуси. {detail} {location} {random_suffix}",
                variables={
                    "action": ["ликвидации", "реорганизации", "перерегистрации", "изменения", "преобразования"],
                    "entity": ["юридического лица", "ИП", "ООО", "предприятия", "организации"],
                    "detail": [
                        "Какие документы требуются?",
                        "Сколько времени занимает?",
                        "Какие есть особенности?",
                        "Какие требования предъявляются?",
                        "Какой порядок действий?"
                    ],
                    "location": ["в Минске", "в Гомеле", "в Могилеве", "в Витебске", "в Гродно", "в Бресте"],
                    "random_suffix": ["Тест", "Проверка", "Вопрос", "Запрос", "Исследование"]
                },
                category="процедуры"
            ),
            QuestionTemplate(
                template="Какие {tax_type} {entity_type} в Беларуси? {question_detail} {period} {random_suffix}",
                variables={
                    "tax_type": ["налоги", "сборы", "платежи", "обязательства", "отчисления"],
                    "entity_type": ["платит ООО", "платит ИП", "платит предприятие", "платит организация"],
                    "question_detail": [
                        "Какие ставки применяются?",
                        "Какие льготы предусмотрены?",
                        "Какие сроки уплаты?",
                        "Какие отчеты сдаются?",
                        "Какие документы нужны?"
                    ],
                    "period": [
                        "в 2024 году",
                        "в текущем году",
                        "в следующем году",
                        "ежеквартально",
                        "ежемесячно"
                    ],
                    "random_suffix": ["Тест", "Проверка", "Вопрос", "Запрос", "Исследование"]
                },
                category="налоги"
            )
        ]
    
    def generate_question(self, category: str = None) -> str:
        """
        Генерирует уникальный тестовый вопрос
        
        Args:
            category: Категория вопроса (регистрация, договоры, процедуры, налоги)
            
        Returns:
            str: Уникальный вопрос с множественными переменными
        """
        # Выбираем шаблон
        if category:
            available_templates = [t for t in self.templates if t.category == category]
        else:
            available_templates = self.templates
        
        if not available_templates:
            available_templates = self.templates
        
        template = random.choice(available_templates)
        
        # Заполняем переменные
        question_vars = {}
        for var_name, var_options in template.variables.items():
            question_vars[var_name] = random.choice(var_options)
        
        # Добавляем уникальный идентификатор
        timestamp = datetime.now().strftime("%H%M%S")
        random_num = random.randint(100, 999)
        question_vars["random_suffix"] = f"{question_vars['random_suffix']} {timestamp}{random_num}"
        
        # Формируем вопрос
        question = template.template.format(**question_vars)
        
        return question
    
    def generate_multiple_questions(self, count: int = 5, category: str = None) -> List[str]:
        """
        Генерирует несколько уникальных вопросов
        
        Args:
            count: Количество вопросов
            category: Категория вопросов
            
        Returns:
            List[str]: Список уникальных вопросов
        """
        questions = []
        for _ in range(count):
            question = self.generate_question(category)
            if question not in questions:  # Избегаем дублирования
                questions.append(question)
        
        return questions
    
    def get_categories(self) -> List[str]:
        """Возвращает доступные категории вопросов"""
        return list(set(template.category for template in self.templates)) 