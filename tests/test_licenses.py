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

def test_create_license_as_admin(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post("/auth/login", data={"username": admin_user["email"], "password": "1234"})
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    payload = {
        "lic_num": 99999,
        "lic_status": "active",
        "lic_type": "test_type",
        "agency_id": 1,
        "user_id": admin_user["user_id"]
    }

    response = client.post("/licenses", json=payload)
    assert response.status_code == 201, response.text

    license_data = response.json()
    assert license_data["lic_num"] == 99999
    assert license_data["lic_status"] == "active"
    assert license_data["lic_type"] == "test_type"
    assert license_data["agency_id"] == 1
    assert license_data["user_id"] == admin_user["user_id"]
    
def test_create_license_as_non_admin(client: TestClient, get_users_by_roles):
    broker_user_dict = get_users_by_roles(['broker'])
    broker_user = broker_user_dict.get('broker')
    assert broker_user

    response = client.post("/auth/login", data={"username": broker_user["email"], "password": "1234"})
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    payload = {
        "lic_num": 99999,
        "lic_status": "active",
        "lic_type": "test_type",
        "agency_id": 1,
        "user_id": broker_user["user_id"]
    }

    response = client.post("/licenses", json=payload)
    assert response.status_code == 403, response.text

def test_update_license_as_admin(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    create_resp = client.post("/licenses", json={
        "lic_num": 88888,
        "lic_status": "active",
        "lic_type": "initial_type",
        "agency_id": 1,
        "user_id": admin_user["user_id"]
    })
    license_id = create_resp.json()["license_id"]

    update_payload = {
        "lic_num": "12345",
        "lic_status": "updated_status",
        "lic_type": "updated_type",
        "agency_id": str(1),
        "user_id": str(admin_user["user_id"])
    }

    update_resp = client.put(
        f"/licenses/{license_id}",
        data=update_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert update_resp.status_code == 200, update_resp.text

    license_data = update_resp.json().get("license")
    assert license_data, update_resp.json()

    assert license_data["lic_num"] == 12345
    assert license_data["lic_status"] == "updated_status"
    assert license_data["lic_type"] == "updated_type"
    assert license_data["agency_id"] == 1

def test_update_not_existed_license_as_admin(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    update_payload = {
        "lic_num": "12345",
        "lic_status": "updated_status",
        "lic_type": "updated_type",
        "agency_id": str(1),
        "user_id": str(admin_user["user_id"])
    }

    update_resp = client.put(
        f"/licenses/1",
        data=update_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert update_resp.status_code == 404, update_resp.text


def test_update_license_as_non_admin(client: TestClient, get_users_by_roles):
    broker_user_dict = get_users_by_roles(['broker'])
    broker_user = broker_user_dict.get('broker')
    assert broker_user

    response = client.post(
        "/auth/login",
        data={"username": broker_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    update_payload = {
        "lic_num": "12345",
        "lic_status": "updated_status",
        "lic_type": "updated_type",
        "agency_id": str(1),
        "user_id": str(broker_user["user_id"])
    }

    update_resp = client.put(
        f"/licenses/1",
        data=update_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert update_resp.status_code == 403, update_resp.text

