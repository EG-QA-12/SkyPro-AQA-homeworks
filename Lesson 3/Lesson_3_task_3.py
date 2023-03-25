from Address import Address
from Mailing import Mailing

# создаем два адреса
to_address = Address("123456", "Москва", "Красная площадь", "1", "2")
from_address = Address("654321", "Санкт-Петербург", "Невский проспект", "3", "4")

# создаем почтовое отправление
mailing = Mailing(to_address, from_address, 1000, "ABC123")

# печатаем информацию о почтовом отправлении
print(f"Отправление {mailing.track} из {mailing.from_.city}, {mailing.from_.street}, {mailing.from_.house}-{mailing.from_.apartment} в {mailing.to.city}, {mailing.to.street}, {mailing.to.house}-{mailing.to.apartment}. Стоимость {mailing.cost} рублей.")
