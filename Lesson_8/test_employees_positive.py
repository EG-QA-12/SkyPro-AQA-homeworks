import pytest
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

def test_get_employees(api, new_company):
    company_id = new_company["id"]
    employees = api.get_employees_list(company_id)
    assert isinstance(employees, list)

def test_add_new_employee(api, new_company, cleanup_employee):
    company_id = new_company["id"]
    firstName = "Daria"
    lastName = "Abramovich"
    middleName = "Dmitrievna"
    email = "abramovichdash@mail.ru"
    url = "string"
    phone = "89670425734"
    birthdate = "1991-11-24"
    isActive = True

    # Create employee
    new_employee = api.create_employee(firstName, lastName, middleName, company_id, email, url, phone, birthdate, isActive)
    print("New employee created:", new_employee)
    emp_id = new_employee.get("id")
    if not emp_id:
        raise AssertionError("Failed to create employee, no ID returned")

    # Verify employee was created
    employee = api.get_employee(emp_id)
    print("Employee details:", employee)
    assert employee["firstName"] == firstName
    assert employee["lastName"] == lastName
    assert employee["middleName"] == middleName
    assert employee["companyId"] == company_id
    assert employee["email"] == email

def test_get_employee_by_id(api, new_company, cleanup_employee):
    company_id = new_company["id"]
    firstName = "Oleg"
    lastName = "Tinkoff"
    middleName = "Alexandrovich"
    email = "tinkoff777@yandex.ru"
    url = "string"
    phone = "89035145997"
    birthdate = "1971-06-04"
    isActive = True

    # Create employee
    new_employee = api.create_employee(firstName, lastName, middleName, company_id, email, url, phone, birthdate, isActive)
    print("Response from create_employee:", new_employee)
    emp_id = new_employee.get("id")
    if not emp_id:
        raise AssertionError("Failed to create employee, no ID returned")

    # Get employee by ID
    employee = api.get_employee(emp_id)
    print("Employee details:", employee)
    assert employee["id"] == emp_id
    assert employee["firstName"] == firstName
    assert employee["lastName"] == lastName
    assert employee["middleName"] == middleName
    assert employee["companyId"] == company_id
    assert employee["email"] == email

def test_patch_employee(api, new_company, cleanup_employee):
    company_id = new_company["id"]
    firstName = "Vladimir"
    lastName = "Arseniev"
    middleName = "Konstantinovich"
    email = "vlars@mail.ru"
    url = "string"
    phone = "89051112350"
    birthdate = "1992-08-17"
    isActive = True

    # Create employee
    new_employee = api.create_employee(firstName, lastName, middleName, company_id, email, url, phone, birthdate, isActive)
    print("New employee created:", new_employee)
    emp_id = new_employee.get("id")
    if not emp_id:
        raise AssertionError("Failed to create employee, no ID returned")

    # Patch employee
    new_lastName = "Popov"
    new_email = "popov@mail.ru"
    new_url = "_Updated_"
    new_phone = "Updated"
    new_isActive = False
    edited_employee = api.edit_employee(emp_id, new_lastName, new_email, new_url, new_phone, new_isActive)
    print("Edited employee:", edited_employee)

    # Verify changes were applied
    assert edited_employee.get("lastName") == new_lastName, f"Expected: {new_lastName}, Got: {edited_employee.get('lastName')}"
    assert edited_employee.get("email") == new_email, f"Expected: {new_email}, Got: {edited_employee.get('email')}"
    assert edited_employee.get("url") == new_url, f"Expected: {new_url}, Got: {edited_employee.get('url')}"
    assert edited_employee.get("phone") == new_phone, f"Expected: {new_phone}, Got: {edited_employee.get('phone')}"
    assert edited_employee.get("isActive") == new_isActive, f"Expected: {new_isActive}, Got: {edited_employee.get('isActive')}"
