import pytest
from string_utils import StringUtils

string_utils = StringUtils()

# Позитивные тесты

def test_capitalize():
    assert string_utils.capitalize("тест") == "Тест"

def test_lower():
    assert string_utils.lower("Тест") == "тест"

def test_upper():
    assert string_utils.upper("Тест") == "ТЕСТ"

def test_trim():
    assert string_utils.trim("   04 апреля 2023") == "04 апреля 2023"

def test_strip():
    assert string_utils.strip("   04 апреля 2023   ") == "04 апреля 2023"

def test_to_list():
    assert string_utils.to_list("a,b,c,d") == ["a", "b", "c", "d"]

def test_to_delete_simbol():
    assert string_utils.delete_symbol("SkyPro", "Pro") == "Sky"

def test_to_starts_with():
    assert string_utils.starts_with("Skypro", "y") == False

def test_to_starts_with():
    assert string_utils.starts_with("Skypro", "S") == True

# Негативные тесты

def test_capitalize_empty_string():
    assert string_utils.capitalize("") == ""

def test_lower_empty_string():
    assert string_utils.lower("") == ""

def test_trim_empty_string():
    assert string_utils.trim(" ") == ""

def test_strip_empty_string():
    assert string_utils.strip("     ") == ""

def test_with_none():
    assert string_utils.capitalize(None) is None

def test_to_list_empty_string():
    assert string_utils.to_list("") == []