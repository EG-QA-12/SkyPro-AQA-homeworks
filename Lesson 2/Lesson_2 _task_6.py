<<<<<<< HEAD
lst = [11, 5, 8, 32, 15, 3, 20, 132, 21, 4, 555, 9, 20] #  Создаем список lst с заданными элементами.

result = [x for x in lst if x < 30 and x % 3 == 0]      #Затем, с помощью генератора списков, создаем новый список result, содержащий только те элементы из списка lst, которые меньше 30 и делятся на 3 без остатка.

=======
lst = [11, 5, 8, 32, 15, 3, 20, 132, 21, 4, 555, 9, 20] #  Создаем список lst с заданными элементами.

result = [x for x in lst if x < 30 and x % 3 == 0]      #Затем, с помощью генератора списков, создаем новый список result, содержащий только те элементы из списка lst, которые меньше 30 и делятся на 3 без остатка.

>>>>>>> 44f8754237d5a2bc37d9c2959aec693ad55799ff
print(result)                                           #Наконец, выводим результат с помощью функции print().