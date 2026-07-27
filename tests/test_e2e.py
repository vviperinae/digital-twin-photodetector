import requests
import time

def test_pipeline_end_to_end():
    """Confirms the full chain: sensor sim -> MQTT -> InfluxDB -> queryable"""
    time.sleep(2)  # let a cycle publish
    resp = requests.get(
        "http://localhost:8086/api/v2/query?org=team7",
        headers={"Authorization": "Token YOUR_TOKEN_HERE"},
        params={"query": 'from(bucket:"digital_twin") |> range(start:-5m) |> filter(fn:(r)=>r._measurement=="photodetector_reading")'},
        timeout=5
    )
    assert resp.status_code == 200
    assert "photodetector_reading" in resp.text
