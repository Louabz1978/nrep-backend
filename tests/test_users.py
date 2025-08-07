import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.user_model import User
from app.models.role_model import Role
from passlib.hash import bcrypt

# --- Fixtures ---
@pytest.fixture
def create_user_with_role(override_db):
    def _create_user(email, password, role):
        user = User(
            first_name="Test",
            last_name="User",
            email=email,
            password_hash=bcrypt.hash(password),
            phone_number="+1234567890",
            created_by=1
        )
        override_db.add(user)
        override_db.commit()
        override_db.refresh(user)
        user_role = Role(user_id=user.user_id, **{role: True})
        override_db.add(user_role)
        override_db.commit()
        return user
    return _create_user

@pytest.fixture
def get_token(client, create_user_with_role):
    def _get_token(email, password, role):
        user = create_user_with_role(email, password, role)
        login_response = client.post(
            "/auth/login",
            data={"username": email, "password": password}
        )
        assert login_response.status_code == 200
        return login_response.json()["access_token"], user.user_id
    return _get_token

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
    response = client.get("/users/999999")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_user_by_id_with_auth(client, create_user_with_role):
    # Create and login user
    email = "admin@example.com"
    password = "1234"
    role = "admin"
    create_user_with_role(email, password, role)
    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
    # Use the token to access user data
    response = client.get(
        "/users/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 404]

def test_get_user_by_id_admin_access(client, create_user_with_role):
    # Create and login admin
    admin_email = "admin@example.com"
    admin_password = "1234"
    admin_role = "admin"
    create_user_with_role(admin_email, admin_password, admin_role)
    login_response = client.post(
        "/auth/login",
        data={"username": admin_email, "password": admin_password}
    )
    assert login_response.status_code == 200
    token = login_response.json().get("access_token")
    # Create a user using admin token
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@test.com",
        "password": "password123",
        "phone_number": "+1234567890",
        "role": ["buyer"]
    }
    create_response = client.post(
        "/users",
        json=user_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    created_user = create_response.json()["user"]
    user_id = created_user["user_id"]
    # Now try to get that user's data
    response = client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["email"] == "john@test.com"

def test_check_user_out():
    pass
