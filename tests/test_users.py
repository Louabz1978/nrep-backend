import pytest
from fastapi.testclient import TestClient

from sqlalchemy.orm import joinedload

from main import app
from app.models.user_model import User
from app.models.role_model import Role
from passlib.hash import bcrypt
import random

@pytest.fixture
def get_users_by_roles(override_db):
    def _get_users_by_roles(role_fields: list[str]):
        users_by_role = {}

        for role_field in role_fields:
            user = (
                override_db.query(User)
                .join(Role)
                .options(
                    joinedload(User.roles),
                    joinedload(User.creator)
                )
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
                    "creator": {
                        "created_by": user.creator.created_by
                    } if user.creator else None,
                    "roles": user.roles
                }
        
        return users_by_role

    return _get_users_by_roles

def test_get_user_details(client: TestClient, get_users_by_roles):
    users_by_role = get_users_by_roles(['admin', 'broker', 'realtor', 'buyer', 'seller', 'tenant'])

    for role, user in users_by_role.items():
        if user is None:
            continue

        response = client.post("/auth/login", data={"username": user["email"], "password": "1234"})
        token = response.json().get("access_token")

        client.headers.update({"Authorization": f"Bearer {token}"})
        response = client.get("/users/me")
        assert response.status_code == 200

        data = response.json()
        assert data["user_id"] == user["user_id"]
        assert data["email"] == user["email"]
        assert data["first_name"] == user["first_name"]
        assert data["last_name"] == user["last_name"]

def test_update_user_as_admin(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user, "No admin users found for testing"

    response = client.post("/auth/login", data={"username": admin_user["email"], "password": "1234"})
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    users = get_users_by_roles(['admin', 'broker', 'realtor', 'buyer', 'seller', 'tenant'])

    for target_user in users.values():
        update_payload = {
            "first_name": "UpdatedName",
            "last_name": target_user["last_name"],
            "email": target_user["email"],
            "phone_number": target_user["phone_number"],
            "password": None
        }
        response = client.put(f"/users/{target_user['user_id']}", json=update_payload)
        assert response.status_code == 200

        body = response.json()
        assert body["message"] == "User updated successfully"
        assert body["user"]["first_name"] == "UpdatedName"


def test_update_user_as_broker(client: TestClient, get_users_by_roles):
    broker_user_dict = get_users_by_roles(['broker'])
    broker_user = broker_user_dict.get('broker')
    assert broker_user, "No broker users found for testing"
    
    response = client.post("/auth/login", data={"username": broker_user["email"], "password": "1234"})
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    users = get_users_by_roles(['admin', 'broker', 'realtor', 'buyer', 'seller', 'tenant'])

    for target_user in users.values():
        update_payload = {
            "first_name": "UpdatedName",
            "last_name": target_user["last_name"],
            "email": target_user["email"],
            "phone_number": target_user["phone_number"],
            "password": None
        }
        response = client.put(f"/users/{target_user['user_id']}", json=update_payload)
        
        can_update = (
            target_user['created_by'] == broker_user['user_id'] or
            (target_user['creator'] and target_user['creator']['created_by'] == broker_user['user_id'])
        )
        expected_status = 200 if can_update else 403
        
        assert response.status_code == expected_status

        if response.status_code == 200:
            body = response.json()
            assert body["message"] == "User updated successfully"
            assert body["user"]["first_name"] == "UpdatedName"


def test_update_user_as_realtor(client: TestClient, get_users_by_roles):
    realtor_user_dict = get_users_by_roles(['realtor'])
    realtor_user = realtor_user_dict.get('realtor')
    assert realtor_user, "No realtor users found for testing"
    
    response = client.post("/auth/login", data={"username": realtor_user["email"], "password": "1234"})
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    users = get_users_by_roles(['admin', 'broker', 'realtor', 'buyer', 'seller', 'tenant'])

    for target_user in users.values():
        update_payload = {
            "first_name": "UpdatedName",
            "last_name": target_user["last_name"],
            "email": target_user["email"],
            "phone_number": target_user["phone_number"],
            "password": None
        }
        response = client.put(f"/users/{target_user['user_id']}", json=update_payload)
        
        if target_user['created_by'] == realtor_user['user_id']:
            expected_status = 200
        else:
            expected_status = 403
        
        assert response.status_code == expected_status

        if response.status_code == 200:
            body = response.json()
            assert body["message"] == "User updated successfully"
            assert body["user"]["first_name"] == "UpdatedName"


def test_update_user_as_buyer(client: TestClient, get_users_by_roles):
    buyer_user_dict = get_users_by_roles(['buyer'])
    buyer_user = buyer_user_dict.get('buyer')
    assert buyer_user, "No buyer users found for testing"
    
    response = client.post("/auth/login", data={"username": buyer_user["email"], "password": "1234"})
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    users = get_users_by_roles(['admin', 'broker', 'realtor', 'buyer', 'seller', 'tenant'])

    for target_user in users.values():
        update_payload = {
            "first_name": "UpdatedName",
            "last_name": target_user["last_name"],
            "email": target_user["email"],
            "phone_number": target_user["phone_number"],
            "password": None
        }
        response = client.put(f"/users/{target_user['user_id']}", json=update_payload)
        
        assert response.status_code == 403
    
    
def test_update_nonexistent_user(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')

    response = client.post("/auth/login", data={"username": admin_user["email"], "password": "1234"})
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
        
    non_existent_user_id = 9999999

    update_payload = {
        "first_name": "ShouldNotExist",
        "last_name": "User",
        "email": "nonexistent@example.com",
        "phone_number": "0000000000",
        "password": None
    }

    response = client.put(f"/users/{non_existent_user_id}", json=update_payload)

    if response.status_code != 404:
        print("Response status:", response.status_code)
        print("Response content:", response.content)

    assert response.status_code == 404



# --- Tests for GET /users/{id} ---

def test_get_user_by_id_unauthorized(client):
    response = client.get("/users/999")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_user_by_id_invalid_format(client):
    response = client.get("/users/invalid")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_user_by_id_not_found(client):
    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={"username": "test@admin.com", "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
    response = client.get("/users/999999" ,  headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"



def test_get_all_users_admin(client: TestClient):
    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={"username": "test@admin.com", "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) >= 1


def test_get_all_users_broker(client: TestClient):
    # Login as broker
    login_response = client.post(
        "/auth/login",
        data={"username": "test@broker.com", "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_all_users_realtor(client: TestClient):
    # Login as realtor
    login_response = client.post(
        "/auth/login",
        data={"username": "test@realtor.com", "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")

    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_all_users_non_privileged_roles(client, get_users_by_roles):
    users = get_users_by_roles(['buyer', 'seller', 'tenant'])

    for role, user in users.items():
        login_response = client.post(
            "/auth/login",
            data={"username": user["email"], "password": "1234"}
        )
        token = login_response.json().get("access_token")

        response = client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403


def test_get_all_users_no_token(client: TestClient):
    # Request without token returns 401
    response = client.get("/users")
    assert response.status_code == 401

#delete_user

def test_delete_user_by_id_admin_access(client, get_users_by_roles):
    admin_user = get_users_by_roles(['admin'])['admin']
    
    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = login_response.json().get("access_token")

    # Delete a buyer for example
    buyer_user = get_users_by_roles(['buyer'])['buyer']
    response = client.delete(
        f"/users/{buyer_user['user_id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 204)


def test_delete_user_by_id_non_admin_access(client, get_users_by_roles):
    users = get_users_by_roles(['broker', 'realtor', 'buyer', 'seller', 'tenant'])

    for role, user in users.items():
        # Login as this role
        login_response = client.post(
            "/auth/login",
            data={"username": user["email"], "password": "1234"}
        )
        token = login_response.json().get("access_token")

        # Attempt to delete another user 
        target_admin = get_users_by_roles(['admin'])['admin']
        response = client.delete(
            f"/users/{target_admin['user_id']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403

def test_delete_user_by_id_without_token(client):
    response = client.delete("/users/4")  
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"