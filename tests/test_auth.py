import pytest
from app.models.user_model import User
from sqlalchemy.orm import joinedload
from jose import jwt
import os

def test_login_and_all_roles(client, override_db):
    db = override_db
    users = db.query(User).options(
        joinedload(User.roles),
        joinedload(User.creator)
    ).all()

    for user in users:
        roles = [
            key for key, value in user.roles.__dict__.items()
            if key in ["admin", "broker", "realtor", "seller", "buyer", "tenant"]
            and value
        ]
        role = roles[0]
        email = user.email
        password = "1234"

        response = client.post(
            "/auth/login",
            data={
                "username": email,
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        assert response.status_code == 200, f"Login failed for role: {role}"
        data = response.json()

        assert "access_token" in data, f"No token returned for role: {role}"
        assert data["token_type"] == "bearer"

        token = data["access_token"]

        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        assert role in payload.get("roles", []), f"Role in token does not match for {role}"


def test_login_wrong_password(client, override_db):
    user = override_db.query(User).first()

    response = client.post(
        "/auth/login",
        data = {
            "username": user.email,
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_wrong_email(client, override_db):
    user = override_db.query(User).first()

    response = client.post(
        "/auth/login",
        data = {
            "username": "wrongemail@test.com",
            "password": "123456"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"