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
        roles_dict={"admin": True, "broker": False, "realtor": False, "buyer": False, "seller": False, "tenant": False}
    )

    # Create broker user created by admin
    broker = create_user(
        db_session,
        "Broker", "User", "broker@example.com", "hashed_broker_password",
        "1234567891", created_by=admin.user_id,
        roles_dict={"admin": False, "broker": True, "realtor": False, "buyer": False, "seller": False, "tenant": False}
    )

    # Realtor created by broker
    realtor = create_user(
        db_session,
        "Realtor", "User", "realtor@example.com", "hashed_realtor_password",
        "1234567892", created_by=broker.user_id,
        roles_dict={"admin": False, "broker": False, "realtor": True, "buyer": False, "seller": False, "tenant": False}
    )

    # buyer user created by realtor
    buyer = create_user(
        db_session,
        "Buyer", "User", "buyer@example.com", "hashed_buyer_password",
        "1234567893", created_by=realtor.user_id,
        roles_dict={"admin": False, "broker": False, "realtor": False, "buyer": True, "seller": False, "tenant": False}
    )
    
    # seller user created by realtor
    seller = create_user(
        db_session,
        "Seller", "User", "seller@example.com", "hashed_seller_password",
        "1234567894", created_by=realtor.user_id,
        roles_dict={"admin": False, "broker": False, "realtor": False, "buyer": False, "seller": True, "tenant": False}
    )
    
    #tenant user created by realtor
    tenant = create_user(
        db_session,
        "Tenant", "User", "tenant@example.com", "hashed_tenant_password",
        "1234567895", created_by=realtor.user_id,
        roles_dict={"admin": False, "broker": False, "realtor": False, "buyer": False, "seller": False, "tenant": True}
    )

    return admin, broker, realtor, buyer, seller, tenant


def test_get_user(client: TestClient, db_session, setup_users):
    admin, broker, realtor, buyer, seller, tenant = setup_users
    users = [admin, broker, realtor, buyer, seller, tenant]
    for user in users:
        token = create_user_token(user)
        client.headers.update({"Authorization": f"Bearer {token}"})
        response = client.get("/users/me")
        assert response.status_code == 200

