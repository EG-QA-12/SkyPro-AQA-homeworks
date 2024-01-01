class ProductPage:
    def __init__(self, driver):
        self.driver = driver

    def add_product_to_cart(self, product_locator):
        self.driver.find_element_by_xpath(product_locator).click()


class CartPage:
    def __init__(self, driver):
        self.driver = driver

    def proceed_to_checkout(self):
        self.driver.find_element_by_xpath('//*[@class="shopping_cart_link"]').click()
        self.driver.find_element_by_xpath('//*[@id="checkout"]').click()
