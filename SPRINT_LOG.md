# Sprint Log, Digital Twin Photodetector Project

## Sprint 1, 20 July 2026 to 27 July 2026
**Goal:** Core pipeline design and hardware/sensor work (offline, pre-GitHub)

Work began offline before formal version control started: BH1750 sensor wiring and testing, initial Node-RED flow design, digital twin model design (predicted_current = K * lux), and early Grafana/Blender exploration. GitHub repo and PR-based version control began 27 July once implementation was ready to formalize.

| Member | Task |
|---|---|
| Safa | Docker Compose stack, repo setup, CI pipeline skeleton, branch workflow |
| Banaf | BH1750 sensor integration, Node-RED publisher/subscriber flow, Blender 3D model, Grafana dashboard |

**Deliverable:** Real sensor data flowing sensor to MQTT to InfluxDB, verified in Data Explorer; visualization components (Blender, Grafana) merged
**Merged to main:** 27 to 28 July 2026

---

## Sprint 2, 29 July 2026 to 31 July 2026
**Goal:** Data streaming and aggregation, AI/behavioral model, full test coverage, documentation

| Member | Task |
|---|---|
| Safa | Sprint log, STEPS.md, branch protection, PR review process, CI/CD maintenance |
| Nessa | Streaming and aggregation notebook |
| Sofea | AI/behavioral model notebook and fault classifier |
| Sobena | README.md and JSON work |
| Banaf | Demo video recordings |

**Deliverable:** Data aggregation notebook, AI fault-detection model, unit/integration/e2e tests, full documentation (README, STEPS.md, service contracts), video demos
**Merged to main:** 30 to 31 July 2026

---

## Development Practices Summary

- **Version control:** All contributions made via feature branches and pull requests, reviewed and approved before merging into `main`
- **CI/CD:** Automated build and test suite (`.github/workflows/ci.yml`) triggers on every push and pull request
- **Testing:** Unit tests for the fault classifier (`fault-service/tests/`), integration and end-to-end tests for the full pipeline (`tests/`)
- **Sprints:** 2 sprint cycles covering (1) core pipeline, sensor integration, and visualization, and (2) data aggregation, AI model, and documentation
