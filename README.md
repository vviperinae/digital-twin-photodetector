# Digital Twin Photodetector Project

A digital twin system for a photodetector (LDR/light sensor), simulating and monitoring real sensor behaviour through a live data pipeline: **sensor → MQTT → InfluxDB → Grafana**, with an AI-based fault detection layer and 3D visualization.

## Quick Links
- [Sprint Log](./SPRINT_LOG.md) - sprint planning, task ownership, deliverables
- [Setup Guide](./STEPS.md) - full stack setup instructions
- [Video Demos](./Video_Link.md) - recordings of the working system

## Team

| Name | Student ID |
|---|---|
| Safa Sarfraz | 24001006 |
| Puteri Banafsha Binti Azmi | 22010863 |
| Aisyah Sofea Binti Mohd Sallehuddin | 22011342 |
| Dania Anessa Binti Mohd Aswawi | 22011086 |
| Sobena A/P Ramachanthirarao | 22010905 |

## Project Overview

The digital twin models a photodetector using:

    predicted_current = K * lux

`lux` is captured from a real BH1750 sensor connected via an STM32 Nucleo F411RE (mbed toolchain), over serial. This predicted value is compared against a measured current (simulated pending additional hardware) to compute an error signal. If the error exceeds a threshold, the system flags a `FAULT` status, otherwise `OK`.

## Architecture

    BH1750 Sensor (STM32 Nucleo F411RE, real) → Node-RED (native install, serial in) → Twin Logic → MQTT (test.mosquitto.org)
                                                                      ↓
                                                        Node-RED (subscriber) → InfluxDB (Docker) → Grafana (Docker)
                                                                      ↓
                                                        Fault Classifier (Flask + Random Forest)

## Service Contracts

| From → To | Protocol | Port | Route/Topic | Format |
|---|---|---|---|---|
| BH1750 (STM32, serial) → Node-RED | Serial | COM14, 9600 baud | - | Plain text (`Lux: <value>`) |
| Node-RED → MQTT Broker | MQTT | 1883 | `photodetector/team7/reading` | JSON |
| MQTT Broker → Node-RED (subscriber) | MQTT | 1883 | `photodetector/team7/reading` | JSON |
| Node-RED → InfluxDB | HTTP | 8086 | `/api/v2/write?org=team7&bucket=digital_twin` | Line Protocol |
| Node-RED → Fault Service | HTTP POST | 5001 | `/predict` | JSON |
| Grafana → InfluxDB | HTTP (Flux) | 8086 | `/api/v2/query` | Flux/JSON |

## Repository Structure

    digital-twin-photodetector/
    ├── .github/workflows/       # CI/CD pipeline
    ├── blender/                 # 3D visualization (model + sync script, run inside Blender)
    ├── fault-service/           # Flask microservice + Random Forest fault classifier
    │   └── tests/                # Unit tests
    ├── grafana/                 # Dashboard export
    ├── influxdb/                 # Data export
    ├── nodered/                  # Node-RED flow export + docs
    ├── notebooks/                 # AI model + streaming/aggregation notebooks
    ├── tests/                     # Integration and end-to-end tests
    ├── docker-compose.yml        # Brings up InfluxDB + Grafana
    ├── SPRINT_LOG.md              # Sprint planning and execution log
    ├── STEPS.md                    # Full setup guide
    └── Video_Link.md                # Demo videos

## Setup

See [STEPS.md](./STEPS.md) for full setup instructions.

Quick start:

    docker compose up -d
    docker compose ps   # confirm influxdb2 and grafana are Up
    # Node-RED runs as a native install, started separately (see STEPS.md)

## Rubric Evidence Map

| Category | Evidence |
|---|---|
| **Visualization** | `blender/`, `grafana/grafana.json`, demo videos in [Video_Link.md](./Video_Link.md) |
| **AI/Behavioral Model** | `notebooks/ai_behavioral_model.ipynb`, `fault-service/` (Random Forest classifier + physics model in Node-RED twin logic) |
| **Data, Streaming, Aggregation** | `nodered/` (real BH1750/STM32 sensor stream via serial), `notebooks/streaming_aggregation.ipynb`, `influxdb/` |
| **Development Practices** | [SPRINT_LOG.md](./SPRINT_LOG.md), `.github/workflows/ci.yml`, pull request history |
| **Deployment** | `docker-compose.yml`, Service Contracts table above, demo video in [Video_Link.md](./Video_Link.md) |

## Development Practices

This project follows a sprint-based, PR-reviewed Git workflow. See:
- [SPRINT_LOG.md](./SPRINT_LOG.md) for sprint goals, task ownership, and deliverables per member
- [.github/workflows/ci.yml](./.github/workflows/ci.yml) for the CI/CD pipeline (automatic tests on every push/PR)
- Pull request history for individual contributions and peer review

## Demo

See [Video_Link.md](./Video_Link.md) for walkthrough demos of the working system.
