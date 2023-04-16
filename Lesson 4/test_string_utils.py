
import pytest
from string_utils import StringUtils
string_utils = StringUtils ()

class TestStringUtils:

    def test_reverse_string(self):
        string_utils = StringUtils ()
        assert StringUtils.reverse_string("Test") == "tseT"
        assert StringUtils.reverse_string("123") == "321"
        assert StringUtils.reverse_string("04 апреля 2023") == "3202 ылерпа 40"

    def test_is_palindrome(self):
        string_utils = StringUtils ()
        assert StringUtils.is_palindrome("level") == True
        assert StringUtils.is_palindrome("radar") == True
        assert StringUtils.is_palindrome("test") == False

    def test_swap_case(self):
        string_utils = StringUtils ()
        assert StringUtils.swap_case("TeSt") == "tEsT"
        assert StringUtils.swap_case("123") == "123"
        assert StringUtils.swap_case("04 апреля 2023") == "04 АПРЕЛЯ 2023"

    def test_strip_punctuation(self):
        string_utils = StringUtils ()
        assert StringUtils.strip_punctuation("Test!@#$%^&*()_+-={}|[]\\:\";'<>?,./") == "Test"
        assert StringUtils.strip_punctuation("123") == "123"
        assert StringUtils.strip_punctuation("04 апреля 2023!") == "04 апреля 2023"

    def test_count_words(self):
        string_utils = StringUtils ()
        assert StringUtils.count_words("Test string.") == 2
        assert StringUtils.count_words("123 456 789") == 3
        assert StringUtils.count_words("04 апреля 2023") == 3

    def test_longest_word(self):
        string_utils = StringUtils ()
        assert StringUtils.longest_word("Test string.") == "string"
        assert StringUtils.longest_word("123 456 789") == "123"
        assert StringUtils.longest_word("04 апреля 2023") == "апреля"

    def test_most_common_words(self):
        string_utils = StringUtils ()
        assert StringUtils.most_common_words("Test string. Test string.") == ["test", "string"]
        assert StringUtils.most_common_words("123 456 789 123 456") == ["123", "456"]
        assert StringUtils.most_common_words("04 апреля 2023 04 04 2023") == ["04", "апреля", "2023"]
    
    # Проверка негативных сценариев
    def test_reverse_string_empty(self):
        string_utils = StringUtils ()
        assert StringUtils.reverse_string("") == ""

    def test_reverse_string_space(self):
        string_utils = StringUtils ()
        assert StringUtils.reverse_string(" ") == " "

    def test_reverse_string_none(self):
        string_utils = StringUtils ()
        assert StringUtils.reverse_string(None) is None

    def test_is_palindrome_empty(self):
        string_utils = StringUtils ()
        assert StringUtils.is_palindrome("") == False

    def test_is_palindrome_space(self):
        string_utils = StringUtils ()
        assert StringUtils.is_palindrome(" ") == False

