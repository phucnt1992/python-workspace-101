import os

import httpx
from domain.todo import Todo


class TodoApiError(Exception):
    pass


class TodoNotFoundError(TodoApiError):
    pass


class TodoApiClient:
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def list_todos(self) -> list[Todo]:
        response = self._request("GET", "/api/todos")
        payload = response.json()
        return [Todo.model_validate(item) for item in payload]

    def create_todo(self, title: str, description: str | None = None) -> Todo:
        response = self._request("POST", "/api/todos", json={"title": title, "description": description})
        return Todo.model_validate(response.json())

    def update_todo(self, todo_id: int, title: str | None = None, description: str | None = None) -> Todo:
        response = self._request(
            "PUT",
            f"/api/todos/{todo_id}",
            json={"title": title, "description": description},
        )
        return Todo.model_validate(response.json())

    def delete_todo(self, todo_id: int) -> None:
        self._request("DELETE", f"/api/todos/{todo_id}")

    def complete_todo(self, todo_id: int) -> Todo:
        response = self._request("POST", f"/api/todos/{todo_id}/complete")
        return Todo.model_validate(response.json())

    def reopen_todo(self, todo_id: int) -> Todo:
        response = self._request("POST", f"/api/todos/{todo_id}/reopen")
        return Todo.model_validate(response.json())

    def _request(self, method: str, path: str, **kwargs: object) -> httpx.Response:
        try:
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise TodoApiError(f"Could not reach Todo API: {exc}") from exc

        if response.status_code == 404:
            raise TodoNotFoundError(self._extract_error_message(response))
        if response.is_error:
            raise TodoApiError(self._extract_error_message(response))

        return response

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text or f"Todo API returned HTTP {response.status_code}."

        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail

        return response.text or f"Todo API returned HTTP {response.status_code}."


def get_api_client() -> TodoApiClient:
    return TodoApiClient(base_url=os.environ.get("APP_API_BASE_URL", "http://127.0.0.1:8000"))
