from selenium import webdriver

# Установите путь к драйверу веб-браузера, например, для Chrome
driver = webdriver.Chrome('путь_к_файлу_драйвера/chromedriver')

# Откройте веб-страницу
driver.get('https://www.aviasales.ru/')

# Найдите элемент логотипа с помощью CSS-селектора
logo = driver.find_element_by_css_selector('span[data-test-id="logo"]')

# Выведите текст элемента логотипа
print(logo.text)

# Закройте браузер
driver.quit()
