"""
Модуль для работы с почтовыми отправлениями.
"""

from Address import Address
from Mailing import Mailing

# Создаем два адреса
to_address = Address("123456", "Москва", "Красная площадь", "1", "2")
from_address = Address("654321", "Санкт-Петербург", "Невский проспект", "3", "4")

# Создаем почтовое отправление
mailing = Mailing(to_address, from_address, 1000, "ABC123")

# Печатаем информацию о почтовом отправлении
print(f"Отправление {mailing.track} из {mailing.from_.city}, {mailing.from_.street},"
      f" {mailing.from_.house}-{mailing.from_.apartment} в {mailing.to.city}, {mailing.to.street},"
      f"{mailing.to.house}-{mailing.to.apartment}. Стоимость {mailing.cost} рублей.")
