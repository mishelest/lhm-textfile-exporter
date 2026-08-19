# Contributing

This is a small personal project. Issues and PRs are welcome.

## Setup

Follow the Quick start in the [README](README.md). Use `config.yaml` for local settings — it is gitignored.

## Scope

v0.1.0 only exports **AMD CPU + NVIDIA GPU** sensors (plus motherboard, memory, and storage). Intel CPU and AMD GPU are planned; see the [open issues](https://github.com/mishelest/lhm-textfile-exporter/issues).

Sensor matching lives in `src/normalizer.py`. The mapping is documented in [docs/sensor-inventory.md](docs/sensor-inventory.md).

## Pull requests

- Open an issue first for anything larger than a small fix.
- For new hardware support, include a redacted LibreHardwareMonitor `/metrics` snippet (sensor names only, no need for live values).
- Do not commit `config.yaml`, `logs/`, or `*.prom` files.
