import requests

auth_url = "http://127.0.0.1:8000/auth/login"
user_url = "http://127.0.0.1:8000/users/2"

# Replace with your actual admin credentials
data = {
    "username": "demo@demo.com",
    "password": "1234"
}

# Get token
auth_response = requests.post(auth_url, data=data)
auth_response.raise_for_status()  # Raise error if failed

token = auth_response.json().get("access_token")
if not token:
    raise Exception("Failed to get access token")

headers = {
    "Authorization": f"Bearer {token}"
}

# Step 2: Use token to access protected endpoint
user_response = requests.get(user_url, headers=headers)
print(user_response.status_code)
print(user_response.json())
