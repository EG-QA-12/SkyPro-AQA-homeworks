class StringUtils:
    @staticmethod
    def reverse_string(string):
        if string is None:
            return None
        return string[::-1]

    @staticmethod
    def is_palindrome(string):
        if string is None:
            return False
        return string == string[::-1]

    @staticmethod
    def swap_case(string):
        return string.swapcase()

    @staticmethod
    def strip_punctuation(string):
        return "".join(c for c in string if c.isalnum() or c.isspace())

    @staticmethod
    def count_words(string):
        return len(string.split())

    @staticmethod
    def longest_word(string):
        words = string.split()
        return max(words, key=len)

    @staticmethod
    def most_common_words(string):
        words = string.split()
        word_counts = {}
        for word in words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [x[0] for x in sorted_words if x[1] == sorted_words[0][1]]

    @staticmethod
    def capitalize_words(string):
        words = string.split()
        return " ".join([word.capitalize() for word in words])