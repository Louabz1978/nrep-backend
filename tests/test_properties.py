# tests/test_properties_seed_based.py
import pytest
from fastapi.testclient import TestClient
from app.routers.properties.properties_type_enum import PropertyTypes
from app.routers.properties.properties_status_enum import PropertyStatus

# -----------------------------
# Fixtures for tokens per role
# -----------------------------
@pytest.fixture
def admin_token(client: TestClient):
    resp = client.post("/auth/login", data={"email": "test@admin.com", "password": "123456"})
    return resp.json()["access_token"]

@pytest.fixture
def broker_token(client: TestClient):
    resp = client.post("/auth/login", data={"email": "test@broker.com", "password": "123456"})
    return resp.json()["access_token"]

@pytest.fixture
def realtor_token(client: TestClient):
    resp = client.post("/auth/login", data={"email": "test@realtor.com", "password": "123456"})
    return resp.json()["access_token"]

# -----------------------------
# Authorized client fixture
# -----------------------------
@pytest.fixture
def admin_client(client: TestClient, admin_token):
    client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return client

@pytest.fixture
def broker_client(client: TestClient, broker_token):
    client.headers.update({"Authorization": f"Bearer {broker_token}"})
    return client

@pytest.fixture
def realtor_client(client: TestClient, realtor_token):
    client.headers.update({"Authorization": f"Bearer {realtor_token}"})
    return client

# -----------------------------
# Test get all properties
# -----------------------------
def test_get_all_properties(admin_client):
    response = admin_client.get("/property")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    # Seed data has at least 2 properties
    assert len(data["data"]) >= 2

# -----------------------------
# Test get my properties (admin created)
# -----------------------------
def test_get_my_properties(admin_client):
    response = admin_client.get("/property/my-properties")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    # Admin created properties should exist
    assert len(data["data"]) >= 1

# -----------------------------
# Test get property by ID
# -----------------------------
def test_get_property_by_id(admin_client):
    # Use first property from seed
    response_all = admin_client.get("/property")
    prop_id = response_all.json()["data"][0]["property_id"]

    response = admin_client.get(f"/property/{prop_id}")
    assert response.status_code == 200
    res_json = response.json()
    assert "property" in res_json
    assert res_json["property"]["property_id"] == prop_id

# -----------------------------
# Test update property
# -----------------------------
def test_update_property(admin_client):
    response_all = admin_client.get("/property")
    prop_id = response_all.json()["data"][0]["property_id"]

    update_payload = {
        "property_data": {"description": "Updated Description from Test"},
        "address_data": {"city": "Updated City"},
        "additional_data": {}
    }

    response = admin_client.put(
        f"/property/{prop_id}",
        data={
            "property_data": update_payload["property_data"],
            "address_data": update_payload["address_data"],
            "additional_data": update_payload["additional_data"]
        }
    )
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["message"] == "Property updated successfully"
    assert res_json["property details"]["description"] == "Updated Description from Test"

# -----------------------------
# Test delete property
# -----------------------------
def test_delete_property(admin_client):
    # Use second property from seed
    response_all = admin_client.get("/property")
    if len(response_all.json()["data"]) < 2:
        pytest.skip("Not enough seed properties to test delete")
    prop_id = response_all.json()["data"][1]["property_id"]

    response = admin_client.delete(f"/property/{prop_id}")
    assert response.status_code == 204

# -----------------------------
# Test property status options
# -----------------------------
def test_property_status_options(admin_client):
    response = admin_client.get("/property/status-options")
    assert response.status_code == 200
    assert all(s in [status.value for status in PropertyStatus] for s in response.json())

# -----------------------------
# Test property type options
# -----------------------------
def test_property_type_options(admin_client):
    response = admin_client.get("/property/types_option")
    assert response.status_code == 200
    assert all(t in [t.value for t in PropertyTypes] for t in response.json())
