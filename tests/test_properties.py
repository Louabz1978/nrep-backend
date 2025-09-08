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
    ("test@broker.com", 1, 200),
    ("test@broker.com", 2, 200),
    ("test@realtor.com", 1, 200),
    ("test@realtor.com", 2, 200),
    ("test@norole.com", 1, 403),
    ("test@admin.com", 99999, 404),
    ("test@admin.com","3B",405)
])
def test_get_property_by_id_roles(client: TestClient, token_by_email, email, property_id, expected_status):
    token = token_by_email(email)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/property/{property_id}", headers=headers)

    assert response.status_code == expected_status , f"Ecpected {expected_status} found {response.status_code}"

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


## MY properties
def test_my_properties(client: TestClient, token_by_email):
    token = token_by_email("test@broker.com")  
    response = client.get("/property/my-properties", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    
    assert "pagination" in data , "No page detected"
    assert "data" in data , "The JSON was not formatted to include data"
    assert all(p["created_by_user"]["user_id"] for p in data["data"])


def test_my_properties_unauthorized(client: TestClient):
    response = client.get("/property/my-properties")
    assert response.status_code == 401 , "Expected 401"


def test_my_properties_pagination(client: TestClient, token_by_email):
    token = token_by_email("test@admin.com")
    response = client.get("/property/my-properties?page=1&per_page=2", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200 , f"{response.text}"
    data = response.json()
    assert data["pagination"]["per_page"] == 2
    assert len(data["data"]) <= 2

def test_my_properties_sorting(client: TestClient, token_by_email):
    token = token_by_email("test@admin.com")
    response = client.get("/property/my-properties?sort_by=price&sort_order=asc", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200 , f"expected 200 but found {response.text}"
    prices = [p["price"] for p in response.json()["data"]]
    assert prices == sorted(prices)


@pytest.mark.parametrize(
    "query,check",
    [
        ("?city=Homs", lambda prop: "Homs" in prop["address"]["city"]),
        ("?area=Inshaat", lambda prop: "Inshaat" in prop["address"]["area"]),
        ("?min_price=5000", lambda prop: prop["price"] >= 5000),
        ("?max_price=200000", lambda prop: prop["price"] <= 200000),
        ("?mls_num=123", lambda prop: str(123) in str(prop["mls_num"])),
        ("?status_filter=available", lambda prop: prop["status"] == "available"),
    
    ],
)
def test_my_properties_filters(client: TestClient, token_by_email, query, check):
 
    token=token_by_email("test@admin.com")
    response = client.get(f"/my-properties{query}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, f"Query {query} failed with {response.text}"

    data = response.json()
    for prop in data["data"]:
        assert check(prop), f"Filter {query} did not match property {prop}"


def test_my_properties_sorting(client: TestClient, token_by_email):
    token=token_by_email("test@admin.com")
    response = client.get(
        "/my-properties?sort_by=price&sort_order=asc",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]

    prices = [prop["price"] for prop in data]
    assert prices == sorted(prices), "Properties not sorted by price ASC"

    # جرب نزولاً
    response = client.get(
        "/my-properties?sort_by=price&sort_order=desc",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()["data"]
    prices = [prop["price"] for prop in data]
    assert prices == sorted(prices, reverse=True), "Properties not sorted by price DESC"



def test_my_properties_complex_filter(client: TestClient, token_by_email):
    """تست يجمع أكتر من فلتر مع بعض"""
    query = "?city=Homs&min_price=10000&max_price=200000"
    
    token=token_by_email("test@admin.com")
    response = client.get(f"/my-properties{query}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200, f"Failed complex filter with {response.text}"
    data = response.json()["data"]

    for prop in data:
        assert "Homs" in prop["address"]["city"], f"City filter failed: {prop}"
        assert prop["price"] >= 10000, f"Min price filter failed: {prop}"
        assert prop["price"] <= 200000, f"Max price filter failed: {prop}"


def test_my_properties_pagination(client: TestClient, token_by_email):
    """تست مفصّل للـ Pagination"""
    per_page = 2
    token=token_by_email("test@admin.com")
    # الصفحة الأولى
    response = client.get(f"/my-properties?page=1&per_page={per_page}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    pagination = data["pagination"]
    properties = data["data"]

    assert pagination["page"] == 1
    assert pagination["per_page"] == per_page
    assert pagination["total"] >= len(properties)
    assert len(properties) <= per_page
    assert pagination["has_next"] is (pagination["total_pages"] > 1)
    assert pagination["has_prev"] is False  # أول صفحة ما إلها previous

    first_page_ids = [prop["property_id"] for prop in properties]

    # الصفحة الثانية (إذا في صفحات تانية)
    if pagination["total_pages"] > 1:
        response2 = client.get(f"/my-properties?page=2&per_page={per_page}", headers={"Authorization": f"Bearer {token}"})
        assert response2.status_code == 200
        data2 = response2.json()
        pagination2 = data2["pagination"]
        properties2 = data2["data"]

        assert pagination2["page"] == 2
        assert pagination2["has_prev"] is True
        assert pagination2["has_next"] is (pagination2["page"] < pagination2["total_pages"])

        second_page_ids = [prop["property_id"] for prop in properties2]
        # تأكد ما في تداخل بين الصفحة 1 و 2
        assert not set(first_page_ids).intersection(second_page_ids), "Pagination overlap!"
