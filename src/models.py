from dataclasses import dataclass, field


@dataclass(slots=True)
class Metric:
    name:   str
    value:  str
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







@dataclass
class HardwareMetrics:
    cpu: CpuHardware = field(default_factory=CpuHardware)