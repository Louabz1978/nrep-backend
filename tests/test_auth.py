# from fastapi.testclient import TestClient

# from main import app

# client = TestClient(app)

# def test_login(client):
#     response = client.post(
#         "/auth/login",
#         data={
#             "username": "test@admin.com",
#             "password": "1234"
#         }
#     )
#     print("STATUS:", response.status_code)
#     print("RESPONSE JSON:", response.json())
#     print("RESPONSE TEXT:", response.text)
#     assert response.status_code == 200

