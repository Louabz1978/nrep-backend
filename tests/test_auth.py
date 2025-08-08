import pytest
from passlib.hash import bcrypt
from fastapi.testclient import TestClient

from main import app

from app.models.user_model import User
from app.models.role_model import Role

#creating user with each role
def create_user(db, fn:str, ln:str, email: str, password: str, roles, phone_number: str, created_by: int):
    exist = db.query(User).filter_by(email=email).first()
    if exist:
        print("you are wrong")
    hashed_password = bcrypt.hash(password)
    user = User(
        first_name = fn,
        last_name = ln,
        email = email,
        password_hash = hashed_password,
        phone_number = phone_number,
        created_by = created_by
    )
    role = Role(**roles)
    user.roles = role

    db.add(user)
    db.add(role)   
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def admin_user(override_db):
    return create_user(override_db, "admin", "admin", "admin@example.com", "1234", {"admin" : True}, "0957390823", 1)

@pytest.fixture
def broker_user(override_db):
    return create_user(override_db, "broker", "broker", "broker@example.com", "1234", {"admin" : True}, "0957390823", 1)

@pytest.fixture
def realtor_user(override_db):
    return create_user(override_db, "realtor", "realtor", "realtor@example.com", "1234", {"admin" : True}, "0957390823", 1)


@pytest.fixture
def seller_user(override_db):
    return create_user(override_db, "seller", "seller", "seller@example.com", "1234", {"admin" : True}, "0957390823", 1)

@pytest.fixture
def buyer_user(override_db):
    return create_user(override_db, "buyer", "buyer", "buyer@example.com", "1234", {"admin" : True}, "0957390823", 1)

@pytest.fixture
def tenant_user(override_db):
    return create_user(override_db, "tenant", "tanent", "tenant@example.com", "1234", {"admin" : True}, "0957390823", 1)

#returning access_token
@pytest.fixture
def admin_token(client, admin_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@example.com",
            "password": "1234"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def broker_token(client, broker_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "broker@example.com",
            "password": "1234"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def realtor_token(client, realtor_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "realtor@example.com",
            "password": "1234"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def buyer_token(client, buyer_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "buyer@example.com",
            "password": "1234"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def seller_token(client, seller_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "seller@example.com",
            "password": "1234"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def tenant_token(client, tenant_user):
    response = client.post(
        "/auth/login",
        data={
            "username": "tenant@example.com",
            "password": "1234"
        }
    )
    return response.json()["access_token"]

@pytest.mark.parametrize("email,password,fixture_name",[
    ("admin@example.com","1234","admin_user"),
    ("broker@example.com","1234","broker_user"),
    ("realtor@example.com","1234","realtor_user"),
    ("seller@example.com","1234","seller_user"),
    ("buyer@example.com","1234","buyer_user"),
    ("tenant@example.com","1234","tenant_user"),
])

def test_login(client, request, email, password, fixture_name):
    request.getfixturevalue(fixture_name)

    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
def test_login_wrong_password(client, admin_user):
    response = client.post(
        "/auth/login",
        data ={
            "username": "admin@example.com",
            "password" : "wrongpassword" 
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail" : "Incorrect username or password"}

def test_login_wrong_email(client, admin_user):
    response = client.post(
        "/auth/login",
        data ={
            "username": "admin1@example.com",
            "password" : "1234" 
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail" : "Incorrect username or password"}

def test_login_missing_password(client, admin_user):
    response = client.post(
        "/auth/login",
        data = {
            "username": "admin@example.com"
        }
    )
    assert response.status_code == 422 
    
def test_login_missing_email(client, admin_user):
    response = client.post(
        "/auth/login",
        data = {
            "password": "1234"
        }
    )
    assert response.status_code == 422 
