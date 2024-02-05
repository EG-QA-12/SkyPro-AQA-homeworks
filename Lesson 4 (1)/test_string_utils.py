import pytest
import re
from collections import Counter
from string_utils import StringUtils


class TestStringUtils:
    
    def setup_method(self):
        self.string_utils = StringUtils()

    def teardown_method(self):
        del self.string_utils

    # Оставляем только один статический метод, который используется в других тестах.
    @staticmethod
    def test_reverse_string(string_utils):
        assert string_utils.reverse_string("Test") == "tseT"
        assert string_utils.reverse_string("123") == "321"
        assert string_utils.reverse_string("04 апреля 2023") == "3202 ылерпа 40"

    def test_is_palindrome(self):
        assert self.string_utils.is_palindrome("level") == True
        assert self.string_utils.is_palindrome("radar") == True
        assert self.string_utils.is_palindrome("test") == False

    def test_swap_case(self):
        assert self.string_utils.swap_case("TeSt") == "tEsT"
        assert self.string_utils.swap_case("123") == "123"
        assert self.string_utils.swap_case("04 апреля 2023") == "04 АПРЕЛЯ 2023"

    def test_strip_punctuation(self):
        assert self.string_utils.strip_punctuation("Test!@#$%^&*()_+-={}|[]\\:\";'<>?,./") == "Test"
        assert self.string_utils.strip_punctuation("123") == "123"
        assert self.string_utils.strip_punctuation("04 апреля 2023!") == "04 апреля 2023"

    def test_count_words(self):
        assert self.string_utils.count_words("Test string.") == 2
        assert self.string_utils.count_words("123 456 789") == 3
        assert self.string_utils.count_words("04 апреля 2023") == 3

    def test_longest_word(self):
        assert self.string_utils.longest_word("Test string.") == "string"
        assert self.string_utils.longest_word("123 456 789") == "123"
        assert self.string_utils.longest_word("04 апреля 2023") == "апреля"

    def test_most_common_words(self):
        assert self.string_utils.most_common_words("Test string. Test string.") == ["Test", "string."]
        assert self.string_utils.most_common_words("123 456 789 123 456") == ["123", "456"]
        assert self.string_utils.most_common_words("Test 123 123 Test Test") == ["Test", "123"]
        
    # Добавляем тест для исключительной ситуации, когда передан пустой текст.
    def test_empty_string(self):
        assert self.string_utils.reverse_string("") == ""
        assert self.string_utils.is_palindrome("") == True
        assert self.string_utils.swap_case("") == ""
        assert self.string_utils.strip_punctuation("") == ""
        assert self.string_utils.count_words("") == 0
        assert self.string_utils.longest_word("") == ""
        assert self.string_utils.most_common_words("") == []
