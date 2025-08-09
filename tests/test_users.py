import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from app.database import Base, get_db
from main import app
from app.models.user_model import User
from app.models.role_model import Role
from app.routers.auth.auth_router import create_access_token  # your token function

# Assuming you have a fixture for db_session and client from your conftest.py

def create_user(db: Session, first_name, last_name, email, password_hash, phone_number, created_by, roles_dict):
    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=password_hash,
        phone_number=phone_number,
        created_by=created_by
    )
    # Set roles boolean fields according to roles_dict
    role = Role(**roles_dict)
    user.roles = role
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

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

@pytest.fixture
def setup_users(db_session):
    # Create admin user
    admin = create_user(
        db_session,
        "Admin", "User", "admin@example.com", "hashed_admin_password",
        "1234567890", created_by=1,
        roles_dict={"admin": True, "broker": False, "realtor": False}
    )

    # Create broker user created by admin
    broker = create_user(
        db_session,
        "Broker", "User", "broker@example.com", "hashed_broker_password",
        "1234567891", created_by=admin.user_id,
        roles_dict={"admin": False, "broker": True, "realtor": False}
    )

    # Realtor created by broker
    realtor = create_user(
        db_session,
        "Realtor", "User", "realtor@example.com", "hashed_realtor_password",
        "1234567892", created_by=broker.user_id,
        roles_dict={"admin": False, "broker": False, "realtor": True}
    )

    # Other user created by realtor
    other_user = create_user(
        db_session,
        "Other", "User", "other@example.com", "hashed_other_password",
        "1234567893", created_by=realtor.user_id,
        roles_dict={"admin": False, "broker": False, "realtor": False}
    )

    return admin, broker, realtor, other_user


def test_admin_can_access_all_users(client: TestClient, db_session, setup_users):
    admin, broker, realtor, other_user = setup_users
    token = create_user_token(admin)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/users/")
    assert response.status_code == 200

def test_broker_access(client: TestClient, db_session, setup_users):
    admin, broker, realtor, other_user = setup_users
    token = create_user_token(broker)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/users/")
    assert response.status_code == 200

def test_realtor_access(client: TestClient, db_session, setup_users):
    admin, broker, realtor, other_user = setup_users
    token = create_user_token(realtor)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get("/users/")
    assert response.status_code == 200

def test_other_users_only_access_self(client: TestClient, db_session, setup_users):
    admin, broker, realtor, other_user = setup_users
    token = create_user_token(other_user)
    client.headers.update({"Authorization": f"Bearer {token}"})

    # Try to get all users (should not be allowed)
    response = client.get("/users/")
    assert response.status_code in [403, 401]

    # Can access own user by ID
    response = client.get(f"/users/{other_user.user_id}")
    assert response.status_code == 200

    # Cannot access another user by ID
    response = client.get(f"/users/{admin.user_id}")
    assert response.status_code in [403, 401, 404]

def test_access_denied_for_unauthorized_user(client: TestClient, setup_users):
    admin, broker, realtor, other_user = setup_users
    
    token = create_user_token(other_user)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.get(f"/users/{admin.user_id}")
    assert response.status_code == 403

    response_self = client.get(f"/users/{other_user.user_id}")
    assert response_self.status_code == 200

def test_get_user_id_not_exist_returns_404(client: TestClient, db_session, setup_users):
    admin, _, _, _ = setup_users
    token = create_user_token(admin)
    client.headers.update({"Authorization": f"Bearer {token}"})

    # Assuming 99999 user_id does not exist
    response = client.get("/users/99999")
    assert response.status_code == 404
