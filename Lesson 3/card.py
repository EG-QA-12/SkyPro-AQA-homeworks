class Card:
    number = '0000 0000 0000 0000'
    validDate = '01/99'
    holder = 'unknown'

    def __init__(self, number, date, holder):
        self.holder = holder
        self.number = number
        self.validDate = date

    def pay (self, amount):
        print("c карты", self.number," списали", amount)

