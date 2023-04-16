def capitalize(self, string: str) -> str:
    """
    Принимает на вход текст, делает первую букву заглавной и возвращает этот же текст
    Пример: `capitalize("skypro") -> "Skypro"`
    """
    return string.capitalize()

def trim(self, string: str) -> str:
    """
    Принимает на вход текст и удаляет пробелы в начале, если они есть
    Пример: `trim("   skypro") -> "skypro"`
    """
    return string.lstrip()  # заменил цикл на lstrip()

def to_list(self, string: str, delimiter: str = ",") -> list[str]:
    """
    Принимает на вход текст с разделителем и возвращает список строк. \n
    Параметры: \n 
        `string` - строка для обработки \n
        `delimiter` - разделитель строк. По умолчанию запятая (",") \n
    Пример 1: `to_list("a,b,c,d") -> ["a", "b", "c", "d"]`
    Пример 2: `to_list("1:2:3", ":") -> ["1", "2", "3"]`
    """
    if self.is_empty(string):
        return []
    
    return string.split(delimiter)

def contains(self, string: str, symbol: str) -> bool:
    """
    Возвращает `True`, если строка содержит искомый символ и `False` - если нет \n 
    Параметры: \n 
        `string` - строка для обработки \n
        `symbol` - искомый символ \n
    Пример 1: `contains("SkyPro", "S") -> True`
    Пример 2: `contains("SkyPro", "U") -> False`
    """
    return symbol in string  # заменил try-except на in

def delete_symbol(self, string: str, symbol: str) -> str:
    """
    Удаляет все подстроки из переданной строки \n 
    Параметры: \n 
        `string` - строка для обработки \n
        `symbol` - искомый символ для удаления \n
    Пример 1: `delete_symbol("SkyPro", "k") -> "SyPro"`
    Пример 2: `delete_symbol("SkyPro", "Pro") -> "Sky"`
    """
    return string.replace(symbol, "")  # убрал проверку на наличие символа

def starts_with(self, string: str, symbol: str) -> bool:
    """
    Возвращает `True`, если строка начинается с заданного символа и `False` - если нет \n 
    Параметры: \n 
        `string` - строка для обработки \n
        `symbol` - искомый символ \n
    Пример 1: `starts_with("SkyPro", "S") -> True`
    Пример 2: `starts_with("SkyPro", "P") -> False`
    """
    return string.startswith(symbol)

def end_with(self, string: str, symbol: str) -> bool:
