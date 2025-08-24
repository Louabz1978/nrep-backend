import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import joinedload
from app.models.user_model import User
from app.models.role_model import Role

# Fixture to get users by roles
@pytest.fixture
def get_users_by_roles(override_db):
    def _get_users_by_roles(role_fields: list[str]):
        users_by_role = {}
        for role_field in role_fields:
            user = (
                override_db.query(User)
                .join(Role)
                .options(joinedload(User.roles), joinedload(User.creator))
                .filter(getattr(Role, role_field) == True)
                .first()
            )
            if user:
                users_by_role[role_field] = {
                    "user_id": user.user_id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": getattr(user, "phone_number", None),
                    "created_by": getattr(user, "created_by", None),
                    "creator": {"created_by": user.creator.created_by} if user.creator else None,
                    "roles": user.roles,
                }
        return users_by_role
    return _get_users_by_roles

#-----Tests for delete ------

def test_delete_existing_agency_as_admin(client :TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.delete(f"/agencies/1")
    assert response.status_code == 204

def test_delete_existing_agency_as_non_admin(client: TestClient, get_users_by_roles):
    broker_user_dict = get_users_by_roles(['broker'])
    broker_user = broker_user_dict.get('broker')
    assert broker_user

    response = client.post(
        "/auth/login",
        data={"username": broker_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.delete("/agencies/1")
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized"



def test_delete_non_existing_agency_as_admin(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user

    response = client.post(
        "/auth/login",
        data={"username": admin_user["email"], "password": "1234"}
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.delete("/agencies/999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Agency not found"