import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30
HEADERS = {"Content-Type": "application/json"}

def test_task_crud_operations():
    task_create_url = f"{BASE_URL}/tasks/"
    task_detail_url = lambda task_id: f"{BASE_URL}/tasks/{task_id}/"

    # Sample data for creating and updating a task
    task_data = {
        "title": "Test Task",
        "description": "This is a test task for CRUD operations.",
        "status": "todo"
    }
    updated_task_data = {
        "title": "Updated Test Task",
        "description": "This task has been updated.",
        "status": "in_progress"
    }

    task_id = None
    try:
        # Create Task (POST)
        create_resp = requests.post(task_create_url, json=task_data, headers=HEADERS, timeout=TIMEOUT)
        assert create_resp.status_code == 201, f"Expected 201 Created, got {create_resp.status_code}"
        create_json = create_resp.json()
        task_id = create_json.get("id")
        assert task_id is not None, "Task ID not returned on creation"
        assert create_json["title"] == task_data["title"]
        assert create_json["description"] == task_data["description"]
        assert create_json["status"] == task_data["status"]

        # Retrieve Task (GET)
        get_resp = requests.get(task_detail_url(task_id), headers=HEADERS, timeout=TIMEOUT)
        assert get_resp.status_code == 200, f"Expected 200 OK on GET, got {get_resp.status_code}"
        get_json = get_resp.json()
        assert get_json["id"] == task_id
        assert get_json["title"] == task_data["title"]
        assert get_json["description"] == task_data["description"]
        assert get_json["status"] == task_data["status"]

        # Update Task (PUT)
        update_resp = requests.put(task_detail_url(task_id), json=updated_task_data, headers=HEADERS, timeout=TIMEOUT)
        assert update_resp.status_code == 200, f"Expected 200 OK on PUT, got {update_resp.status_code}"
        update_json = update_resp.json()
        assert update_json["title"] == updated_task_data["title"]
        assert update_json["description"] == updated_task_data["description"]
        assert update_json["status"] == updated_task_data["status"]

        # Partial Update Task Status (PATCH)
        patch_data = {"status": "done"}
        patch_resp = requests.patch(task_detail_url(task_id), json=patch_data, headers=HEADERS, timeout=TIMEOUT)
        assert patch_resp.status_code == 200, f"Expected 200 OK on PATCH, got {patch_resp.status_code}"
        patch_json = patch_resp.json()
        assert patch_json["status"] == patch_data["status"]

        # Confirm status update via GET
        confirm_resp = requests.get(task_detail_url(task_id), headers=HEADERS, timeout=TIMEOUT)
        assert confirm_resp.status_code == 200
        confirm_json = confirm_resp.json()
        assert confirm_json["status"] == patch_data["status"]

    finally:
        if task_id is not None:
            # Delete Task (DELETE)
            del_resp = requests.delete(task_detail_url(task_id), headers=HEADERS, timeout=TIMEOUT)
            assert del_resp.status_code in (200, 204), f"Expected 200 OK or 204 No Content on DELETE, got {del_resp.status_code}"

            # Confirm deletion by GET (should return 404)
            get_after_del_resp = requests.get(task_detail_url(task_id), headers=HEADERS, timeout=TIMEOUT)
            assert get_after_del_resp.status_code == 404, f"Expected 404 Not Found after deletion, got {get_after_del_resp.status_code}"

test_task_crud_operations()