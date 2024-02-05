"""
Module Description: This module contains tests for simple HTTP requests using the requests library.
"""
import requests
base_url = "https://x-clients-be.onrender.com"
def test_simple_req():
    """
    Function Description: Test the simple HTTP request using the requests library.
    """
    resp = requests.get(base_url +'/company')

    response_body = resp.json()
    first_company = response_body[0]
    assert first_company ["name"] == "Клининг-центр 'Клинг-кинг'"  # Update the expected value
    assert resp.status_code == 200
    assert resp.headers["Content-type"] == "application/json; charset=utf-8"

def test_auth():
    creds = {
        "username": "leonardo",
        "password": "leads"
    }

    resp = requests.post(base_url + '/auth/login', json=creds)
    token = resp.json()["userToken"]
    assert resp.status_code == 201
    print(token)  # Indent this line properly


def test_create_company ():
    creds = {
        "username": "leonardo",
        "password": "leads"

    }
    company = {
        "name": "python",
        "description" : "requests"
    }

    #авторизация
    resp = requests.post(base_url + '/auth/login', json=creds)
    token = resp.json()["userToken"]

    #создание
    my_headers= {}
    my_headers["x-client-token"] = token

    resp = requests.post(base_url + '/company', json=company, headers =my_headers)
    assert resp.status_code == 201