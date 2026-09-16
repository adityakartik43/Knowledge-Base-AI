from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_does_not_require_auth() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_protected_route_rejects_missing_api_key() -> None:
    response = client.post("/embed", json={"texts": ["hello"]})
    assert response.status_code == 401


def test_protected_route_rejects_invalid_api_key() -> None:
    response = client.post(
        "/embed",
        json={"texts": ["hello"]},
        headers={"X-Service-Api-Key": "wrong-key"},
    )
    assert response.status_code == 401
