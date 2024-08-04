import requests
import logging

class EmployeesApi:
    def __init__(self, url):
        self.url = url
        self.logger = logging.getLogger(__name__)

    def get_token(self, user='raphael', password='cool-but-crude'):
        """
        Получает токен пользователя для аутентификации.

        :param user: Имя пользователя для аутентификации.
        :param password: Пароль пользователя для аутентификации.
        :return: Возвращает токен пользователя.
        """
        creds = {
            'username': user,
            'password': password
        }
        try:
            resp = requests.post(self.url + '/auth/login', json=creds)
            resp.raise_for_status()
            return resp.json()['userToken']
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch token: {e}")
            raise  # Повторное возбуждение исключения для обработки в вызывающем коде

    def create_company(self, name, description=""):
        """
        Создает новую компанию.

        :param name: Название компании.
        :param description: Описание компании (по умолчанию "").
        :return: Возвращает JSON-ответ с информацией о созданной компании.
        """
        company = {
            "name": name,
            "description": description
        }
        headers = {"x-client-token": self.get_token()}
        try:
            resp = requests.post(self.url + '/company', json=company, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to create company: {e}")
            raise

    def get_employee(self, id):
        """
        Получает информацию о сотруднике по его идентификатору.

        :param id: Идентификатор сотрудника.
        :return: Возвращает JSON-ответ с информацией о сотруднике.
        """
        try:
            resp = requests.get(self.url + '/employee/' + str(id))
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get employee {id}: {e}")
            raise

    # Добавьте аналогичные обработки и документацию для остальных методов (get_employees_list, create_employee, edit_employee, delete_employee)

    def delete_employee(self, id):
        headers = {"x-client-token": self.get_token()}
        try:
            resp = requests.delete(self.url + '/employee/' + str(id), headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to delete employee {id}: {e}")
            raise
