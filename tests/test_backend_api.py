from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_health_endpoint_returns_ok():
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_strategy_preview_endpoint_returns_bounded_window():
    client = TestClient(create_app())

    response = client.post("/api/v1/strategy/preview", json={})

    assert response.status_code == 200
    payload = response.json()
    assert payload["recommended_window_start"] >= 1
    assert payload["recommended_window_start"] <= payload["recommended_window_end"]
    assert payload["risk_label"] in {"low", "medium", "high"}
    assert "Recommended review window" in payload["explanation"]
