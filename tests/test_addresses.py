import pytest
from fastapi.testclient import TestClient
from pydantic import EmailStr
from datetime import datetime, time, date
from app.routers.addresses.address_out import AddressOut 


# -------------------- Fixtures -------------------- 
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


# -------------------- Address Tests --------------------

# CREATE endpoint tests (success + validation)
#
def test_create_address_success(client: TestClient, token_by_email):
    token = token_by_email("test@broker.com")  # broker/realtor allowed too
    headers = {"Authorization": f"Bearer {token}"}

    form_data = {
        "floor": 5,
        "apt": 10,
        "area": "Inshaat",
        "city": "Homs",
        "county": "SomeCounty",
        "building_num": "7654321",
        "street": "Main Street"
    }

    resp = client.post("/address/me", data=form_data, headers=headers)
    assert resp.status_code == 201, f"expected 201, got {resp.status_code}: {resp.text}"
    data = resp.json()

    # basic shape checks
    assert "address_id" in data
    assert data["floor"] == form_data["floor"]
    assert data["apt"] == form_data["apt"]
    assert data["area"] == form_data["area"]
    assert data["city"] == form_data["city"]
    assert data["building_num"] == form_data["building_num"]
    assert "created_at" in data

    # cleanup
    admin_token = token_by_email("test@admin.com")
    del_headers = {"Authorization": f"Bearer {admin_token}"}
    del_resp = client.delete(f"/address/{data['address_id']}", headers=del_headers)
    assert del_resp.status_code == 204

@pytest.mark.parametrize(
    "payload, missing_or_bad_field",
    [
        ({"apt": 1, "area": "A", "city": "Homs", "county": "C", "building_num": "1234567", "street": "s"}, "floor"),
        ({"floor": 1, "area": "valid", "city": "Homs", "county": "C", "building_num": "123", "street": "s", "apt": 1}, "building_num"),
        ({"floor": -1, "apt": 1, "area": "valid", "city": "Homs", "county": "C", "building_num": "1234567", "street": "s"}, "floor"),
        ({"floor": 1, "apt": 0, "area": "valid", "city": "Homs", "county": "C", "building_num": "1234567", "street": "s"}, "apt"),
        # short area
        ({"floor": 1, "apt": 1, "area": "A", "city": "Homs", "county": "C", "building_num": "1234567", "street": "s"}, "area"),
    ]
)
def test_create_address_validation_errors(client: TestClient, token_by_email, payload, missing_or_bad_field):
    token = token_by_email("test@broker.com")
    headers = {"Authorization": f"Bearer {token}"}

    # send form - missing/invalid fields should produce 422
    resp = client.post("/address/me", data=payload, headers=headers)
    assert resp.status_code == 422, f"expected 422 for invalid {missing_or_bad_field}, got {resp.status_code}: {resp.text}"

def test_create_address_unauthorized(client: TestClient):
    form_data = {
        "floor": 1,
        "apt": 1,
        "area": "Area 1",
        "city": "Homs",
        "county": "Cty",
        "building_num": "1234567",
        "street": "Street 1"
    }
    resp = client.post("/address/me", data=form_data)
    # if auth is required, expect 401 (Not authenticated)
    assert resp.status_code in (401, 403), f"expected 401/403 for unauthenticated, got {resp.status_code}"


@pytest.mark.parametrize("email, address_id, expected_status", [
    ("test@admin.com", 1, 200),
    ("test@broker.com", 3, 200),
    ("test@norole.com", 1, 403),
    ("test@admin.com", 9999, 404),
])
def test_get_address_by_id_roles(client: TestClient, token_by_email, email, address_id, expected_status):
    token = token_by_email(email)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/address/{address_id}", headers=headers)

    assert response.status_code == expected_status
    data = response.json()

    if expected_status == 200:
        addr = AddressOut(**data)
        assert isinstance(addr.address_id, int)
        assert isinstance(addr.city, str)
        assert isinstance(addr.area, str)
        assert isinstance(addr.created_at, datetime)

    elif expected_status == 403:
        assert data["detail"] == "Not authorized"

    elif expected_status == 404:
        assert data["detail"] == "Address not found"


def test_my_address_out_schema(client: TestClient, token_by_email):
    token = token_by_email("test@broker.com")
    response = client.get("/address/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    addr = AddressOut(**response.json())
    assert isinstance(addr.address_id, int)
    assert isinstance(addr.city, str)
    assert isinstance(addr.created_at, datetime)


def test_address_list_pagination_and_schema(client: TestClient, token_by_email):
    token = token_by_email("test@admin.com")
    response = client.get("/address/all?page=1&per_page=3", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 3
    for addr_json in data["data"]:
        addr = AddressOut(**addr_json)
        assert isinstance(addr.address_id, int)


# -------------------- Unit Test for AddressOut --------------------
def test_addressout_validator_created_at_time_to_datetime():
    """يتأكد إنو validator بيحوّل time → datetime"""
    t = time(12, 30)
    addr = AddressOut(address_id=1, city="Homs", area="Inshaat", floor=1,county="Homs",apt=1,created_at=t)
    assert isinstance(addr.created_at, datetime), "wrong"
    assert addr.created_at.hour == 12 and addr.created_at.minute == 30 ,"incorrect"



# ---- Update ----
def test_update_address_success(client: TestClient, token_by_email):
    token = token_by_email("test@admin.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "city": "Damascus",
        "street": "Mazzeh",
        "floor": 5
    }

    response = client.put("/address/1", headers=headers, json=payload)

    assert response.status_code == 200, f"Update failed: {response.text}"
    data = response.json()
    print(data)
    assert data['address']["city"] == "Damascus"
    assert data['address']["street"] == "Mazzeh"
    assert data['address']["floor"] == 5
    


def test_update_address_not_found(client: TestClient, token_by_email):
    token = token_by_email("test@admin.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.put("/address/999999", headers=headers, json={"city": "Aleppo"})
    assert response.status_code == 404
    assert response.json()["detail"] == "address not found"


# ---- Delete ----
def test_delete_address_success(client: TestClient, token_by_email):
    token = token_by_email("test@admin.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/address/2", headers=headers)
    assert response.status_code == 204

    response_get = client.get("/address/2", headers=headers)
    assert response_get.status_code == 404
    assert response_get.json()["detail"] == "Address not found"



def test_delete_address_not_found(client: TestClient, token_by_email):
    token = token_by_email("test@admin.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/address/999999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Address not found"
