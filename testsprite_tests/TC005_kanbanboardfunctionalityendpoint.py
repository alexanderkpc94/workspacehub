import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_kanbanboardfunctionalityendpoint():
    # We will test the Task Management endpoints related to Kanban board functionality.
    # Adjusted endpoint URLs based on discovered URLconf patterns.

    headers = {
        "Content-Type": "application/json"
    }

    # Step 1: Create a new task with initial status "To Do"
    task_payload = {
        "title": "Test Task for Kanban",
        "description": "Task for testing Kanban board functionality",
        "status": "To Do"
    }
    task_id = None

    try:
        # Create Task at adjusted endpoint
        response = requests.post(f"{BASE_URL}/tasks/create-task/", json=task_payload, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 201, f"Failed to create task: {response.status_code} {response.text}"
        task = response.json()
        assert "id" in task, "Created task response missing id"
        task_id = task["id"]
        assert task["status"] == "To Do"

        # Step 2: Verify task appears in Kanban board under "To Do"
        response = requests.get(f"{BASE_URL}/kanban/", timeout=TIMEOUT)
        assert response.status_code == 200, f"Failed to get Kanban board: {response.status_code} {response.text}"
        kanban = response.json()
        assert isinstance(kanban, dict), "Kanban board response is not a dictionary"
        assert "To Do" in kanban, "Kanban board missing 'To Do' column"
        todo_tasks = kanban.get("To Do", [])
        assert any(t.get("id") == task_id for t in todo_tasks), "Created task not found in 'To Do' column"

        # Step 3: Move task from "To Do" to "In Progress"
        update_payload = {
            "status": "In Progress"
        }
        response = requests.put(f"{BASE_URL}/tasks/{task_id}/update/", json=update_payload, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Failed to update task status: {response.status_code} {response.text}"
        updated_task = response.json()
        assert updated_task.get("status") == "In Progress", "Task status not updated to 'In Progress'"

        # Step 4: Verify task appears in Kanban board under "In Progress"
        response = requests.get(f"{BASE_URL}/kanban/", timeout=TIMEOUT)
        assert response.status_code == 200, f"Failed to get Kanban board after update: {response.status_code} {response.text}"
        kanban = response.json()
        assert "In Progress" in kanban, "Kanban board missing 'In Progress' column"
        inprogress_tasks = kanban.get("In Progress", [])
        assert any(t.get("id") == task_id for t in inprogress_tasks), "Updated task not found in 'In Progress' column"

        todo_tasks = kanban.get("To Do", [])
        assert not any(t.get("id") == task_id for t in todo_tasks), "Task still found in 'To Do' after moving"

        # Step 5: Move task to "Done"
        update_payload = {
            "status": "Done"
        }
        response = requests.put(f"{BASE_URL}/tasks/{task_id}/update/", json=update_payload, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Failed to update task status to Done: {response.status_code} {response.text}"
        done_task = response.json()
        assert done_task.get("status") == "Done", "Task status not updated to 'Done'"

        # Step 6: Verify task appears under "Done"
        response = requests.get(f"{BASE_URL}/kanban/", timeout=TIMEOUT)
        assert response.status_code == 200, f"Failed to get Kanban board after moving to Done: {response.status_code} {response.text}"
        kanban = response.json()
        assert "Done" in kanban, "Kanban board missing 'Done' column"
        done_tasks = kanban.get("Done", [])
        assert any(t.get("id") == task_id for t in done_tasks), "Task not found in 'Done' column"
        assert not any(t.get("id") == task_id for t in kanban.get("To Do", [])), "Task still found in 'To Do' after moving to Done"
        assert not any(t.get("id") == task_id for t in kanban.get("In Progress", [])), "Task still found in 'In Progress' after moving to Done"

    finally:
        if task_id is not None:
            # Cleanup - delete the created task
            try:
                response = requests.delete(f"{BASE_URL}/tasks/{task_id}/", timeout=TIMEOUT)
                assert response.status_code in (200, 204), f"Failed to delete task during cleanup: {response.status_code} {response.text}"
            except Exception as e:
                print(f"Cleanup failed: {e}")


test_kanbanboardfunctionalityendpoint()
