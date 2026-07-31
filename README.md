# digital-twin-photodetector

## Data Provenance

| Field | Source |
|---|---|
| `lux` | Real — BH1750 via STM32 |
| `v_out`, `temp`, `measured_current` | Simulated (no BPW34/TL071/DHT22 hardware yet) |
| `predicted_current`, `error`, `status` | Calculated from the values above |


## Repo Structure

| Folder / File | Contents |
|---|---|
| `blender/` | `mqtt_lux_sync_blender.py` — sync the 3D scene's light live from MQTT readings |
| `fault-service/` | Fault classifier microservice + its unit tests |
| `grafana/` | Dashboard JSON provisioning (4 panels: Real-time Current, Model Error gauge, Illuminance & Voltage Trend, System Status) |
| `influxdb/` | InfluxDB config / init |
| `nodered/` | Node-RED flow: serial parsing, twin model logic, MQTT publish, InfluxDB write validation |
| `notebooks/` | `Digital_Twin_AI_Behavioral_Model.ipynb` (fault classifier training + streaming demo), `Digital_Twin_Streaming_Aggregation.ipynb` (live MQTT capture + windowed aggregation) |
| `tests/` | Unit, integration, and system tests |
| `docker-compose.yml` | Brings up InfluxDB + Grafana |
| `SPRINT_LOG.md` | Sprint-by-sprint progress log |
| `VIDEO_LINK.md` | Link to the demo walkthrough video |

## Setup

### Prerequisites
- Docker + Docker Compose
- Node-RED (native install)
- Python 3.x with `paho-mqtt` (for the Blender sync script)
- Blender (for live 3D visualization)
- STM32 Nucleo F411RE + BH1750, mbed toolchain (for firmware)

### 1. Bring up the data stack
```bash
docker compose up -d
docker compose ps   # confirm InfluxDB + Grafana are running
```

### 2. Node-RED
Import the flow from `nodered/`, deploy. It reads from the STM32 over serial (COM14 @ 9600 baud), runs the twin model, and publishes to `photodetector/team7/reading` on `test.mosquitto.org`.

### 3. Blender live sync
```bash
python blender/mqtt_lux_sync_blender.py
```

### 4. Grafana
Open `localhost:3000` — dashboards are pre-provisioned from `grafana/`.

### 5. Fault classifier service
See `fault-service/` for setup — runs alongside the pipeline and reacts to streamed readings.

## Notebooks
Run these live against the pipeline, not just as static code:
- `notebooks/Digital_Twin_Streaming_Aggregation.ipynb` — captures live MQTT data, shows windowed aggregation vs. raw
- `notebooks/Digital_Twin_AI_Behavioral_Model.ipynb` — trained classifier, demonstrated against a streamed sequence with explicit actions

## Testing
```bash
pytest tests/
```
Covers unit tests (sensor parsing, twin logic, InfluxDB write validation), integration tests (fake MQTT message → InfluxDB, malformed payload rejection), and at least one full-pipeline system test. CI (`.github/workflows/`) runs this automatically on every push.

## Branching / Contributing
Strict workflow: `branch → commit → push → PR → review → merge`. No direct pushes to `main`.
```bash
git checkout main && git pull origin main
git checkout -b feature/<short-description>
# ...commit, push...
git push origin feature/<short-description>
# open PR on GitHub, assign a reviewer, get approval, merge
```

## Demo
See [`VIDEO_LINK.md`](VIDEO_LINK.md) for the full walkthrough — hardware, live Node-RED, Grafana + Blender reacting together, container persistence, and notebook outputs.

## Team — Group 7
- vviperinae — Docker/CI infrastructure, integration & e2e tests, PR reviews
- kuaav — Blender visualization, Grafana dashboards, InfluxDB export, twin model logic
- [Teammate B] — Fault classifier microservice
- [Teammate C] — Node-RED flow, InfluxDB integration, live fault demo
- Sobana — Documentation (README, sprint log)
