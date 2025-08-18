import pytest
from fastapi.testclient import TestClient
from app.models.user_model import User

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

# GET ALL USERS
def test_get_all_users_admin(client: TestClient, setup_users):
    #Admin can get all users
    admin = next((u for u in setup_users if u.email == "test@admin.com"), setup_users[0])
    token = login_user(client, admin.email, "1234")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) >= len(setup_users)


def test_get_all_users_broker(client: TestClient, setup_users):
    # Broker can get all users
    broker = next((u for u in setup_users if u.email == "test@broker.com"), setup_users[0])
    token = login_user(client, broker.email, "1234")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_all_users_realtor(client: TestClient, setup_users):
    # Realtor can get all users
    realtor = next((u for u in setup_users if u.email == "test@realtor.com"), setup_users[0])
    token = login_user(client, realtor.email, "1234")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


def test_get_all_users_no_token(client: TestClient):
    # Request without token returns 401
    response = client.get("/users")
    assert response.status_code == 401


# DELETE USER (Admin only)
def test_delete_user_admin(client: TestClient, setup_users):
    # Admin can delete another user
    admin = next((u for u in setup_users if u.email == "test@admin.com"), setup_users[0])
    user_to_delete = next((u for u in setup_users if u.email == "test@broker.com"), None)

    token = login_user(client, admin.email, "1234")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.delete(f"/users/{user_to_delete.user_id}")
    assert response.status_code == 204  # No Content


def test_delete_user_non_admin_forbidden(client: TestClient, setup_users):
    # Non-admin (broker) cannot delete a user
    broker = next((u for u in setup_users if u.email == "test@broker.com"), setup_users[0])
    user_to_delete = next((u for u in setup_users if u.email == "test@realtor.com"), None)

    token = login_user(client, broker.email, "1234")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.delete(f"/users/{user_to_delete.user_id}")
    assert response.status_code == 403


def test_delete_user_no_token(client: TestClient, setup_users):
    # Request without token returns 401
    user_to_delete = next((u for u in setup_users if u.email == "test@realtor.com"), None)

    response = client.delete(f"/users/{user_to_delete.user_id}")
    assert response.status_code == 401


def test_delete_user_not_exist(client: TestClient, setup_users):
    #Deleting non-existent user returns 404
    admin = next((u for u in setup_users if u.email == "test@admin.com"), setup_users[0])
    token = login_user(client, admin.email, "1234")
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.delete("/users/99999")
    assert response.status_code == 404
