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
