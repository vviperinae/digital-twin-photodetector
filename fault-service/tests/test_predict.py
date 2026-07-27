import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_predict_ok_case(client):
    resp = client.post("/predict", json={
        "lux": 500, "v_out": 10, "temp": 25,
        "predicted_current": 10, "measured_current": 9.8, "error": 0.2
    })
    assert resp.status_code == 200
    assert resp.get_json()["predicted_status"] in ["OK", "FAULT"]

def test_predict_fault_case(client):
    resp = client.post("/predict", json={
        "lux": 500, "v_out": 10, "temp": 25,
        "predicted_current": 10, "measured_current": 2, "error": 8
    })
    assert resp.get_json()["predicted_status"] == "FAULT"
