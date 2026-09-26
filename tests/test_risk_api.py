def risk_payload(**overrides):
    payload = {
        "trip_id": 1,
        "vehicle_type": "truck",
        "temperature": 18,
        "precipitation": 22,
        "wind_speed": 65,
    }
    payload.update(overrides)
    return payload


def test_health_check(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_complete_crud(client):
    created = client.post("/risk-analysis", json=risk_payload())
    assert created.status_code == 201
    assert created.json()["score"] == 60
    assert created.json()["classification"] == "MODERATE"
    assert created.json()["warnings"] == ["Heavy precipitation", "Strong winds"]
    analysis_id = created.json()["id"]

    assert len(client.get("/risk-analysis").json()) == 1
    assert client.get(f"/risk-analysis/{analysis_id}").status_code == 200

    updated = client.put(
        f"/risk-analysis/{analysis_id}",
        json={"score": 72, "classification": "HIGH"},
    )
    assert updated.status_code == 200
    assert updated.json()["classification"] == "HIGH"

    assert client.delete(f"/risk-analysis/{analysis_id}").status_code == 204
    assert client.get(f"/risk-analysis/{analysis_id}").status_code == 404


def test_risk_boundaries(client):
    low = client.post(
        "/risk-analysis",
        json=risk_payload(temperature=20, precipitation=0, wind_speed=0),
    )
    high = client.post(
        "/risk-analysis",
        json=risk_payload(temperature=2, precipitation=11, wind_speed=51),
    )
    assert (low.json()["score"], low.json()["classification"]) == (0, "LOW")
    assert (high.json()["score"], high.json()["classification"]) == (80, "HIGH")

