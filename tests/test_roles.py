import pytest
from fastapi.testclient import TestClient
from app.models.user_model import User
from app.models.role_model import Role
from sqlalchemy.orm import joinedload

@pytest.fixture
def get_users_by_roles(override_db):
    def _get_users_by_roles(role_fields: list[str]):
        users_by_role = {}

        for role_field in role_fields:
            user = (
                override_db.query(User)
                .join(Role)
                .options(
                    joinedload(User.roles),
                    joinedload(User.creator)
                )
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
                    "creator": {
                        "created_by": user.creator.created_by
                    } if user.creator else None,
                    "roles": user.roles
                }
        
        return users_by_role

    return _get_users_by_roles

def test_update_role_as_admin(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user, "No admin users found for testing"
    
    response = client.post("/auth/login", data={"username": admin_user['email'], "password": "1234"})
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    target_users = get_users_by_roles(['broker', 'realtor', 'buyer', 'seller', 'tenant'])
    
    for target_user in target_users.values():
        payload = {
            "admin": False,
            "broker": True,
            "realtor": False,
            "seller": True,
            "buyer": False,
            "tenant": False
        }
        
        response = client.put(f"/roles/{target_user['user_id']}", json=payload)
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["message"] == "Role updated successfully"
        assert json_data["user_id"] == target_user['user_id']
            


def test_update_role_as_non_admin(client: TestClient, get_users_by_roles):
    non_admin_users = get_users_by_roles(['broker', 'realtor', 'buyer', 'seller', 'tenant'])
    
    for non_admin_user in non_admin_users.values():
        response = client.post("/auth/login", data={"username": non_admin_user['email'], "password": "1234"})
        token = response.json().get("access_token")
        client.headers.update({"Authorization": f"Bearer {token}"})
        for target_user in non_admin_users.values():
            payload = {
                "admin": False,
                "broker": True,
                "realtor": False,
                "seller": True,
                "buyer": False,
                "tenant": False
            }
            
            response = client.put(f"/roles/{target_user['user_id']}", json=payload)
            assert response.status_code == 403
            assert response.json()["detail"] == "Not authorized"


def test_update_role_user_not_found(client: TestClient, get_users_by_roles):
    admin_user_dict = get_users_by_roles(['admin'])
    admin_user = admin_user_dict.get('admin')
    assert admin_user, "No admin users found for testing"
    
    response = client.post("/auth/login", data={"username": admin_user['email'], "password": "1234"})
    token = response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})

    payload = {
        "admin": False,
        "broker": True,
        "realtor": False,
        "seller": True,
        "buyer": False,
        "tenant": False
    }
    
    response = client.put("/roles/999999", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
