import math

def square():
    side = float(input("Введите сторону квадрата: "))
    area = side * side
    if not isinstance(area, int):
        area = math.ceil(area)
    return area

# Пример использования функции:
result = square()
print(f"Площадь квадрата равна {result}")
