# Digital Twin Data Pipeline, Setup Guide (Node-RED + InfluxDB + Grafana + Blender)

This guide sets up the full pipeline: **BH1750 sensor (via STM32) → MQTT → InfluxDB → Grafana**, plus a 3D visualization layer in Blender. InfluxDB and Grafana run in Docker; Node-RED runs as a native install.

**Note on visualization tooling:** this project uses **Blender** for 3D digital twin visualization instead of NVIDIA Omniverse, chosen for its lower hardware requirements, free/open-source licensing, and Python scripting support (via `bpy`), which made it straightforward to sync live sensor data into the 3D scene.

## 1. Prerequisites

- **Docker Desktop** installed (for InfluxDB + Grafana)
- **Node-RED** installed natively (not run inside Docker)
- **Blender** installed
- **STM32 Nucleo F411RE** with BH1750 sensor wired up, mbed toolchain for firmware
- If you're on **Windows**: use **WSL2** as your terminal for the Docker commands, and in Docker Desktop go to Settings → Resources → WSL Integration and enable it for your distro (e.g. Ubuntu)

## 2. Get the data stack running

1. Create a folder for the project stack:

        mkdir -p ~/digital-twin-stack
        cd ~/digital-twin-stack

2. Copy `docker-compose.yml` (from this repo) into this folder.
3. Bring up InfluxDB and Grafana:

        docker compose up -d

4. Confirm both services are running:

        docker compose ps

   You should see `influxdb2` and `grafana` listed as **Up**. (Node-RED is not part of this compose file, it's started separately in Section 3.)

### What's running and where

| Service | URL | Purpose |
|---|---|---|
| Node-RED (native) | http://localhost:1880 | Reads sensor data over serial, runs digital twin logic, publishes/subscribes MQTT |
| InfluxDB (Docker) | http://localhost:8086 | Stores time-series sensor + twin data |
| Grafana (Docker) | http://localhost:3000 | Visualizes the data on dashboards |

**Important:** InfluxDB and Grafana are each in their own Docker container. Inside Grafana, `localhost` refers to the Grafana container itself, not InfluxDB. To reach InfluxDB from Grafana, always use `http://influxdb:8086`, since `influxdb` is the container's service name and Docker resolves it automatically as both are on the same network (`dt-net`). Node-RED, running natively on your host machine (not in Docker), reaches InfluxDB via `http://localhost:8086` instead, since from the host's perspective, InfluxDB's port is published to `localhost`.

## 3. Set up Node-RED (native install)

### 3.1 Install Node-RED and the InfluxDB palette node

If Node-RED isn't installed yet:

    npm install -g --unsafe-perm node-red

Then start it:

    node-red

Node-RED doesn't include InfluxDB or serial-port support by default.

1. Open http://localhost:1880
2. Hamburger menu (top right) → Manage palette → Install tab
3. Search `node-red-contrib-influxdb` → Install
4. Search `node-red-node-serialport` → Install

### 3.2 Import the flow

1. Hamburger menu → Import
2. Upload or paste `nodered/digital_twin_flow.json` (from this repo)
3. Click Import, this creates a "Digital Twin Pipeline" tab with everything wired up:
   - **Serial in:** reads real `lux` readings from the BH1750 sensor via the STM32 Nucleo F411RE, over serial
   - **Publisher side:** twin logic function node computes `predicted_current = K * lux`, simulates `measured_current`, `v_out`, `temp` until further hardware exists, computes `error`, flags `status` as `OK`/`FAULT`, publishes as JSON over MQTT
   - **Subscriber side:** subscribes to the same MQTT topic, validates the payload, writes it into InfluxDB

### 3.3 Configure the MQTT broker node

Double-click the **Public Test Broker** config node and confirm exactly:

| Field | Value |
|---|---|
| Server | `test.mosquitto.org` (no `http://`, no trailing slash) |
| Port | 1883 |
| TLS | Off |
| Client ID | Leave blank |

**Common mistake:** if the Server field ever gets an `https://` prefix pasted into it (easy to do if copying from a browser address bar), the connection will hang on "connecting" forever and never error clearly. It must be the bare hostname only.

If `test.mosquitto.org` is ever slow/unreachable, `broker.hivemq.com` (same port, no auth) is a reliable fallback, just swap the Server field.

### 3.4 Configure the serial-in node (STM32 + BH1750)

Double-click the **serial** node and its linked config node, and set:

| Field | Value |
|---|---|
| Serial Port | Your STM32 Nucleo F411RE's COM port (e.g. COM14 on Windows) |
| Baud Rate | 9600 |
| Data bits | 8 |
| Parity | none |
| Stop bits | 1 |
| Newline char | `\n` |

### 3.5 Configure the InfluxDB node

Double-click the **Write to InfluxDB** node, and its linked config node, and set:

| Field | Value |
|---|---|
| URL | `http://localhost:8086` (Node-RED runs natively on the host, so it reaches InfluxDB's published port via `localhost`, not the Docker service name) |
| Version | 2.0 |
| Organization | `team7` |
| Bucket | `digital_twin` |
| Token | (see Section 4 below to generate this) |
| Measurement | `photodetector_reading` |

### 3.6 Deploy

Click Deploy (top right). If a dialog warns about unconfigured nodes, click "Search for invalid nodes" to jump straight to whichever field is still empty, Node-RED outlines missing/invalid fields in red when you open the node.

## 4. Set up InfluxDB

1. Open http://localhost:8086
2. Log in: username `admin`, password `adminadmin` (this is pre-set via the compose file's env vars, org `team7` and bucket `digital_twin` already exist, no onboarding wizard needed)
3. Left sidebar → Load Data → API Tokens
4. Click the existing token, or Generate API Token → All Access API Token
5. Copy the full token string and paste it into Node-RED's InfluxDB config (Section 3.5) and later into Grafana's data source (Section 5)

If this container ever gets removed/recreated, you'll need to repeat this token step, a fresh container means a fresh token.

## 5. Set up Grafana

### 5.1 Add InfluxDB as a data source

1. Open http://localhost:3000, log in with `admin` / `admin`
2. Left sidebar → Connections → Data sources → Add data source → InfluxDB
3. Fill in:
   - **Query Language:** Flux (not InfluxQL, InfluxDB 2.x tokens work differently under InfluxQL)
   - **URL:** `http://influxdb:8086` (Grafana runs in the same Docker network as InfluxDB, so it uses the service name)
   - **Organization:** `team7`
   - **Token:** paste the same token from Section 4
   - **Default Bucket:** `digital_twin`
4. Click Save & Test

If you get an "unauthorized: unauthorized access error reading buckets" error:
- Re-copy the token carefully (trailing spaces/missed characters are the most common cause)
- Make sure the token has All Access (or at least read access to `digital_twin`)
- Double-check Organization is `team7` exactly (not the org ID)
- Confirm Query Language is set to Flux

The data source usually still saves even if the test shows unauthorized, you can fix the token afterward without redoing this whole step.

### 5.2 Test your query in Explore first

Before building a dashboard panel, it's easier to confirm the query works using Explore (compass icon, left sidebar):

1. Pick the InfluxDB data source
2. Paste:

        from(bucket: "digital_twin")
          |> range(start: -15m)
          |> filter(fn: (r) => r._measurement == "photodetector_reading")
          |> filter(fn: (r) => r._field == "lux")

3. Run it, you should see a live line if data is flowing.

### 5.3 Build the dashboard panels

Once a query works in Explore, create a dashboard: Dashboards → New → New Dashboard → Add visualization → same data source → same query style, swapping the `_field` filter per panel:

| Panel | Fields to filter on | Suggested visualization |
|---|---|---|
| Comparison of Real-time Current | `predicted_current`, `measured_current` | Time series (line) |
| Model Error (MAE) | `error` | Gauge, thresholds: green < 0.05 |
| Illuminance & Output Voltage Trend | `lux`, `v_out` | Time series (line) |
| System Status | `status` | Stat panel, value mapping OK/FAULT |

Save the dashboard once you're happy with it: Save dashboard (top right), name it e.g. "Photodetector Digital Twin".

## 6. Set up the Blender 3D visualization

This project uses **Blender** (instead of NVIDIA Omniverse) for the 3D digital twin visualization, syncing live sensor readings from MQTT into the 3D scene via Blender's Python scripting API (`bpy`).

### 6.1 Open the Blender scene

1. Open Blender
2. File → Open → select `blender/Photodetector.blend` (from this repo)
3. This loads the 3D model of the photodetector setup (includes the `BH1750.stl` sensor model)
4. In the Outliner panel (top-right), check the exact name of the light object you want to drive (e.g. "Light", "Point", "Sun"), you'll need this in Section 6.3

### 6.2 Install the MQTT client library

The sync script imports `paho-mqtt`. Blender's bundled Python doesn't see packages installed via a regular system `pip install`, so the script itself works around this by manually appending your system Python's user site-packages folder to `sys.path` before importing.

Install `paho-mqtt` using your regular system Python (not Blender's):

    pip install paho-mqtt

This should be enough, since the script handles locating it. If it still can't find the module, double check the `_user_site` path near the top of `mqtt_lux_sync_blender.py` matches where pip actually installed it on your system.

### 6.3 Run the sync script

1. In Blender, switch to the **Scripting** tab (top menu)
2. Open `blender/mqtt_lux_sync_blender.py` (from this repo) in the text editor panel
3. Confirm the script's settings match your setup:
   - `LIGHT_OBJECT_NAME`, must exactly match the light object name you noted in Section 6.1
   - `LIGHT_ENERGY_SCALE`, tune until brightness changes are clearly visible
4. Click **Run Script** (▶ button)
5. The script starts a background MQTT thread and registers a Blender timer (`bpy.app.timers`) that checks for new lux readings every 0.2 seconds, updating the named light object's energy live as readings arrive

**Note:** this script must be run from inside Blender (it imports `bpy`), not as a standalone terminal command. Blender's console (Window → Toggle System Console on Windows) will show `[BlenderLuxSync]` log lines confirming MQTT connection and each light update.

### 6.4 Demonstrating it live

With InfluxDB/Grafana running (Section 2), Node-RED running and deployed (Section 3), the STM32 + BH1750 connected, and this script running in Blender, changing the light level on the real sensor should visibly update:
- The Grafana dashboard (Section 5.3)
- The Blender 3D scene's light object (this section)
- The `status` field (`OK`/`FAULT`) in InfluxDB

This live three-way sync (real sensor → dashboard → 3D visualization) is the core demo shown in the [video recordings](./Video_Link.md).

## 7. Everyday commands

    docker compose up -d               # start InfluxDB + Grafana
    docker compose stop                # stop, keep data
    docker compose down                # stop + remove containers (volumes/data still kept)
    docker compose ps                  # check what's running
    docker compose logs -f grafana     # watch Grafana's logs

## 8. Troubleshooting quick reference

| Symptom | Likely cause |
|---|---|
| MQTT node stuck on "connecting" | Broker Server field has `https://` or wrong hostname |
| `ECONNREFUSED` connecting to InfluxDB from Node-RED | Node-RED (native) should use `http://localhost:8086`, not `http://influxdb:8086`, since it's outside the Docker network |
| InfluxDB Data Explorer shows only one weird `measurement` field | `Write to InfluxDB` node expects a flat field object |
| Grafana: "unauthorized: unauthorized access error reading buckets" | Bad/incomplete token, wrong org, or InfluxQL instead of Flux |
| `docker compose up -d` fails with "port already allocated" | An old standalone container (before you had compose) is already using that port |
| Blender script errors on `import bpy` when run outside Blender | This script only runs inside Blender's Scripting tab, it cannot run as a plain terminal `python` command |
| Blender script can't find `paho-mqtt` | Confirm the `_user_site` path in the script matches where your system `pip` actually installed it |

## 9. Sharing this with the team

- `docker-compose.yml`, `nodered/digital_twin_flow.json`, and `blender/` should all live in the repo, anyone can `git pull`, run `docker compose up -d` for InfluxDB/Grafana, start Node-RED natively, and import the same flow/scene.
- The InfluxDB token and Grafana login are **not** stored in these files (by design, they're credentials), each person generates/enters their own after setup.
- If you improve the flow (e.g. add a new panel or fix a node), re-export it from Node-RED and commit the updated `digital_twin_flow.json` so the team stays in sync. Same applies to the Blender scene, save and re-commit `Photodetector.blend` after changes.
