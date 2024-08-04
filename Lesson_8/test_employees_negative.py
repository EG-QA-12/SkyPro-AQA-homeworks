import pytest
import requests
from EmployeesApi import EmployeesApi

@pytest.fixture(scope="module")
def api():
    return EmployeesApi()

@pytest.fixture
def new_company(api):
    company = api.create_company("Test Company")
    yield company
    api.delete_company(company["id"])

@pytest.fixture
def cleanup_employee(api, new_company):
    yield
    company_id = new_company["id"]
    employees = api.get_employees_list(company_id)
    for emp in employees:
        try:
            api.delete_employee(emp['id'])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Employee {emp['id']} not found for deletion")
            else:
                raise

def test_create_employee_with_invalid_email(api, new_company, cleanup_employee):
    company_id = new_company["id"]
    firstName = "Invalid"
    lastName = "Email"
    middleName = "Test"
    invalid_email = "invalid-email"
    url = "string"
    phone = "89670425734"
    birthdate = "1991-11-24"
    isActive = True

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        api.create_employee(firstName, lastName, middleName, company_id, invalid_email, url, phone, birthdate, isActive)
    assert excinfo.value.response.status_code == 400

def test_create_employee_with_missing_required_fields(api, new_company, cleanup_employee):
    company_id = new_company["id"]
    firstName = "Missing"
    lastName = "Fields"
    middleName = "Test"
    email = "missing@fields.com"
    url = "string"
    phone = "89670425734"
    birthdate = "1991-11-24"
    isActive = True

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        api.create_employee("", lastName, middleName, company_id, email, url, phone, birthdate, isActive)
    assert excinfo.value.response.status_code == 400

def test_get_non_existent_employee(api, new_company):
    non_existent_id = 999999

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        api.get_employee(non_existent_id)
    assert excinfo.value.response.status_code == 404

def test_delete_non_existent_employee(api, new_company):
    non_existent_id = 999999

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        api.delete_employee(non_existent_id)
    assert excinfo.value.response.status_code == 404

def test_edit_non_existent_employee(api, new_company):
    non_existent_id = 999999
    new_lastName = "Updated"
    new_email = "updated@mail.com"
    new_url = "Updated"
    new_phone = "Updated"
    new_isActive = False

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        api.edit_employee(non_existent_id, new_lastName, new_email, new_url, new_phone, new_isActive)
    assert excinfo.value.response.status_code == 404
