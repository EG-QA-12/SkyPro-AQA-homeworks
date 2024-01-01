class LoginPage:
    def __init__(self, driver):
        self.driver = driver

    def login_as_standard_user(self, username, password):
        self.driver.find_element_by_xpath('//*[@id="user-name"]').send_keys(username)
        self.driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
        self.driver.find_element_by_xpath('//*[@id="login-button"]').click()
