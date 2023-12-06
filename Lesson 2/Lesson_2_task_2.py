#def is_year_leap(year):
#    if year % 4 == 0:      # проверяем, делится ли год на 4 без остатка
#        return True       # если да, то год високосный
#    else:
 #       return False      # если нет, то год не високосный
    
#year = 2024     # передаем год 2024 в функцию is_year_leap
#is_leap = is_year_leap(year)  # сохраняем результат выполнения функции в переменной is_leap
#print('год {}: {}'.format(year, is_leap))

# либо так
    

def is_year_leap(year):
    if year % 4 == 0:            # проверяем, делится ли год на 4 без остатка
        return True              # если да, то год високосный
    else:
        return False             # если нет, то год не високосный

year = int(input())                  # передаем год 2024 в функцию is_year_leap
is_leap = is_year_leap(year)     # сохраняем результат выполнения функции в переменной is_leap
print(f"год {year}: {is_leap}")