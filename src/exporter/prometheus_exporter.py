import os
import time
from pathlib import Path

from src.models import (
    HardwareMetrics,
    MotherboardHardware,
    CpuHardware,
    GpuHardware,
    MemoryHardware,
    StorageHardware,
)


class PrometheusExporter:

    def __init__(
        self,
        output_dir: str = "textfile_inputs",
        output_file: str = "hardware.prom",
    ):

        self.output_dir = Path(output_dir)
        self.output_file = output_file



    def write(self, hardware_metrics: HardwareMetrics):

        lines = self.write_hardware(hardware_metrics)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        target = self.output_dir /  self.output_file
        output_path = self.output_dir / f"{self.output_file}.tmp"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            f.write("\n")




    def write_hardware(self, hardware_metrics: HardwareMetrics):

        lines = []
        seen: set[str] = set()

        lines = self._write_motherboard(lines, seen, hardware_metrics.motherboard)
        lines = self._write_cpu(lines, seen, hardware_metrics.cpu)
        lines = self._write_gpu(lines, seen, hardware_metrics.gpu)
        lines = self._write_memory(lines, seen, hardware_metrics.memory)
        lines = self._write_storage(lines, seen, hardware_metrics.storage)

        return lines




    def _gauge(
        self,
        lines: list[str],
        seen: set[str],
        name: str,
        help_text: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> list[str]:

        # -- Append HELP/TYPE only once per metric -- #
        if name not in seen:
            lines.append(f"# HELP {name} {help_text}")
            lines.append(f"# TYPE {name} gauge")
            seen.add(name)

        if labels:
            label_str = ",".join(f'{key}="{val}"' for key, val in labels.items())
            lines.append(f"{name}{{{label_str}}} {value}")

        else:
            lines.append(f"{name} {value}")

        return lines



    
    def _write_motherboard(self, lines, seen, motherboard: MotherboardHardware):

        # Fans
        for fan in motherboard.fans.values():
            print(fan)

            if fan.rpm is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_motherboard_fan_rpm",
                    "Motherboard fan speed in RPM",
                    fan.rpm,
                    {"fan": str(fan.index)},
                )

            if fan.control is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_motherboard_fan_control",
                    "Motherboard fan control percentage",
                    fan.control,
                    {"fan": str(fan.index)},
                )

            
        # Temperature
        for sensor, temp in motherboard.temperature.items():
            lines = self._gauge(
                lines, seen,
                "hardware_motherboard_temperature_celsius",
                "Motherboard temperature in Celsius",
                temp,
                {"sensor": sensor},
            )

        # Volts
        for sensor, volts in motherboard.voltage.items():
            lines = self._gauge(
                lines, seen,
                "hardware_motherboard_voltage_volts",
                "Motherboard voltage in volts",
                volts,
                {"sensor": sensor}
            )

        return lines


    def _write_cpu(self, lines, seen, cpu: CpuHardware):

        # Package temperature
        if cpu.package_temp is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_cpu_package_temperature_celsius",
                "CPU package temperature in Celsius",
                cpu.package_temp
            )

        # CCD temperature
        if cpu.ccd_temp is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_cpu_ccd_temperature_celsius",
                "CPU CCD temperature in Celsius",
                cpu.ccd_temp
            )

        # Total load
        if cpu.total_load is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_cpu_total_load_percent",
                "CPU total load percentage",
                cpu.total_load
            )

        # Max core load
        if cpu.max_core_load is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_cpu_max_core_load_percent",
                "CPU max core load percent",
                cpu.max_core_load
            )

        # Package power
        if cpu.package_power is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_cpu_package_power_watts",
                "CPU package power in watts",
                cpu.package_power
            )

        # Average clock
        if cpu.average_clock is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_cpu_average_clock_hertz",
                "CPU average clock in hertz",
                cpu.average_clock
            )

        # Average effective clock
        if cpu.average_effective_clock is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_cpu_average_effective_clock_hertz",
                "CPU average effective clock in hertz",
                cpu.average_effective_clock
            )


        # Per-core
        for core in cpu.cores.values():

            # Clock
            if core.clock is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_cpu_core_clock_hertz",
                    "CPU per-core clock in hertz",
                    core.clock,
                    {"core": str(core.index)},
            )

        for core in cpu.cores.values():
            # Effective clock
            if core.effective_clock is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_cpu_core_effective_clock_hertz",
                    "CPU per-core effective clock in hertz",
                    core.effective_clock,
                    {"core": str(core.index)},
            )

        for core in cpu.cores.values():
            # Voltage
            if core.voltage is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_cpu_core_voltage_volts",
                    "CPU per-core voltage in volts",
                    core.voltage,
                    {"core": str(core.index)},
            )

        for core in cpu.cores.values():
            # Power
            if core.power is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_cpu_core_power_watts",
                    "CPU per-core power in watts",
                    core.power,
                    {"core": str(core.index)},
            )

        for core in cpu.cores.values():
            # Load
            if core.load is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_cpu_core_load_percent",
                    "CPU per-core load percentage",
                    core.load,
                    {"core": str(core.index)},
            )

        return lines


    def _write_gpu(self, lines, seen, gpu: GpuHardware):

        if gpu.core_temp is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_core_temperature_celsius",
                "GPU core temperature in Celsius",
                gpu.core_temp,
            )

        if gpu.memory_junction_temp is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_memory_junction_temperature_celsius",
                "GPU memory junction temperature in Celsius",
                gpu.memory_junction_temp,
            )

        if gpu.core_load is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_core_load_percent",
                "GPU core load percentage",
                gpu.core_load,
            )

        if gpu.memory_load is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_memory_load_percent",
                "GPU memory load percentage",
                gpu.memory_load,
            )

        if gpu.memory_controller_load is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_memory_controller_load_percent",
                "GPU memory controller load percentage",
                gpu.memory_controller_load,
            )

        if gpu.d3d_3d_load is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_d3d_3d_load_percent",
                "GPU D3D 3D load percentage",
                gpu.d3d_3d_load,
            )

        if gpu.power is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_power_watts",
                "GPU package power in watts",
                gpu.power,
            )

        if gpu.core_clock is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_core_clock_hertz",
                "GPU core clock in hertz",
                gpu.core_clock,
            )

        if gpu.memory_clock is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_memory_clock_hertz",
                "GPU memory clock in hertz",
                gpu.memory_clock,
            )

        if gpu.memory_used is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_memory_used_bytes",
                "GPU memory used in bytes",
                gpu.memory_used,
            )

        if gpu.memory_free is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_memory_free_bytes",
                "GPU memory free in bytes",
                gpu.memory_free,
            )

        if gpu.memory_total is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_memory_total_bytes",
                "GPU memory total in bytes",
                gpu.memory_total,
            )

        if gpu.d3d_dedicated_memory_used is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_d3d_dedicated_memory_used_bytes",
                "GPU D3D dedicated memory used in bytes",
                gpu.d3d_dedicated_memory_used,
            )

        if gpu.d3d_shared_memory_used is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_d3d_shared_memory_used_bytes",
                "GPU D3D shared memory used in bytes",
                gpu.d3d_shared_memory_used,
            )

        if gpu.pcie_rx is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_pcie_rx_bytes_per_second",
                "GPU PCIe receive throughput in bytes per second",
                gpu.pcie_rx,
            )

        if gpu.pcie_tx is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_gpu_pcie_tx_bytes_per_second",
                "GPU PCIe transmit throughput in bytes per second",
                gpu.pcie_tx,
            )

        for fan in gpu.fans.values():

            if fan.rpm is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_gpu_fan_rpm",
                    "GPU fan speed in RPM",
                    fan.rpm,
                    {"fan": str(fan.index)},
                )

            if fan.control is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_gpu_fan_control",
                    "GPU fan control percentage",
                    fan.control,
                    {"fan": str(fan.index)},
                )

        return lines


    def _write_memory(self, lines, seen, memory: MemoryHardware):

        if memory.load is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_memory_load_percent",
                "Physical memory load percentage",
                memory.load,
            )

        if memory.used is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_memory_used_bytes",
                "Physical memory used in bytes",
                memory.used,
            )

        if memory.available is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_memory_available_bytes",
                "Physical memory available in bytes",
                memory.available,
            )

        if memory.virtual_load is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_virtual_memory_load_percent",
                "Virtual memory load percentage",
                memory.virtual_load,
            )

        if memory.virtual_used is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_virtual_memory_used_bytes",
                "Virtual memory used in bytes",
                memory.virtual_used,
            )

        if memory.virtual_available is not None:
            lines = self._gauge(
                lines, seen,
                "hardware_virtual_memory_available_bytes",
                "Virtual memory available in bytes",
                memory.virtual_available,
            )

        for dimm, temp in memory.dimms.items():
            lines = self._gauge(
                lines, seen,
                "hardware_memory_dimm_temperature_celsius",
                "DIMM temperature in Celsius",
                temp,
                {"dimm": dimm},
            )

        return lines


    def _write_storage(self, lines, seen, storage: StorageHardware):

        for device in storage.devices.values():
            if device.temperature is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_temperature_celsius",
                    "Storage device temperature in Celsius",
                    device.temperature,
                    {"device": device.name},
                )

        for device in storage.devices.values():
            if device.read_activity is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_read_activity_percent",
                    "Storage read activity percentage",
                    device.read_activity,
                    {"device": device.name},
                )

        for device in storage.devices.values():
            if device.write_activity is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_write_activity_percent",
                    "Storage write activity percentage",
                    device.write_activity,
                    {"device": device.name},
                )

        for device in storage.devices.values():
            if device.total_activity is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_total_activity_percent",
                    "Storage total activity percentage",
                    device.total_activity,
                    {"device": device.name},
                )

        for device in storage.devices.values():
            if device.read_rate is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_read_rate_bytes_per_second",
                    "Storage read rate in bytes per second",
                    device.read_rate,
                    {"device": device.name},
                )

        for device in storage.devices.values():
            if device.write_rate is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_write_rate_bytes_per_second",
                    "Storage write rate in bytes per second",
                    device.write_rate,
                    {"device": device.name},
                )

        for device in storage.devices.values():
            if device.used_space is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_used_space_percent",
                    "Storage used space percentage",
                    device.used_space,
                    {"device": device.name},
                )

        for device in storage.devices.values():
            if device.free_space is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_free_space_bytes",
                    "Storage free space in bytes",
                    device.free_space,
                    {"device": device.name},
                )

        for device in storage.devices.values():
            if device.life is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_life_percent",
                    "Storage remaining life percentage",
                    device.life,
                    {"device": device.name},
                )

        for device in storage.devices.values():
            if device.percentage_used is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_percentage_used",
                    "Storage percentage used (wear)",
                    device.percentage_used,
                    {"device": device.name},
                )

        for device in storage.devices.values():
            if device.available_spare is not None:
                lines = self._gauge(
                    lines, seen,
                    "hardware_storage_available_spare_percent",
                    "Storage available spare percentage",
                    device.available_spare,
                    {"device": device.name},
                )

        return lines














        