
def bank(X, Y):          # Для решения данной задачи нам необходимо произвести Y-количество итераций, на каждой из которых увеличиваем сумму вклада на 10% от текущей суммы вклада. 
    for i in range(Y):   # Для этого можно написать функцию, которая будет производить итерации и возвращать конечную сумму. 
        X = X * 1.1      # В этом примере мы передаем функции начальную сумму вклада X = 100000 и срок вклада Y = 5 лет. 
    return X             # Функция производит 5 итераций, на каждой из которых увеличивает сумму вклада на 10% от текущей суммы. 
result = bank(100000, 5) # В конечном итоге функция возвращает сумму, которая будет на счету пользователя спустя Y лет.
print(result)            # 161051.00000000006


