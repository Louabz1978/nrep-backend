import pytest
from fastapi.testclient import TestClient
from app.models.user_model import User
from app.routers.auth.auth_router import create_access_token

@pytest.fixture
def setup_users(override_db):
    db = override_db
    users = db.query(User).all()
    return users

def create_user_token(user: User) -> str:
    role_dict = user.roles.__dict__
    roles = [
        key for key, value in role_dict.items()
        if key not in ['id', 'user_id', '_sa_instance_state'] and isinstance(value, bool) and value
    ]

    token_data = {
        "sub": str(user.user_id),
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "created_at": user.created_at.date().isoformat(),
        "roles": roles
    }

    return create_access_token(token_data)

def test_all_users_access_their_own_data(client: TestClient, setup_users):
    for user in setup_users:
        token = create_user_token(user)
        client.headers.update({"Authorization": f"Bearer {token}"})
        response = client.get("/users/me")
        assert response.status_code == 200
