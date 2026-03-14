import requests

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = f"{BASE_URL}/api/users/register/"
HEADERS = {"Content-Type": "application/json"}
TIMEOUT = 30

def test_user_registration_endpoint():
    # Test successful user registration with valid data
    valid_payload = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "StrongPassword!123"
    }

    response = requests.post(REGISTER_ENDPOINT, json=valid_payload, headers=HEADERS, timeout=TIMEOUT)
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"
    json_resp = response.json()
    assert "id" in json_resp
    assert json_resp.get("username") == valid_payload["username"]
    assert json_resp.get("email") == valid_payload["email"]

    # Test error handling for missing username
    invalid_payload = {
        "email": "nousername@example.com",
        "password": "Password123!"
    }
    response = requests.post(REGISTER_ENDPOINT, json=invalid_payload, headers=HEADERS, timeout=TIMEOUT)
    assert response.status_code == 400
    json_resp = response.json()
    assert "username" in json_resp

    # Test error handling for invalid email format
    invalid_payload = {
        "username": "userwithbademail",
        "email": "not-an-email",
        "password": "Password123!"
    }
    response = requests.post(REGISTER_ENDPOINT, json=invalid_payload, headers=HEADERS, timeout=TIMEOUT)
    assert response.status_code == 400
    json_resp = response.json()
    assert "email" in json_resp

    # Test error handling for weak password (assuming some password validation)
    invalid_payload = {
        "username": "weakpassworduser",
        "email": "weakpassword@example.com",
        "password": "123"
    }
    response = requests.post(REGISTER_ENDPOINT, json=invalid_payload, headers=HEADERS, timeout=TIMEOUT)
    assert response.status_code == 400
    json_resp = response.json()
    assert "password" in json_resp

test_user_registration_endpoint()