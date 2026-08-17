from dataclasses import dataclass, field


@dataclass(slots=True)
class Metric:
    name:   str
    value:  float
    labels: dict

@dataclass
class FanHardware:
    index:      int
    control:    float | None = None
    rpm:        float | None = None


# --------- CPU --------- #
@dataclass
class CpuCore:
    index:              int
    clock:              float | None = None
    effective_clock:    float | None = None
    voltage:            float | None = None
    power:              float | None = None
    load:               float | None = None

@dataclass
class CpuHardware:
    package_temp:               float | None = None # Tctl/Tdie
    ccd_temp:                   float | None = None # CCD1

    total_load:                 float | None = None
    max_core_load:              float | None = None

    average_clock:              float | None = None
    average_effective_clock:    float | None = None
    package_power:              float | None = None

    cores:                      dict[int, CpuCore] = field(default_factory=dict)


# --------- Motherboard --------- #
@dataclass
class MotherboardHardware:
    fans:           dict[str, FanHardware] = field(default_factory=dict)
    temperature:    dict[str, float] = field(default_factory=dict)
    voltage:        dict[str, float] = field(default_factory=dict)


# --------- GPU (NVIDIA) --------- #
@dataclass
class GpuHardware:
    core_temp:                  float | None = None
    memory_junction_temp:       float | None = None

    core_load:                  float | None = None
    memory_load:                float | None = None
    memory_controller_load:     float | None = None
    d3d_3d_load:                float | None = None

    power:                      float | None = None

    core_clock:                 float | None = None
    memory_clock:               float | None = None

    memory_used:                float | None = None
    memory_free:                float | None = None
    memory_total:               float | None = None
    d3d_dedicated_memory_used:  float | None = None
    d3d_shared_memory_used:     float | None = None

    pcie_rx:                    float | None = None
    pcie_tx:                    float | None = None

    fans:                       dict[int, FanHardware] = field(default_factory=dict)


# --------- Memory --------- #
@dataclass
class MemoryHardware:
    load:               float | None = None
    used:               float | None = None
    available:          float | None = None

    virtual_load:       float | None = None
    virtual_used:       float | None = None
    virtual_available:  float | None = None

    dimms:              dict[str, float] = field(default_factory=dict)


# --------- Storage --------- #
@dataclass
class StorageDevice:
    name:               str
    temperature:        float | None = None

    read_activity:      float | None = None
    write_activity:     float | None = None
    total_activity:     float | None = None

    read_rate:          float | None = None
    write_rate:         float | None = None

    used_space:         float | None = None
    free_space:         float | None = None

    life:               float | None = None
    percentage_used:    float | None = None
    available_spare:    float | None = None

@dataclass
class StorageHardware:
    devices:     dict[str, StorageDevice] = field(default_factory=dict)



@dataclass
class HardwareMetrics:
    motherboard:    MotherboardHardware = field(default_factory=MotherboardHardware)
    cpu:            CpuHardware = field(default_factory=CpuHardware)
    gpu:            GpuHardware = field(default_factory=GpuHardware)
    memory:         MemoryHardware = field(default_factory=MemoryHardware)
    storage:        StorageHardware = field(default_factory=StorageHardware)


@dataclass
class ExporterHealth:
    up:                             int = 0
    scrape_duration_seconds:        float = 0.0
    last_scrape_success_timestamp:  float = 0.0
    scrape_errors_total:            float = 0.0