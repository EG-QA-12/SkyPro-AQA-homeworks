"""
Module Description: This module contains tests for simple HTTP requests using the requests library.
"""
import requests

base_url = "https://x-clients-be.onrender.com"

def get_company_list(params_to_add = None):
    resp = requests.get(base_url + '/company', params=params_to_add)
    return resp.json()



def test_get_companies():
    resp = requests.get(base_url + '/company')
    body = resp.json()

    assert resp.status_code == 200
    assert len(body) > 0  # ==x


def test_get_active_companies():
    #1. Получить список всех компаний
    resp = get_company_list
    full_list = resp.json()

    #2. Получить список активных компаний
    my_params = {
        'active' : 'true',
        'abc' : '123'
        }

    resp = get_company_list (params=my_params)
    filter_list = resp.json()

    #3. Проверить, что список 1 > списка 2
    assert len(full_list) > len(filter_list) # ==x

def test_get_active_companies2():
        # 1. Получить список всех компаний
        resp = get_company_list
        full_list = resp.json()

        # 2. Получить список активных компаний
        resp = get_company_list (params_to_add={'active': 'true'})
        filter_list = resp.json()

        # 3. Проверить, что список 1 > списка 2
        assert len(full_list) > len(filter_list)



def test_add_new():
    # получить количество компаний
    resp = get_company_list
    body = resp.json()
    len_before = len(body)

    # создать новую компанию
    # получить количество компаний
    resp = get_company_list
    body = resp.json()
    len_after = len(body)
    # проверить, что +1
    # 



    resp = requests.get(base_url + '/company?active=true')
    body = resp.json()
    assert resp.status_code == 200
    assert len(body) > 0  # ==x


def test_auth():
    creds = {
        "username": "leonardo",
        "password": "leads"
    }

    resp = requests.post(base_url + '/auth/login', json=creds)
    token = resp.json()["userToken"]
    assert resp.status_code == 201
    print(token)  # Indent this line properly


def test_create_company():
    creds = {
        "username": "leonardo",
        "password": "leads"

    }
    company = {
        "name": "python",
        "description": "requests"
    }

    # авторизация
    resp = requests.post(base_url + '/auth/login', json=creds)
    token = resp.json()["userToken"]

    # создание
    my_headers = {}
    my_headers["x-client-token"] = token

    resp = requests.post(base_url + '/company', json=company, headers=my_headers)
    assert resp.status_code == 201
