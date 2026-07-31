# Node-RED Flow

`digital_twin_flow.json` — imports as a single tab: "Digital Twin Pipeline"

## What it does

**Publisher side:**
- Reads real `lux` values from a BH1750 sensor over serial (COM14, 9600 baud)
- Computes `predicted_current = K * lux` (twin physics model)
- Simulates `measured_current`, `v_out`, and `temp` (until real hardware for those exists)
- Computes `error` and flags `status` as `OK`/`FAULT`
- Publishes the combined reading as JSON to MQTT topic `photodetector/team7/reading`

**Subscriber side:**
- Subscribes to the same MQTT topic
- Validates the payload (rejects malformed or incomplete messages)
- Writes the reading to InfluxDB (`digital_twin` bucket, `photodetector_reading` measurement)

## Data provenance

Each published reading includes a `data_source` field marking which values are real vs. simulated:
- `lux`: real (BH1750 sensor)
- `v_out`, `temp`, `measured_current`: simulated, pending additional hardware (BPW34 + TL071, DHT22)

## Import instructions

1. Open Node-RED (`localhost:1880`)
2. Hamburger menu → Import → paste/upload `digital_twin_flow.json`
3. Configure the MQTT broker node (test.mosquitto.org, port 1883) and InfluxDB node (org `team7`, bucket `digital_twin`, token required — see main README)
4. Deploy
