import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.user_model import User
from app.models.role_model import Role
from passlib.hash import bcrypt
import random

@pytest.fixture
def setup_users(override_db):
    db = override_db
    return db.query(User).all()

def login_user(client: TestClient, email: str, password: str):
    response = client.post("/auth/login", data={
        "username": email,
        "password": password
    })
    assert response.status_code == 200, f"Login failed for {email}"
    token = response.json().get("access_token")
    assert token is not None
    return token

def test_all_users_access_their_own_data(client: TestClient, setup_users):
    for user in setup_users:
        token = login_user(client, user.email, "1234")
        client.headers.update({"Authorization": f"Bearer {token}"})
        response = client.get("/users/me")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == user.user_id
        assert data["email"] == user.email
        assert data["first_name"] == user.first_name
        assert data["last_name"] == user.last_name



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
