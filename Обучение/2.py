from smartphone import Smartphone

catalog = []
phone1 = Smartphone("Apple", "iPhone 15", "+79876543221")
phone2 = Smartphone("Samsung", "Galaxy S22 Ultra", "+79511593625")
phone3 = Smartphone("Google", "Pixel 7", "+79234567889")
phone4 = Smartphone("Xiaomi", "Mi 10", "+79638524114")
phone5 = Smartphone("OnePlus", "10 Pro", "+79123356547")

catalog.append(phone1)
catalog.append(phone2)
catalog.append(phone3)
catalog.append(phone4)
catalog.append(phone5)

for phone in catalog:



    print(f"{phone.brand}. {phone.model}. {phone.phone_number}")