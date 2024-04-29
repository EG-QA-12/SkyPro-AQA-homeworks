import requests

class CompanyApi:

    def __init__(self,url):
        self.url = url


    def get_company_list(self, params_to_add=None):
        resp = requests.get(self.url + '/company', params=params_to_add)
        return resp.json()


    def get_token(self, user='michaelangelo', password='party-dude'):
        creds = {
            "username": "user",
            "password": "password"
        }

        resp = requests.post(self.url + '/auth/login', json=creds)
        return resp.json()["userToken"]

    def get_company(self,id):
        resp = requests.get(self.url + '/company'+str(id))
        return resp.json()
    def create_company(self, name, description = ''):
        creds = {
                "name": name,
                "description": description
            }

        my_headers = {}
        my_headers ["x-client-token"] = self.get_token()
        resp = requests.post(base_url + '/company', json=company, headers=my_headers)
        return resp.json()
