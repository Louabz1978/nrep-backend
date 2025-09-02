import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_agency_success():
    # login as admin
    login_response = client.post("/auth/login", data={"username": "admin@example.com", "password": "1234"})
    token = login_response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # test agency with known ID
    response = client.get("/agencies/1")
    assert response.status_code == 200
    data = response.json()
    assert "agency_id" in data
    assert "name" in data
    assert "broker" in data
    assert "address" in data or data["address"] is None

def test_get_agency_not_found():
    # login as admin
    login_response = client.post("/auth/login", data={"username": "admin@example.com", "password": "1234"})
    token = login_response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    response = client.get("/agencies/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Agency not found"

def test_get_agency_forbidden():
    # login as non-admin
    login_response = client.post("/auth/login", data={"username": "broker@example.com", "password": "1234"})
    token = login_response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    response = client.get("/agencies/1")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import joinedload
from app.models.user_model import User
from app.models.role_model import Role

# Fixture to get users by roles
@pytest.fixture
def get_users_by_roles(override_db):
    def _get_users_by_roles(role_fields: list[str]):
        users_by_role = {}
        for role_field in role_fields:
            user = (
                override_db.query(User)
                .join(Role)
                .options(joinedload(User.roles), joinedload(User.creator))
                .filter(getattr(Role, role_field) == True)
                .first()
            )
            if user:
                users_by_role[role_field] = {
                    "user_id": user.user_id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": getattr(user, "phone_number", None),
                    "created_by": getattr(user, "created_by", None),
                    "creator": {"created_by": user.creator.created_by} if user.creator else None,
                    "roles": user.roles,
                }
        return users_by_role
    return _get_users_by_roles

#-----Tests for delete ------

def test_delete_existing_agency_as_admin(client :TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.delete(f"/agencies/1")
    assert response.status_code == 204

def test_delete_existing_agency_as_non_admin(client: TestClient, get_users_by_roles):
    broker_user_dict = get_users_by_roles(['broker'])
    broker_user = broker_user_dict.get('broker')
    assert broker_user

    response = client.post(
        "/auth/login",
        data={"username": broker_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.delete("/agencies/1")
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized"



def test_delete_non_existing_agency_as_admin(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.delete("/agencies/999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Agency not found"

#get all agencies
def test_get_all_agencies_as_admin(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/agencies?page=1&per_page=10&sort_by=agency_id&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 4
    assert data["pagination"]["total"] == 4
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 10
    assert data["pagination"]["total_pages"] == 1
    assert data["pagination"]["has_next"] is False
    assert data["pagination"]["has_prev"] is False
    assert data["data"][0]["agency_id"] == 1
    assert data["data"][0]["name"] == "test"
    assert data["data"][1]["agency_id"] == 2
    assert data["data"][1]["name"] == "Agency A"
    assert data["data"][2]["agency_id"] == 3
    assert data["data"][2]["name"] == "Agency B"
    assert data["data"][3]["agency_id"] == 4
    assert data["data"][3]["name"] == "Agency C"

def test_get_all_agencies_as_non_admin(client: TestClient, get_users_by_roles):
    broker_user_dict = get_users_by_roles(['broker'])
    broker_user = broker_user_dict.get('broker')
    assert broker_user

    response = client.post(
        "/auth/login",
        data={"username": broker_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/agencies?page=1&per_page=10&sort_by=agency_id&sort_order=asc")
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized"

def test_get_all_agencies_filter_by_name(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/agencies?name=test&page=1&per_page=10&sort_by=agency_id&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["name"] == "test"

def test_get_all_agencies_filter_by_city(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/agencies?city=Amsterdam&page=1&per_page=10&sort_by=agency_id&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["address"]["city"] == "Amsterdam"

def test_get_all_agencies_pagination(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    # Assuming more agencies are added in seed_data.sql later
    response = client.get("/agencies?page=1&per_page=1&sort_by=agency_id&sort_order=asc")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["pagination"]["total"] == 4
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 1
    assert data["pagination"]["total_pages"] == 4
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_prev"] is False
    assert data["data"][0]["agency_id"]== 1