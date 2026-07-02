from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_monte_carlo_endpoint_returns_summary():
    client = TestClient(create_app())

    response = client.post("/api/v1/simulations/monte-carlo", json={"runs": 3})

    assert response.status_code == 200
    payload = response.json()
    assert payload["runs"] == 3
    assert "LEC" in payload["winner_counts"]
    assert "LEC" in payload["average_finish_position"]
    assert payload["assumptions"]
