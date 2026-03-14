import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}

def test_task_creation_endpoint():
    url = f"{BASE_URL}/tasks/"
    valid_task_payload = {
        "title": "Test Task",
        "description": "A task created during testing.",
        "status": "todo"  # Assuming status field and "todo" as a valid status
    }
    invalid_task_payloads = [
        {},  # Empty payload
        {"title": ""},  # Empty title
        {"title": "Valid Title", "status": "unknownstatus"},  # Invalid status
        {"description": "No title field"},  # Missing title field
        {"title": 123, "description": "Title as number"},  # Title wrong type
    ]

    # Test valid task creation
    try:
        response = requests.post(url, json=valid_task_payload, headers=HEADERS, timeout=TIMEOUT)
        assert response.status_code == 201, f"Expected status code 201, got {response.status_code}"
        response_json = response.json()
        assert "id" in response_json, "Response JSON missing 'id'"
        assert response_json["title"] == valid_task_payload["title"], "Title mismatch in response"
        assert response_json["description"] == valid_task_payload["description"], "Description mismatch in response"
        assert response_json["status"] == valid_task_payload["status"], "Status mismatch in response"
        task_id = response_json["id"]
    except requests.RequestException as e:
        assert False, f"Request failed during valid task creation: {e}"
    finally:
        # Cleanup: delete the created task if exists
        if 'task_id' in locals():
            try:
                delete_url = f"{url}{task_id}/"
                requests.delete(delete_url, timeout=TIMEOUT)
            except requests.RequestException:
                pass

    # Test invalid task creations
    for idx, payload in enumerate(invalid_task_payloads):
        try:
            response = requests.post(url, json=payload, headers=HEADERS, timeout=TIMEOUT)
            # Expecting client error (400 Bad Request)
            assert response.status_code == 400, f"Test case {idx+1}: Expected 400 status for invalid input, got {response.status_code}"
            response_json = response.json()
            assert "error" in response_json or "errors" in response_json or response_json, f"Test case {idx+1}: Expected error message in response"
        except requests.RequestException as e:
            assert False, f"Test case {idx+1}: Request failed during invalid task creation test: {e}"

test_task_creation_endpoint()