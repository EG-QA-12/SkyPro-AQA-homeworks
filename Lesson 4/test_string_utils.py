import pytest
from string_utils import StringUtils

string_utils = StringUtils()

# Функция capitalize принимает на вход текст, делает первую букву заглавной и возвращает этот же текст
def test_capitalize():
    assert string_utils.capitalize("тест") == "Тест"

# Функция lower принимает на вход текст, делает первую букву заглавной и возвращает этот же текст
def test_lower():
    assert string_utils.lower("Тест") == "тест"

# Функция upper принимает на вход текст, делает первую букву заглавной и возвращает этот же текст
def test_upper():
    assert string_utils.upper("Тест") == "ТЕСТ"

# Функция trim принимает на вход текст и удаляет пробелы в начале, если они есть
def test_trim():
    assert string_utils.trim("   04 апреля 2023") == "04 апреля 2023"

# Функция strip принимает на вход текст и удаляет пробелы в начале и конце, если они есть
def test_strip():
    assert string_utils.strip("   04 апреля 2023   ") == "04 апреля 2023"

# Функция to_list принимает на вход текст с разделителем и возвращает список строк
def test_to_list():
    assert string_utils.to_list("a,b,c,d") == ["a", "b", "c", "d"]

# Функция contains проверяет, содержит ли строка заданный символ
def test_contains():
    assert string_utils.contains("SkyPro", "S") is True

# Функция delete_symbol удаляет все подстроки из переданной строки
def test_delete_symbol():
    assert string_utils.delete_symbol("SkyPro", "Pro") == "Sky"

# Функция starts_with проверяет, начинается ли строка с заданного символа
def test_starts_with():
    assert string_utils.starts_with("Skypro", "S") == True

# Функция end_with проверяет, заканчивается ли строка заданным символом
def test_end_with():
    assert string_utils.end_with("Skypro", "o") == True

# Тесты для обработки пустой строки
def test_capitalize_empty_string():
    assert string_utils.capitalize("") == ""

def test_lower_empty_string():
    assert string_utils.lower("") == ""

def test_trim_empty_string():
    assert string_utils.trim(" ") == ""

def test_strip_empty_string():
    assert string_utils.strip("     ") == ""

# Тесты для обработки `None`
def test_capitalize_with_none():
    assert string_utils.capitalize(None) is None

def test_delete_symbol_with_none():
    assert string_utils.delete_symbol(None, 'a') is None

# Тесты для обработки строки с пробелом
def test_capitalize_with_spaces():
    assert string_utils.capitalize(" sky pro ") == "Sky Pro"

def test_lower_with_spaces():
    assert string_utils.lower(" sky pro ") == "sky pro"

def test_trim_with_spaces():
    assert string_utils.trim("   sky pro   ") == "sky pro"

def test_strip_with_spaces():
    assert string_utils.strip("   sky pro   ") == "sky pro"