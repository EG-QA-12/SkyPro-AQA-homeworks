import requests

class CompanyApi:

    def __init__(self, url, user='michaelangelo', password='party-dude'):
        self.url = url
        self.user = user
        self.password = password

    def get_token(self):
        creds = {
            "username": self.user,
            "password": self.password
        }
        resp = requests.post(self.url + '/auth/login', json=creds)
        return resp.json()["userToken"]
