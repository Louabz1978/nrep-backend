import pytest
from fastapi.testclient import TestClient
from pydantic import EmailStr


@pytest.fixture
def token_by_email(client: TestClient):
    def _get_token(email: EmailStr):
        """Login and return the access token"""
        login_response = client.post(
            "/auth/login",
            data={"username": email, "password": "1234"}
        )
        data = login_response.json()
        token = data.get("access_token")
        assert token, f"Login failed: {data}"
        return token
    return _get_token

@pytest.mark.parametrize("email, property_id, expected_status", [
    ("test@admin.com", 1, 200),
    ("test@broker.com", 2, 200),
    ("test@realtor.com", 1, 200),
    ("test@norole.com", 1, 403),
    ("test@admin.com", 99999, 404),
    ("test@admin.com","3b",422)
])
def test_get_property_by_id_roles(client: TestClient, token_by_email, email, property_id, expected_status):
    token = token_by_email(email)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/property/{property_id}", headers=headers)

    assert response.status_code == expected_status

    data = response.json()

    if expected_status == 200:
        assert "property" in data
        assert data["property"]["property_id"] == property_id
        assert "price" in data["property"]
        assert isinstance(data["property"]["status"], str)

    elif expected_status == 403:
        assert data["detail"] == "Not authorized"

    elif expected_status == 404:
        assert data["detail"] == "Property not found"
