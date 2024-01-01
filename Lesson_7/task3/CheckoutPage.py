class CheckoutPage:
    def __init__(self, driver):
        self.driver = driver

    def fill_shipping_info(self, first_name, last_name, postal_code):
        self.driver.find_element_by_xpath('//*[@id="first-name"]').send_keys(first_name)
        self.driver.find_element_by_xpath('//*[@id="last-name"]').send_keys(last_name)
        self.driver.find_element_by_xpath('//*[@id="postal-code"]').send_keys(postal_code)
        self.driver.find_element_by_xpath('//*[@id="continue"]').click()

    def get_total_price(self):
        return self.driver.find_element_by_xpath('//*[@class="summary_info_label summary_total_label"]/following-sibling::div').text

    def finish_order(self):
        self.driver.find_element_by_xpath('//*[@id="finish"]').click()
