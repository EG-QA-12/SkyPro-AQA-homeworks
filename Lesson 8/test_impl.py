import pytest
import requests  # Добавляем импорт библиотеки requests
from empl import Company

@pytest.fixture(scope="module")
def api():
    """
    Фикстура для создания объекта API.
    """
    api_instance = Company("https://x-clients-be.onrender.com")
    api_instance.get_token()
    return api_instance

@pytest.fixture
def company(api):
    """
    Фикстура для создания новой компании перед каждым тестом.
    """
    return api.create_company(name="TestCompany", description="Testing company creation")

def test_get_list_of_employees(api, company):
    """
    Тест на получение пустого списка сотрудников новой компании.
    """
    employee_list = api.get_list_employee(company["id"])
    assert len(employee_list) == 0

def test_add_new_employee(api, company):
    """
    Тест на добавление нового сотрудника в компанию и проверку его данных.
    """
    new_employee = api.add_new_employee(company["id"], "Evgeny1982", "Gusinets")
    assert new_employee["id"] > 0

    resp = api.get_list_employee(company["id"])
    assert resp[0]["companyId"] == company["id"]
    assert resp[0]["firstName"] == "Evgeny1982"
    assert resp[0]["isActive"] == True
    assert resp[0]["lastName"] == "Gusinets"

def test_get_employee_by_id(api, company):
    """
    Тест на получение данных сотрудника по его ID.
    """
    new_employee = api.add_new_employee(company["id"], "Evgeny1982", "Gusinets")
    employee_data = api.get_employee_by_id(new_employee["id"])
    assert employee_data["firstName"] == "Evgeny1982"
    assert employee_data["lastName"] == "Gusinets"

def test_change_employee_info(api, company):
    """
    Тест на изменение данных сотрудника.
    """
    new_employee = api.add_new_employee(company["id"], "Evgeny1982", "Gusinets")
    updated_employee = api.update_employee_info(new_employee["id"], "Gusinets", "test2@mail.ru")
    assert updated_employee["id"] == new_employee["id"]
    assert updated_employee["email"] == "test2@mail.ru"
    assert updated_employee["isActive"] == True

def test_add_employee_without_first_name(api, company):
    """
    Негативный тест на добавление сотрудника без имени.
    """
    with pytest.raises(requests.exceptions.HTTPError):
        api.add_new_employee(company["id"], "", "Gusinets")

def test_add_employee_without_last_name(api, company):
    """
    Негативный тест на добавление сотрудника без фамилии.
    """
    with pytest.raises(requests.exceptions.HTTPError):
        api.add_new_employee(company["id"], "Evgeny1982", "")

def test_add_employee_without_email(api, company):
    """
    Негативный тест на добавление сотрудника без электронной почты.
    """
    with pytest.raises(requests.exceptions.HTTPError):
        api.add_new_employee(company["id"], "Evgeny1982", "Gusinets", email="")


def test_add_employee_without_company_id(api):
    """
    Негативный тест на добавление сотрудника без ID компании.
    """
    with pytest.raises(requests.exceptions.HTTPError):
        api.add_new_employee(None, "Evgeny1982", "Gusinets")
