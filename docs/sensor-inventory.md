# Sensor inventory

Mapping from LibreHardwareMonitor `/metrics` sensors to the `hardware_*` series written into the textfile.

v0.1.0 supports **AMD CPU + NVIDIA GPU + NVMe/SSD/HDD** on Windows. Intel CPU and AMD GPU sensors are not exported; unknown sensors are skipped (logged at DEBUG).

This inventory was built from one live LHM scrape (2026-08-18) on:

| Group | Hardware |
|---|---|
| CPU | AMD Ryzen 7 7800X3D |
| Motherboard | ASUS TUF GAMING B850-PLUS WIFI |
| GPU | NVIDIA GeForce RTX 5070 |
| iGPU (not exported) | AMD Radeon(TM) Graphics |
| Memory | Total / Virtual Memory, Kingston KF560C30-16 DIMM 1 and DIMM 3 |
| Storage | CT1000T500SSD5, WD_BLACK SN850X 4000GB, TS480GSSD220S, KINGSTON SHFS37A240G, WDC WD10EZEX-00BN5A0 |

LHM labels used for matching: `sensorName`, and `hardwareName` for memory and storage. `N` in the tables is the index LHM puts in the sensor name (core, thread, fan, DIMM).

---

## CPU

`lhm_cpu_*` from the AMD package. Per-core clock / VID / SMU power use physical cores (`1`–`8` here). Load uses LHM's `CPU Core N` series, which on this chip is 16 logical processors.

| LHM metric / `sensorName` | Exported metric | Labels | Notes |
|---|---|---|---|
| `lhm_cpu_temperature_celsius` / `Core (Tctl/Tdie)` | `hardware_cpu_package_temperature_celsius` | — | Package temperature |
| `lhm_cpu_temperature_celsius` / `CCD*` (here `CCD1 (Tdie)`) | `hardware_cpu_ccd_temperature_celsius` | — | Last matching CCD sensor wins |
| `lhm_cpu_load_percent` / `CPU Total` | `hardware_cpu_total_load_percent` | — | |
| `lhm_cpu_load_percent` / `CPU Core Max` | `hardware_cpu_max_core_load_percent` | — | |
| `lhm_cpu_load_percent` / `CPU Core N` | `hardware_cpu_core_load_percent` | `core="N"` | Logical processors on this CPU (`1`–`16`) |
| `lhm_cpu_power_watts` / `Package` | `hardware_cpu_package_power_watts` | — | |
| `lhm_cpu_power_watts` / `Core N (SMU)` | `hardware_cpu_core_power_watts` | `core="N"` | Physical cores |
| `lhm_cpu_clock_hertz` / `Cores (Average)` | `hardware_cpu_average_clock_hertz` | — | |
| `lhm_cpu_clock_hertz` / `Cores (Average Effective)` | `hardware_cpu_average_effective_clock_hertz` | — | |
| `lhm_cpu_clock_hertz` / `Core N` | `hardware_cpu_core_clock_hertz` | `core="N"` | Physical cores |
| `lhm_cpu_clock_hertz` / `Core N (Effective)` | `hardware_cpu_core_effective_clock_hertz` | `core="N"` | Physical cores |
| `lhm_cpu_voltage_volts` / `Core N VID` | `hardware_cpu_core_voltage_volts` | `core="N"` | Physical cores |

**Not exported**

| LHM metric / `sensorName` | Notes |
|---|---|
| `lhm_cpu_clock_hertz` / `Bus Speed` | Intentionally skipped |
| `lhm_cpu_factor` / `Core N` | Clock multiplier; no `hardware_*` series |

---

## Motherboard

`lhm_motherboard_*`. Fan index comes from `Fan N`. Temperature and voltage sensor names are copied into the `sensor` label as LHM reports them.

| LHM metric / `sensorName` | Exported metric | Labels | Notes |
|---|---|---|---|
| `lhm_motherboard_fan_rpm` / `Fan N` | `hardware_motherboard_fan_rpm` | `fan="N"` | Fans 1–7 on this board; RPM `0` means no tach / not spinning |
| `lhm_motherboard_control_percent` / `Fan N` | `hardware_motherboard_fan_control` | `fan="N"` | PWM duty cycle |
| `lhm_motherboard_temperature_celsius` / any | `hardware_motherboard_temperature_celsius` | `sensor="<sensorName>"` | This scrape: `CPU Core`, `Temperature 1`–`6` |
| `lhm_motherboard_voltage_volts` / any | `hardware_motherboard_voltage_volts` | `sensor="<sensorName>"` | This scrape: `Vcore`, `CPU Termination`, `AVCC`, `+3.3V`, `+3V Standby`, `Voltage 2`, `5`–`7`, `11`–`15` |

---

## NVIDIA GPU

`lhm_gpunvidia_*` from the discrete NVIDIA card. AMD iGPU (`lhm_gpuamd_*`) is not exported.

| LHM metric / `sensorName` | Exported metric | Labels | Notes |
|---|---|---|---|
| `lhm_gpunvidia_temperature_celsius` / `GPU Core` | `hardware_gpu_core_temperature_celsius` | — | |
| `lhm_gpunvidia_temperature_celsius` / `GPU Memory Junction` | `hardware_gpu_memory_junction_temperature_celsius` | — | |
| `lhm_gpunvidia_load_percent` / `GPU Core` | `hardware_gpu_core_load_percent` | — | |
| `lhm_gpunvidia_load_percent` / `GPU Memory` | `hardware_gpu_memory_load_percent` | — | |
| `lhm_gpunvidia_load_percent` / `GPU Memory Controller` | `hardware_gpu_memory_controller_load_percent` | — | |
| `lhm_gpunvidia_load_percent` / `D3D 3D` | `hardware_gpu_d3d_3d_load_percent` | — | |
| `lhm_gpunvidia_power_watts` / `GPU Package` | `hardware_gpu_power_watts` | — | |
| `lhm_gpunvidia_clock_hertz` / `GPU Core` | `hardware_gpu_core_clock_hertz` | — | |
| `lhm_gpunvidia_clock_hertz` / `GPU Memory` | `hardware_gpu_memory_clock_hertz` | — | |
| `lhm_gpunvidia_smalldata_bytes` / `GPU Memory Used` | `hardware_gpu_memory_used_bytes` | — | |
| `lhm_gpunvidia_smalldata_bytes` / `GPU Memory Free` | `hardware_gpu_memory_free_bytes` | — | |
| `lhm_gpunvidia_smalldata_bytes` / `GPU Memory Total` | `hardware_gpu_memory_total_bytes` | — | |
| `lhm_gpunvidia_smalldata_bytes` / `D3D Dedicated Memory Used` | `hardware_gpu_d3d_dedicated_memory_used_bytes` | — | |
| `lhm_gpunvidia_smalldata_bytes` / `D3D Shared Memory Used` | `hardware_gpu_d3d_shared_memory_used_bytes` | — | |
| `lhm_gpunvidia_throughput_bytes_per_second` / `GPU PCIe Rx` | `hardware_gpu_pcie_rx_bytes_per_second` | — | |
| `lhm_gpunvidia_throughput_bytes_per_second` / `GPU PCIe Tx` | `hardware_gpu_pcie_tx_bytes_per_second` | — | |
| `lhm_gpunvidia_fan_rpm` / `GPU Fan N` | `hardware_gpu_fan_rpm` | `fan="N"` | Fans 1–2 on this card |
| `lhm_gpunvidia_control_percent` / `GPU Fan N` | `hardware_gpu_fan_control` | `fan="N"` | |

**Not exported**

| LHM metric / `sensorName` | Notes |
|---|---|
| `lhm_gpunvidia_voltage_volts` / `GPU Core Voltage` | No `hardware_*` series |
| `lhm_gpunvidia_load_percent` / `GPU Power`, `GPU Board Power`, `GPU Bus`, `GPU Video Engine` | Extra load/limit sensors |
| `lhm_gpunvidia_load_percent` / `D3D Copy`, `D3D Video Decode`, `D3D Video Encode`, `D3D JPEG Decode 0`, `D3D Optical Flow Accelerator 0`, `D3D Security`, `D3D VR` | Extra D3D engines |

---

## Memory

Physical vs virtual is chosen by `hardwareName` (`Total Memory` vs `Virtual Memory`). DIMM temperatures use `sensorName`.

| LHM metric / `sensorName` (`hardwareName`) | Exported metric | Labels | Notes |
|---|---|---|---|
| `lhm_memory_load_percent` / `Memory` (`Total Memory`) | `hardware_memory_load_percent` | — | |
| `lhm_memory_data_bytes` / `Memory Used` (`Total Memory`) | `hardware_memory_used_bytes` | — | |
| `lhm_memory_data_bytes` / `Memory Available` (`Total Memory`) | `hardware_memory_available_bytes` | — | |
| `lhm_memory_load_percent` / `Memory` (`Virtual Memory`) | `hardware_virtual_memory_load_percent` | — | |
| `lhm_memory_data_bytes` / `Memory Used` (`Virtual Memory`) | `hardware_virtual_memory_used_bytes` | — | |
| `lhm_memory_data_bytes` / `Memory Available` (`Virtual Memory`) | `hardware_virtual_memory_available_bytes` | — | |
| `lhm_memory_temperature_celsius` / `DIMM*` | `hardware_memory_dimm_temperature_celsius` | `dimm="<sensorName>"` | This scrape: `DIMM 1`, `DIMM 3` |

---

## Storage

One series per device. The `device` label is LHM `hardwareName`. NVMe drives often use `Composite Temperature`; SATA SSD/HDD often use `Temperature`.

| LHM metric / `sensorName` | Exported metric | Labels | Notes |
|---|---|---|---|
| `lhm_storage_temperature_celsius` / `Composite Temperature` or `Temperature` | `hardware_storage_temperature_celsius` | `device="<hardwareName>"` | |
| `lhm_storage_load_percent` / `Used Space` | `hardware_storage_used_space_percent` | `device="<hardwareName>"` | |
| `lhm_storage_load_percent` / `Read Activity` | `hardware_storage_read_activity_percent` | `device="<hardwareName>"` | |
| `lhm_storage_load_percent` / `Write Activity` | `hardware_storage_write_activity_percent` | `device="<hardwareName>"` | |
| `lhm_storage_load_percent` / `Total Activity` | `hardware_storage_total_activity_percent` | `device="<hardwareName>"` | |
| `lhm_storage_data_bytes` / `Free Space` | `hardware_storage_free_space_bytes` | `device="<hardwareName>"` | |
| `lhm_storage_throughput_bytes_per_second` / `Read Rate` | `hardware_storage_read_rate_bytes_per_second` | `device="<hardwareName>"` | |
| `lhm_storage_throughput_bytes_per_second` / `Write Rate` | `hardware_storage_write_rate_bytes_per_second` | `device="<hardwareName>"` | |
| `lhm_storage_level_percent` / `Life` | `hardware_storage_life_percent` | `device="<hardwareName>"` | Remaining life |
| `lhm_storage_level_percent` / `Percentage Used` | `hardware_storage_percentage_used` | `device="<hardwareName>"` | Wear (NVMe) |
| `lhm_storage_level_percent` / `Available Spare` | `hardware_storage_available_spare_percent` | `device="<hardwareName>"` | NVMe |

**Not exported**

| LHM metric / `sensorName` | Notes |
|---|---|
| `lhm_storage_data_bytes` / `Data Read`, `Data Written`, `NAND writes` | Lifetime totals |
| `lhm_storage_factor` / `Power On Hours`, `Power On Count` | SMART counters |
| `lhm_storage_level_percent` / `Available Spare Threshold` | Threshold, not current spare |
| `lhm_storage_temperature_celsius` / `Temperature 1`, `Warning Temperature`, `Critical Temperature` | Extra NVMe temp / threshold sensors |

---

## Not collected (whole LHM groups)

These groups were present in the scrape and are classified, then dropped. No `hardware_*` series.

| LHM group | Hardware in this scrape | Examples |
|---|---|---|
| `gpuamd` | AMD Radeon(TM) Graphics (7800X3D iGPU) | Core/SoC clocks, D3D loads, iGPU memory |
| `network` | Ethernet, Tailscale, Wi-Fi, Wi-Fi 3 | Download/upload bytes, throughput, utilization |

Intel CPU sensors would also be skipped (different `sensorName` values than the AMD matchers above).

---

## Exporter health

Not from LHM. Always written next to the hardware series.

| Metric | Meaning |
|---|---|
| `hardware_exporter_up` | `1` if the last LHM scrape succeeded, else `0` |
| `hardware_exporter_scrape_duration_seconds` | Last scrape attempt duration |
| `hardware_exporter_last_scrape_success_timestamp` | Unix time of last successful scrape |
| `hardware_exporter_scrape_errors_total` | Scrape errors since process start |
