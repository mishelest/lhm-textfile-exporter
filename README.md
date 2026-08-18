# lhm-textfile-exporter

A small Windows tool that grabs hardware sensor data from
[LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor)
and turns it into clean Prometheus metrics for
[windows_exporter](https://github.com/prometheus-community/windows_exporter).

This project is a **textfile writer**, not a Prometheus HTTP server. It does not
expose its own `/metrics` endpoint — `windows_exporter` (or another textfile
collector) serves the file it produces.

```text
LibreHardwareMonitor -> lhmTF-exporter -> windows_exporter -> Prometheus -> Grafana
```

## Planned Features
- Collect hardware metrics from LibreHardwareMonitor
- Parse LHM's Prometheus-formatted `/metrics` endpoint
- Normalize hardware-specific sensor names and units
- Export hardware metrics in Prometheus textfile format
- Atomic `.prom` file updates
- Resilient handling of LHM and filesystem failures
- Exporter health metrics
- Configurable collection interval and output location
- Designed to run continuously on Windows


## Status
This project is currently in early development and is being rebuilt from an
existing working implementation.

The first public release target is `v0.1.0`.

**Validated on:** AMD CPU + NVIDIA GPU + NVMe/SSD/HDD (Windows).


## Requirements
- Windows
- Python 3.10+
- [LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) - Web server enabled
- [windows_exporter](https://github.com/prometheus-community/windows_exporter) - Textfile collector enabled

## Quick Start

```
Coming Soon...
```

## Roadmap

### Repository Setup
- [x] Create public repository
- [x] Add `.gitignore` (Python, venv, logs, `config.yaml`, `*.prom`)
- [x] Add MIT `LICENSE`
- [x] Add `README.md`
- [x] Define project layout
- [x] Add `requirements.txt`


### Config
- [x] Create `config.default.yaml`
- [x] Config loader (copy default -> `config.yaml` on first run)

### Domain Models
- [x] `Metric`
- [x] CPU models
- [x] GPU models
- [x] Motherboard models
- [x] Memory models
- [x] Storage models
- [x] `HardwareMetrics`
- [x] `ExporterHealth`

### Ingest Pipeline
- [x] Fetch LibreHardwareMonitor `/metrics`
- [x] Handle connection failures, invalid responses, empty responses
- [x] Log connection errors
- [x] Parse Prometheus text
- [x] Parse metrics names, labels, values
- [x] Handle unknown metrics - skip
- [x] Classify metrics by hardware group (`cpu`, `gpunvidia`, `storage`, ...)

### Normalize (AMD CPU + NVIDIA GPU + Disks)
- [x] Normalizer skeleton + safe index helpers
- [x] Motherboard fans / temps / voltages
- [x] AMD CPU Package + per-core sensors
- [x] NVIDIA GPU sensors
- [x] Memory sensors
- [x] Storage sensors (NVMe, SSD, HDD)

### Export & run
- [x] Prometheus textfile writer (`# HELP` / `# TYPE`, atomic write + Windows retry)
- [x] Export all hardware metrics (`hardware_*`)
- [x] Exporter health metrics (`up`, scrape duration, last success, errors)
- [x] Service wiring (config + pipeline + logging setup)
- [x] Resilient scrape loop (keep last good samples; rewrite file with `up=0` on failure)
- [x] `main.py` entrypoint
- [x] End-to-end verified run with LibreHardwareMonitor + `hardware.prom` updates

### Logging
#### Console Logging
- [x] Startup information
- [x] Configuration information
- [x] Errors and warnings

#### File Logging
- [x] File logging
- [x] Error logging

### Docs before release
- [x] Sensor inventory (`docs/sensor-inventory.md`)
- [ ] Full README (quick start, verified setup, PromQL examples, code layout)


## v0.1.0 - Release
- [ ] Minimal Grafana examples (`docs/grafana/`)
- [ ] Bump `__version__` to `0.1.0`
- [ ] Tag and publish `v0.1.0`


## Later

### Reliability & operations
- [ ] Windows Service
- [ ] Log rotation
- [ ] Alertmanager / Prometheus alert examples

### Quality
- [ ] Unit tests (parser / classifier / normalizer)
- [ ] Github Actions CI

### Packaging & Flexibility
- [ ] Simple installer / packaging
- [ ] Config-driven sensor allowlists
- [ ] Broader hardware support (Intel CPU, AMD GPU, ...)
