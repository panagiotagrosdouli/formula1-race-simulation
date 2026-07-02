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


def test_monte_carlo_endpoint_returns_summary():
    client = TestClient(create_app())

    response = client.post(
        "/api/v1/simulations/monte-carlo",
        json={"runs": 3, "current_lap": 42, "circuit": {"lap_count": 44}},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["runs"] == 3
    assert "winner_counts" in payload
    assert "average_finish_position" in payload
    assert payload["assumptions"]
