"""
Модуль для тестирования API управления сотрудниками.
"""

import pytest
import requests
from empl import Company

@pytest.fixture(scope="module")
def api_instance():
    """
    Фикстура для создания объекта API.
    """
    api = Company("https://x-clients-be.onrender.com")
    api.get_token()
    return api

@pytest.fixture
def company_fixture(api_instance):
    """
    Фикстура для создания новой компании перед каждым тестом.
    """
    return api_instance.create_company(name="TestCompany", description="Testing company creation")

def test_get_list_of_employees(api_instance, company_fixture):
    """
    Тест на получение пустого списка сотрудников новой компании.
    """
    employee_list = api_instance.get_list_employee(company_fixture["id"])
    assert len(employee_list) == 0

def test_add_new_employee(api_instance, company_fixture):
    """
    Тест на добавление нового сотрудника в компанию и проверку его данных.
    """
    new_employee = api_instance.add_new_employee(company_fixture["id"], "Evgeny1982", "Gusinets")
    assert new_employee["id"] > 0

    resp = api_instance.get_list_employee(company_fixture["id"])
    assert resp[0]["companyId"] == company_fixture["id"]
    assert resp[0]["firstName"] == "Evgeny1982"
    assert resp[0]["isActive"] is True  # Используем 'is True' для проверки

def test_get_employee_by_id(api_instance, company_fixture):
    """
    Тест на получение данных сотрудника по его ID.
    """
    new_employee = api_instance.add_new_employee(company_fixture["id"], "Evgeny1982", "Gusinets")
    employee_data = api_instance.get_employee_by_id(new_employee["id"])
    assert employee_data["firstName"] == "Evgeny1982"
    assert employee_data["lastName"] == "Gusinets"

def test_change_employee_info(api_instance, company_fixture):
    """
    Тест на изменение данных сотрудника.
    """
    new_employee = api_instance.add_new_employee(company_fixture["id"], "Evgeny1982", "Gusinets")
    updated_employee = api_instance.update_employee_info(new_employee["id"], "Gusinets", "test2@mail.ru")
    assert updated_employee["id"] == new_employee["id"]
    assert updated_employee["email"] == "test2@mail.ru"
    assert updated_employee["isActive"] is True  # Используем 'is True' для проверки

def test_add_employee_without_first_name(api_instance, company_fixture):
    """
    Негативный тест на добавление сотрудника без имени.
    """
    with pytest.raises(requests.exceptions.HTTPError):
        api_instance.add_new_employee(company_fixture["id"], "", "Gusinets")

def test_add_employee_without_last_name(api_instance, company_fixture):
    """
    Негативный тест на добавление сотрудника без фамилии.
    """
    with pytest.raises(requests.exceptions.HTTPError):
        api_instance.add_new_employee(company_fixture["id"], "Evgeny1982", "")

def test_add_employee_without_email(api_instance, company_fixture):
    """
    Негативный тест на добавление сотрудника без электронной почты.
    """
    with pytest.raises(requests.exceptions.HTTPError):
        api_instance.add_new_employee(company_fixture["id"], "Evgeny1982", "Gusinets", email="")

def test_add_employee_without_company_id(api_instance):
    """
    Негативный тест на добавление сотрудника без ID компании.
    """
    with pytest.raises(requests.exceptions.HTTPError):
        api_instance.add_new_employee(None, "Evgeny1982", "Gusinets")
