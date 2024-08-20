import requests

class Company:
    """
    Класс для взаимодействия с API управления сотрудниками и компаниями.
    """

    def __init__(self, url):
        """
        Инициализация класса с базовым URL API.

        :param url: URL API
        """
        self.url = url
        self.headers = None

    def get_token(self, user='bloom', password='fire-fairy'):
        """
        Получение токена авторизации.

        :param user: Имя пользователя для авторизации
        :param password: Пароль пользователя для авторизации
        :return: Авторизационный токен
        """
        creds = {
            'username': user,
            'password': password
        }
        resp = requests.post(f"{self.url}/auth/login", json=creds)
        resp.raise_for_status()  # Проверка успешности запроса
        self.headers = {
            "x-client-token": resp.json()["userToken"]
        }

    def create_company(self, name, description=''):
        """
        Создание новой компании.

        :param name: Название компании
        :param description: Описание компании
        :return: Данные созданной компании
        """
        company = {
            "name": name,
            "description": description
        }
        if not self.headers:
            self.get_token()

        resp = requests.post(f"{self.url}/company", json=company, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_list_employee(self, company_id):
        """
        Получение списка сотрудников по ID компании.

        :param company_id: ID компании
        :return: Список сотрудников
        """
        my_params = {
            "company": company_id
        }
        resp = requests.get(f"{self.url}/employee", params=my_params, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def get_employee_by_id(self, employee_id):
        """
        Получение информации о сотруднике по его ID.

        :param employee_id: ID сотрудника
        :return: Данные сотрудника
        """
        resp = requests.get(f"{self.url}/employee/{employee_id}", headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def add_new_employee(self, company_id, name, last_name, email="test@test.ru", phone="89999999999", birthdate="2024-08-13T14:05:19.766Z"):
        """
        Добавление нового сотрудника.

        :param company_id: ID компании
        :param name: Имя сотрудника
        :param last_name: Фамилия сотрудника
        :param email: Электронная почта сотрудника
        :param phone: Номер телефона сотрудника
        :param birthdate: Дата рождения сотрудника
        :return: Данные добавленного сотрудника
        """
        employee = {
            "firstName": name,
            "lastName": last_name,
            "middleName": "-",
            "companyId": company_id,
            "email": email,
            "url": "string",
            "phone": phone,
            "birthdate": birthdate,
            "isActive": True
        }

        resp = requests.post(f"{self.url}/employee", headers=self.headers, json=employee)
        resp.raise_for_status()
        return resp.json()

    def update_employee_info(self, employee_id, last_name, email):
        """
        Обновление информации о сотруднике.

        :param employee_id: ID сотрудника
        :param last_name: Новая фамилия сотрудника
        :param email: Новая электронная почта сотрудника
        :return: Обновленные данные сотрудника
        """
        user_info = {
            "lastName": last_name,
            "email": email,
            "isActive": True
        }

        resp = requests.patch(f"{self.url}/employee/{employee_id}", headers=self.headers, json=user_info)
        resp.raise_for_status()
        return resp.json()
