from fastapi.testclient import TestClient


def test_create_and_get_todo(client: TestClient) -> None:
    created = client.post("/api/todos", json={"title": "Buy milk", "description": "2 bottles"})

    assert created.status_code == 201
    payload = created.json()
    assert payload["title"] == "Buy milk"
    assert payload["description"] == "2 bottles"
    assert payload["completed"] is False
    todo_id = payload["id"]

    fetched = client.get(f"/api/todos/{todo_id}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == todo_id


def test_list_todos_supports_pagination(client: TestClient) -> None:
    for title in ["A", "B", "C"]:
        assert client.post("/api/todos", json={"title": title}).status_code == 201

    page1 = client.get("/api/todos?page=1&page_size=2")
    assert page1.status_code == 200
    body1 = page1.json()
    assert body1["total"] == 3
    assert body1["page"] == 1
    assert body1["page_size"] == 2
    assert len(body1["items"]) == 2

    page2 = client.get("/api/todos?page=2&page_size=2")
    assert page2.status_code == 200
    body2 = page2.json()
    assert body2["total"] == 3
    assert body2["page"] == 2
    assert body2["page_size"] == 2
    assert len(body2["items"]) == 1


def test_update_complete_reopen_and_delete_todo(client: TestClient) -> None:
    created = client.post("/api/todos", json={"title": "Initial"})
    todo_id = created.json()["id"]

    updated = client.patch(f"/api/todos/{todo_id}", json={"title": "Updated", "description": "Done"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated"
    assert updated.json()["description"] == "Done"

    completed = client.post(f"/api/todos/{todo_id}/complete")
    assert completed.status_code == 200
    assert completed.json()["completed"] is True

    reopened = client.post(f"/api/todos/{todo_id}/reopen")
    assert reopened.status_code == 200
    assert reopened.json()["completed"] is False

    deleted = client.delete(f"/api/todos/{todo_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/todos/{todo_id}").status_code == 404


def test_returns_404_for_missing_todo(client: TestClient) -> None:
    assert client.get("/api/todos/999").status_code == 404
    assert client.patch("/api/todos/999", json={"title": "x"}).status_code == 404
    assert client.delete("/api/todos/999").status_code == 404
    assert client.post("/api/todos/999/complete").status_code == 404
    assert client.post("/api/todos/999/reopen").status_code == 404
