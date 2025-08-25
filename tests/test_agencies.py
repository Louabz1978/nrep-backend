import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_agency_success():
    # login as admin
    login_response = client.post("/auth/login", data={"username": "admin@example.com", "password": "1234"})
    token = login_response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    # test agency with known ID
    response = client.get("/agencies/1")
    assert response.status_code == 200
    data = response.json()
    assert "agency_id" in data
    assert "name" in data
    assert "broker" in data
    assert "address" in data or data["address"] is None

def test_get_agency_not_found():
    # login as admin
    login_response = client.post("/auth/login", data={"username": "admin@example.com", "password": "1234"})
    token = login_response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    response = client.get("/agencies/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Agency not found"

def test_get_agency_forbidden():
    # login as non-admin
    login_response = client.post("/auth/login", data={"username": "broker@example.com", "password": "1234"})
    token = login_response.json().get("access_token")
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    response = client.get("/agencies/1")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized"
