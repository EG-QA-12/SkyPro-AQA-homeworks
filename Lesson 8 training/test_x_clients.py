import requests
from CompanyApi import CompanyApi

api  = CompanyApi("https://x-clients-be.onrender.com")

def test_get_companies():
    body = api.get_company_list()
    assert len(body) > 0

def test_get_active_companies():
    #1. Получить список всех компаний
    full_list = api.get_company_list()
    my_params = {'active': 'true'}

    # 2. Получить список активных компаний
    filter_list = api.get_company_list(params_to_add=my_params)

    # 3. Проверить ,что список 1> списка 2
    assert len(full_list) > len(filter_list)

def get_company_list(params_to_add=None):
    resp = requests.get(base_url + '/company', params=params_to_add)
    return resp.json()

def get_token(self, user='michaelangelo', password='party-dude'):
    creds = {
        "username": user,
        "password": password
    }

    resp = requests.post(self.url + '/auth/login', json=creds)
    return resp.json()["userToken"]


def create_company(name, description):
    token = get_token(user='leonardo', password='leads')
    my_headers = {"x-client-token": token}
    company_data = {"name": name, "description": description}
    resp = requests.post(base_url + '/company', json=company_data, headers=my_headers)
    return resp.json()



def test_get_active_companies2():
    full_list = get_company_list()
    filter_list = get_company_list(params_to_add={'active': 'true'})
    assert len(full_list) > len(filter_list)

def test_add_new():
    body = api.get_company_list()
    len_before = len(body)
    new_company_name = "Autotest"
    new_company_description = "Descr"
    create_company(new_company_name, new_company_description)
    body = api.get_company_list()
    len_after = len(body)
    assert len_after - len_before == 1
    assert body[-1]["name"] == new_company_name
    assert body[-1]["description"] == new_company_description

def test_auth():
    creds = {
        "username": "leonardo",
        "password": "leads"
    }
    resp = requests.post(base_url + '/auth/login', json=creds)
    assert resp.status_code == 201
    assert "userToken" in resp.json()

def test_create_company():
    company_name = "Python"
    company_description = "Requests"
    result = api.create_company(company_name, company_description)
    assert result["name"] == company_name
    assert result["description"] == company_description
    assert "id" in result

def test_get_one_company():
    company_name = 'VS Code'
    company_description = 'IDE'
    result = api.create_company(company_name, company_description)
    new_id = result["id"]

    new_company = api.get_company(new_id)

    assert new_company["id"] == new_id
    assert new_company["name"] == company_name
    assert new_company["description"] == company_description
    assert new_company["isActive"] == True
