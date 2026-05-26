from fastapi.testclient import TestClient


def test_health_endpoints(client: TestClient) -> None:
    liveness = client.get("/api/_healthz/liveness")
    assert liveness.status_code == 200
    assert liveness.json() == {"status": "ok"}

    readiness = client.get("/api/_healthz/readiness")
    assert readiness.status_code == 200
    assert readiness.json() == {"status": "ok"}


def test_openapi_documentation_is_exposed(client: TestClient) -> None:
    docs = client.get("/docs")
    assert docs.status_code == 200

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    schema = openapi.json()
    assert schema["info"]["title"] == "Todo API"
    assert "/api/todos" in schema["paths"]
