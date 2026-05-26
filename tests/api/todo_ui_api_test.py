from fastapi.testclient import TestClient


def test_todo_ui_page_is_rendered(client: TestClient) -> None:
    response = client.get("/ui/")

    assert response.status_code == 200
    assert "Todo Kanban Board" in response.text
    assert "To Do" in response.text
    assert "Done" in response.text
    assert 'hx-post="/ui/create"' in response.text
    assert 'id="theme-toggle"' in response.text


def test_todo_ui_actions_update_partial_list(client: TestClient) -> None:
    created = client.post("/ui/create", data={"title": "Buy milk", "description": "2 bottles"})
    assert created.status_code == 200
    assert "Buy milk" in created.text
    assert "2 bottles" in created.text

    completed = client.post("/ui/1/complete")
    assert completed.status_code == 200
    assert "Done" in completed.text

    reopened = client.post("/ui/1/reopen")
    assert reopened.status_code == 200
    assert "To Do" in reopened.text

    updated = client.post("/ui/1/update", data={"title": "Buy oat milk", "description": "Unsweetened"})
    assert updated.status_code == 200
    assert "Buy oat milk" in updated.text
    assert "Unsweetened" in updated.text

    deleted = client.post("/ui/1/delete")
    assert deleted.status_code == 200
    assert "No cards in To Do." in deleted.text


def test_todo_ui_health_partial_returns_status(client: TestClient) -> None:
    response = client.get("/ui/health")

    assert response.status_code == 200
    assert "Liveness" in response.text
    assert "Readiness" in response.text
