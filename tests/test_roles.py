import pytest
from fastapi.testclient import TestClient
from app.models.user_model import User
from sqlalchemy.orm import joinedload

@pytest.fixture
def setup_users(override_db):
    users = override_db.query(User).options(
        joinedload(User.roles),
        joinedload(User.creator)
    ).all()
    return users

@pytest.fixture
def admin_user(setup_users):
    for user in setup_users:
        if user.roles.admin:
            return user
    pytest.skip("No admin user found in setup_users")

@pytest.fixture
def non_admin_user(setup_users):
    for user in setup_users:
        if not user.roles.admin:
            return user
    pytest.skip("No non-admin user found in setup_users")

def login_user(client: TestClient, email: str, password: str = "1234"):
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200, "Login failed"
    token = response.json().get("access_token")
    assert token is not None
    return token

def test_update_role_as_admin(client: TestClient, setup_users, admin_user):
    token = login_user(client, admin_user.email)
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    target_user = next(user for user in setup_users if user.user_id != admin_user.user_id)
    
    payload = {
        "admin": False,
        "broker": True,
        "realtor": False,
        "seller": True,
        "buyer": False,
        "tenant": False
    }
    
    response = client.put(f"/roles/{target_user.user_id}", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["message"] == "Role updated successfully"
    assert json_data["user_id"] == target_user.user_id

def test_update_role_as_non_admin(client: TestClient, setup_users, non_admin_user):
    token = login_user(client, non_admin_user.email)
    client.headers.update({"Authorization": f"Bearer {token}"})

    target_user = setup_users[0]

    payload = {
        "admin": False,
        "broker": True,
        "realtor": False,
        "seller": True,
        "buyer": False,
        "tenant": False
    }
    
    response = client.put(f"/roles/{target_user.user_id}", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized"

def test_update_role_user_not_found(client: TestClient, admin_user):
    token = login_user(client, admin_user.email)
    client.headers.update({"Authorization": f"Bearer {token}"})

    payload = {
        "admin": False,
        "broker": True,
        "realtor": False,
        "seller": True,
        "buyer": False,
        "tenant": False
    }
    
    response = client.put("/roles/999999", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
