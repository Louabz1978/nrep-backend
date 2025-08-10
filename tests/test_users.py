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

def filter_users_by_role(users, role_name):
    return [u for u in users if getattr(u.roles, role_name, False)]

def test_update_user_as_admin(client: TestClient, setup_users):
    acting_users = filter_users_by_role(setup_users, "admin")
    assert acting_users, "No admin users found for testing"
    
    for acting_user in acting_users:
        token = login_user(client, acting_user.email, "1234")
        client.headers.update({"Authorization": f"Bearer {token}"})

        for target_user in setup_users:
            update_payload = {
                "first_name": "UpdatedName",
                "last_name": target_user.last_name,
                "email": target_user.email,
                "phone_number": target_user.phone_number,
                "password": None
            }
            response = client.put(f"/users/{target_user.user_id}", json=update_payload)
            assert response.status_code == 200

            body = response.json()
            assert body["message"] == "User updated successfully"
            assert body["user"]["first_name"] == "UpdatedName"

def test_update_user_as_broker(client: TestClient, setup_users):
    acting_users = filter_users_by_role(setup_users, "broker")
    assert acting_users, "No broker users found for testing"
    
    for acting_user in acting_users:
        token = login_user(client, acting_user.email, "1234")
        client.headers.update({"Authorization": f"Bearer {token}"})

        for target_user in setup_users:
            update_payload = {
                "first_name": "UpdatedName",
                "last_name": target_user.last_name,
                "email": target_user.email,
                "phone_number": target_user.phone_number,
                "password": None
            }
            response = client.put(f"/users/{target_user.user_id}", json=update_payload)
            
            if (
                target_user.created_by == acting_user.user_id or 
                (target_user.creator and target_user.creator.created_by == acting_user.user_id)
            ):
                expected_status = 200
            else:
                expected_status = 403
                
            assert response.status_code == expected_status
            
            if response.status_code == 200:
                body = response.json()
                assert body["message"] == "User updated successfully"
                assert body["user"]["first_name"] == "UpdatedName"

def test_update_user_as_realtor(client: TestClient, setup_users):
    acting_users = filter_users_by_role(setup_users, "realtor")
    assert acting_users, "No realtor users found for testing"
    
    for acting_user in acting_users:
        token = login_user(client, acting_user.email, "1234")
        client.headers.update({"Authorization": f"Bearer {token}"})

        for target_user in setup_users:
            update_payload = {
                "first_name": "UpdatedName",
                "last_name": target_user.last_name,
                "email": target_user.email,
                "phone_number": target_user.phone_number,
                "password": None
            }
            response = client.put(f"/users/{target_user.user_id}", json=update_payload)
            
            if target_user.created_by == acting_user.user_id:
                expected_status = 200
            else:
                expected_status = 403
                
            assert response.status_code == expected_status
            
            if response.status_code == 200:
                body = response.json()
                assert body["message"] == "User updated successfully"
                assert body["user"]["first_name"] == "UpdatedName"

def test_update_user_as_buyer(client: TestClient, setup_users):
    acting_users = filter_users_by_role(setup_users, "buyer")
    assert acting_users, "No buyer users found for testing"
    
    for acting_user in acting_users:
        token = login_user(client, acting_user.email, "1234")
        client.headers.update({"Authorization": f"Bearer {token}"})

        for target_user in setup_users:
            update_payload = {
                "first_name": "UpdatedName",
                "last_name": target_user.last_name,
                "email": target_user.email,
                "phone_number": target_user.phone_number,
                "password": None
            }
            response = client.put(f"/users/{target_user.user_id}", json=update_payload)
            
            expected_status = 403
            assert response.status_code == expected_status

def test_update_nonexistent_user(client: TestClient, setup_users):
    acting_user = setup_users[0]
    token = login_user(client, acting_user.email, "1234")
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
