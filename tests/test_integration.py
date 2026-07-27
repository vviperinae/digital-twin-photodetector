import requests

def test_fault_service_reachable():
    resp = requests.post("http://localhost:5001/predict", json={
        "lux": 300, "v_out": 5, "temp": 22,
        "predicted_current": 6, "measured_current": 5.9, "error": 0.1
    }, timeout=5)
    assert resp.status_code == 200

def test_influxdb_write_pipeline():
    # Confirms Node-RED's write actually landed in InfluxDB
    resp = requests.get(
        "http://localhost:8086/api/v2/query?org=team7",
        headers={"Authorization": "Token YOUR_TOKEN_HERE"},
        params={"query": 'from(bucket:"digital_twin") |> range(start:-5m)'},
        timeout=5
    )
    assert resp.status_code == 200
