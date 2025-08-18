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



def test_get_user_by_id_realtor_access(client):
   
    login_response = client.post(
        "/auth/login",
        data={"username": "test@broker.com", "password": "1234"}
    )
  
    token = login_response.json().get("access_token")
    # Now try to get that user's data
    response = client.get(
        f"/users/4",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 4
    assert data["email"] == "test@buyer.com"


def test_get_user_by_id_admin_access(client):
    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={"username": "test@admin.com", "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
   
    response = client.get(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1

def test_get_user_by_id_broker_access(client):
    # Login as broker
    login_response = client.post(
        "/auth/login",
        data={"username": "test@broker.com", "password": "1234"}
    )
 
    broker_token = login_response.json().get("access_token")

    # test that broker can access the user created by him
    realtor_response = client.get(
        f"/users/3",
        headers={"Authorization": f"Bearer {broker_token}"}
    )
    assert realtor_response.status_code == 200
    data = realtor_response.json()
    assert data["user_id"] == 3
    assert data["email"] == "test@realtor.com"

    # Now test that broker can access the user created by the realtor
    buyer_response = client.get(
        f"/users/4",
        headers={"Authorization": f"Bearer {broker_token}"}
    )
    assert buyer_response.status_code == 200
    data = buyer_response.json()
    assert data["user_id"] == 4
    assert data["email"] == "test@buyer.com"

def test_check_user_out(client):
    # Login as admin (assuming user_id 1 is admin)
    login_response = client.post(
        "/auth/login",
        data={"username": "test@admin.com", "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")

    # Get user with id 1
    response = client.get(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # Check all UserOut fields
    assert isinstance(data["user_id"], int)
    assert isinstance(data["first_name"], str)
    assert isinstance(data["last_name"], str)
    assert isinstance(data["email"], str)
    assert "@" in data["email"]
    assert isinstance(data["phone_number"], str)
    assert isinstance(data["roles"], list)
    for role in data["roles"]:
        assert role in ["admin", "buyer", "seller", "broker", "realtor", "tenant"]
    assert isinstance(data["created_by"], int)
    assert isinstance(data["created_at"], str)  # ISO datetime string
    # Address is optional and can be None or a dict
    if data["address"] is not None:
        address = data["address"]
        assert isinstance(address, dict)
        # Check some address fields
        assert "address_id" in address
        assert "city" in address
        assert "street" in address



# GET ALL USERS

def test_get_all_users_admin(client: TestClient, setup_users):
    # Admin can get all users
    login_response = client.post(
        "/auth/login",
        data={"username": "test@admin.com", "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) >= len(setup_users)


def test_get_all_users_broker(client: TestClient, setup_users):
    # Broker can get all users
    login_response = client.post(
        "/auth/login",
        data={"username": "test@broker.com", "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_all_users_realtor(client: TestClient, setup_users):
    # Realtor can get all users
    login_response = client.post(
        "/auth/login",
        data={"username": "test@realtor.com", "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_all_users_no_token(client: TestClient):
    # Request without token returns 401
    response = client.get("/users")
    assert response.status_code == 401



def test_get_all_users_no_token(client: TestClient):
    # Request without token returns 401
    response = client.get("/users")
    assert response.status_code == 401


# DELETE USER (Admin only)

def test_delete_user_admin(client: TestClient, setup_users):
    # Admin can delete another user
    admin = next((u for u in setup_users if u.email == "test@admin.com"), setup_users[0])
    user_to_delete = next((u for u in setup_users if u.email == "test@broker.com"), None)

    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={"username": admin.email, "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")

    client.headers.update({"Authorization": f"Bearer {token}"})
    response = client.delete(f"/users/{user_to_delete.user_id}")

    assert response.status_code == 204  # No Content


def test_delete_user_non_admin_forbidden(client: TestClient, setup_users):
    # Non-admin (broker) cannot delete a user
    broker = next((u for u in setup_users if u.email == "test@broker.com"), setup_users[0])
    user_to_delete = next((u for u in setup_users if u.email == "test@realtor.com"), None)

    # Login as broker
    login_response = client.post(
        "/auth/login",
        data={"username": broker.email, "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")

    client.headers.update({"Authorization": f"Bearer {token}"})
    response = client.delete(f"/users/{user_to_delete.user_id}")

    assert response.status_code == 403


def test_delete_user_no_token(client: TestClient, setup_users):
    # Request without token returns 401
    user_to_delete = next((u for u in setup_users if u.email == "test@realtor.com"), None)

    response = client.delete(f"/users/{user_to_delete.user_id}")

    assert response.status_code == 401


def test_delete_user_not_exist(client: TestClient, setup_users):
    # Deleting non-existent user returns 404
    admin = next((u for u in setup_users if u.email == "test@admin.com"), setup_users[0])

    # Login as admin
    login_response = client.post(
        "/auth/login",
        data={"username": admin.email, "password": "1234"}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")

    client.headers.update({"Authorization": f"Bearer {token}"})
    response = client.delete("/users/99999")

    assert response.status_code == 404
