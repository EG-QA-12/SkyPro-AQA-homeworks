from address import Address
from mailing import Mailing
to_address = Address("456123", "Самара", "Победы", "14", "6")
from_address = Address("987654", "Казань", "Советская", "23", "7")
mailing = Mailing(to_address, from_address, 1000, "ABC123")
print(f"Отправление {mailing.track} из {mailing.from_address.index}, {mailing.from_address.city},"
      f"{mailing.from_address.street}, {mailing.from_address.house}, - {mailing.from_address.apartment}"
      f" в {mailing.to_address.index}, {mailing.to_address.city}, {mailing.to_address.street}, "
      f"{mailing.to_address.house} - {mailing.to_address.apartment}. Стоимость {mailing.cost} рублей.")