<<<<<<< HEAD
def month_to_season(month: int) -> str:
    if month in [12, 1, 2]:
        return 'Зима'
    elif month in [3, 4, 5]:
        return 'Весна'
    elif month in [6, 7, 8]:
        return 'Лето'
    elif month in [9, 10, 11]:
        return 'Осень'
    else:
        return 'Неверный номер месяца'
season = month_to_season(2)
=======
def month_to_season(month: int) -> str:
    if month in [12, 1, 2]:
        return 'Зима'
    elif month in [3, 4, 5]:
        return 'Весна'
    elif month in [6, 7, 8]:
        return 'Лето'
    elif month in [9, 10, 11]:
        return 'Осень'
    else:
        return 'Неверный номер месяца'
season = month_to_season(2)
>>>>>>> 44f8754237d5a2bc37d9c2959aec693ad55799ff
print(season) # Выведет 'Зима'