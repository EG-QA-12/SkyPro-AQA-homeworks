from Smartphone import Smartphone

catalog = [
    Smartphone('Apple', 'iPhone 13 Pro', '+79991234567'),
    Smartphone('Samsung', 'Galaxy S21', '+79991234568'),
    Smartphone('Xiaomi', 'Mi 11', '+79991234569'),
    Smartphone('OnePlus', '9 Pro', '+79991234570'),
    Smartphone('Google', 'Pixel 5', '+79991234571'),
]

for phone in catalog:
    print(f"{phone.brand} - {phone.model}. {phone.phone_number}")
