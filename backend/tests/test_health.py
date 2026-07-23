from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "wealthos-api"
    assert payload["version"] == "0.1.0"


def test_organizations_module_is_registered(client: TestClient) -> None:
    response = client.get("/organizations/health")
    assert response.status_code == 200
    assert response.json() == {"module": "organizations", "status": "ready"}
