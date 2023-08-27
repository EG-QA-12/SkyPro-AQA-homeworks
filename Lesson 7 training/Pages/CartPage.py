class CartPage:

    def __init__(self, browser):
        self._driver = browser

        def get():

            self._driver.get("https://www.labirint.ru/cart")