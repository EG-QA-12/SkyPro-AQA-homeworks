import requests
import pytest
from CompanyApi import CompanyApi

api = CompanyApi("https://x-clients-be.onrender.com", user='leonardo', password='leads')

def test_auth():
    token = api.get_token()
    assert token is not None
