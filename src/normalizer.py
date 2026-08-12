from src.models import (
    Metric, HardwareMetrics, FanHardware, CpuCore,
    CpuHardware, MotherboardHardware, GpuHardware,
    MemoryHardware, StorageDevice, StorageHardware
)



class Normalizer:

    def normalize(self, metrics: dict[str, list[Metric]]) -> HardwareMetrics:

        hardware_metrics = HardwareMetrics()

        hardware_metrics.cpu = self._normalize_cpu(metrics.get("cpu", []))
        hardware_metrics.motherboard = self._normalize_motherboard(metrics.get("motherboard", []))
        hardware_metrics.memory = self._normalize_memory(metrics.get("memory", []))
        hardware_metrics.gpu = self._normalize_gpu_nvidia(metrics.get("gpunvidia", []))
        hardware_metrics.storage = self._normalize_storage(metrics.get("storage", []))

        return hardware_metrics




    def _normalize_cpu(self, cpu_metrics: list[Metric]) -> CpuHardware:

        cpu = CpuHardware()

        for metric in cpu_metrics:

            parts = metric.name.split("_")
            if len(parts) < 3:
                continue

            metric_type = parts[2]
            value = metric.value

            sensor_name = metric.labels.get("sensorName")
            if sensor_name is None:
                continue

            sensor_parts = sensor_name.split(" ")

            match metric_type:

                # -- Voltage -- #
                case "voltage":
                    core_index = self._get_core_index(sensor_name, 1)
                    if core_index is None:
                        continue

                    core = self._get_core(core_index, cpu)
                    core.voltage = value


                # -- Power -- #                    
                case "power":
                    if sensor_name == "Package":
                        cpu.package_power = value

                    elif sensor_name.startswith("Core "):
                        core_index = self._get_core_index(sensor_name, 1)
                        if core_index is None:
                            continue

                        core = self._get_core(core_index, cpu)
                        core.power = value


                # -- Clock Speed -- #
                case "clock":
                    if sensor_name == "Bus Speed":
                        continue

                    elif sensor_name == "Cores (Average)":
                        cpu.average_clock = value

                    elif sensor_name == "Cores (Average Effective)":
                        cpu.average_effective_clock = value

                    else:
                        core_index = self._get_core_index(sensor_name, 1)
                        if core_index is None:
                            continue

                        core = self._get_core(core_index, cpu)
                        if len(sensor_parts) < 3:
                            core.clock = value
                        else:
                            core.effective_clock = value


                # -- Temperature -- #
                case "temperature":
                    if sensor_name == "Core (Tctl/Tdie)":
                        cpu.package_temp = value

                    elif sensor_name.startswith("CCD"):
                        cpu.ccd_temp = value


                # -- Load -- #
                case "load":
                    if sensor_name == "CPU Total":
                        cpu.total_load = value

                    elif sensor_name == "CPU Core Max":
                        cpu.max_core_load = value

                    elif sensor_name.startswith("CPU Core"):
                        core_index = self._get_core_index(sensor_name, 2)
                        if core_index is None:
                            continue

                        core = self._get_core(core_index, cpu)
                        core.load = value

        return cpu


    def _normalize_motherboard(self, motherboard_metrics: list[Metric]) -> MotherboardHardware:

        motherboard = MotherboardHardware()

        for metric in motherboard_metrics:

            sensor_name = metric.labels.get("sensorName")
            if sensor_name is None:
                continue

            value = metric.value

            match metric.name:

                # -- Fan RPM -- #
                case "lhm_motherboard_fan_rpm":

                    fan_index = self._get_fan_index(sensor_name, 1)
                    if fan_index is None:
                        continue

                    fan = self._get_fan_motherboard(fan_index, motherboard)
                    fan.rpm = value


                # -- Fan Control -- #
                case "lhm_motherboard_fan_control_percent":

                    fan_index = self._get_fan_index(sensor_name, 1)
                    if fan_index is None:
                        continue

                    fan = self._get_fan_motherboard(fan_index, motherboard)
                    fan.control = value


                # -- Temperature -- #
                case "lhm_motherboard_temperature_celsius":
                    motherboard.temperature[sensor_name] = value


                # -- Voltage -- #
                case "lhm_motherboard_voltage_volts":
                    motherboard.voltage[sensor_name] = value

        return motherboard


    def _normalize_memory(self, memory_metrics: list[Metric]) -> MemoryHardware:
        memory = MemoryHardware()

        for metric in memory_metrics:

            sensor_name = metric.labels.get("sensorName")
            hardware_name = metric.labels.get("hardwareName")
            if sensor_name is None or hardware_name is None:
                continue

            value = metric.value

            match metric.name:

                # -- Load % -- #
                case "lhm_memory_load_percent":
                    if hardware_name == "Total Memory":
                        memory.load = value
                    elif hardware_name == "Virtual Memory":
                        memory.virtual_load = value


                # -- Bytes Usage -- #
                case "lhm_memory_data_bytes":
                    if hardware_name == "Total Memory":
                        if sensor_name == "Memory Used":
                            memory.used = value
                        elif sensor_name == "Memory Available":
                            memory.available = value

                    elif hardware_name == "Virtual Memory":
                        if sensor_name == "Memory Used":
                            memory.virtual_used = value
                        elif sensor_name == "Memory Available":
                            memory.virtual_available = value


                # -- DIMM Temperature -- #
                case "lhm_memory_temperature_celsius":
                    if sensor_name.startswith("DIMM"):
                        memory.dimms[sensor_name] = value

        return memory


    def _normalize_gpu_nvidia(self, gpu_metrics: list[Metric]) -> GpuHardware:
        gpu = GpuHardware()

        for metric in gpu_metrics:

            sensor_name = metric.labels.get("sensorName")
            if sensor_name is None:
                continue

            value = metric.value

            match metric.name:

                # -- Temperature
                case "lhm_gpunvidia_temperature_celsius":
                    if sensor_name == "GPU Core":
                        gpu.core_temp = value
                    elif sensor_name == "GPU Memory Junction":
                        gpu.memory_junction_temp = value


                # -- Load (%) -- #
                case "lhm_gpunvidia_load_percent":
                    if sensor_name == "GPU Core":
                        gpu.core_load = value
                    elif sensor_name == "GPU Memory":
                        gpu.memory_load = value
                    elif sensor_name == "GPU Memory Controller":
                        gpu.memory_controller_load = value
                    elif sensor_name == "D3D 3D":
                        gpu.d3d_3d_load = value


                # -- Power -- #
                case "lhm_gpunvidia_power_watts":
                    if sensor_name == "GPU Package":
                        gpu.power = value


                # -- Clock Speed -- #
                case "lhm_gpunvidia_clock_hertz":
                    if sensor_name == "GPU Core":
                        gpu.core_clock = value
                    elif sensor_name == "GPU Memory":
                        gpu.memory_clock = value


                # -- Bytes Usage -- #
                case "lhm_gpunvidia_smalldata_bytes":
                    if sensor_name == "GPU Memory Used":
                        gpu.memory_used = value
                    elif sensor_name == "GPU Memory Free":
                        gpu.memory_free = value
                    elif sensor_name == "GPU Memory Total":
                        gpu.memory_total = value
                    
                    elif sensor_name == "D3D Dedicated Memory Used":
                        gpu.d3d_dedicated_memory_used = value
                    elif sensor_name == "D3D Shared Memory Used":
                        gpu.d3d_shared_memory_used = value


                # -- Throughput -- #
                case "lhm_gpunvidia_throughput_bytes_per_second":
                    if sensor_name == "GPU PCIe Rx":
                        gpu.pcie_rx = value
                    elif sensor_name == "GPU PCIe Tx":
                        gpu.pcie_tx = value


                # -- Fan RPM -- #
                case "lhm_gpunvidia_fan_rpm":
                    fan_index = self._get_fan_index(sensor_name, 2)
                    if fan_index is None:
                        continue

                    fan = self._get_fan_gpu(fan_index, gpu)
                    fan.rpm = value


                # -- Fan Control -- #
                case "lhm_gpunvidia_control_percent":
                    fan_index = self._get_core_index(sensor_name, 2)
                    if fan_index is None:
                        continue

                    fan = self._get_fan_gpu(fan_index, gpu)
                    fan.control = value

        return gpu


    def _normalize_storage(self, storage_metrics: list[Metric]) -> StorageHardware:
        storage = StorageHardware()

        for metric in storage_metrics:

            hardware_id = metric.labels.get("hardwareId", "")
            sensor_name = metric.labels.get("sensorName")
            hardware_name = metric.labels.get("hardwareName")

            if sensor_name is None or hardware_name is None or hardware_id is None:
                continue

            value = metric.value
            device = self._get_storage_device(hardware_name, storage)

            match metric.name:

                # -- Temperature -- #
                case "lhm_storage_temperature_celsius":
                    if sensor_name in ("Composite Temperature", "Temperature"):
                        device.temperature = value

                
                case "lhm_storage_load_percent":
                    if sensor_name == "Used Space":
                        device.used_space = value
                    elif sensor_name == "Read Activity":
                        device.read_activity = value
                    elif sensor_name == "Write Activity":
                        device.write_activity = value
                    elif sensor_name == "Total Activity":
                        device.total_activity = value


                case "lhm_storage_data_bytes":
                    if sensor_name == "Free Space":
                        device.free_space = value


                case "lhm_storage_throughput_bytes_per_second":
                    if sensor_name == "Read Rate":
                        device.read_rate = value
                    elif sensor_name == "Write Rate":
                        device.write_rate = value


                case "lhm_storage_level_percent":
                    if sensor_name == "Life":
                        device.life = value
                    elif sensor_name == "Percentage Used":
                        device.percentage_used = value
                    elif sensor_name == "Available Spare":
                        device.available_spare = value

        return storage

    

    def _get_core_index(self, sensor_name: str, part_index: int) -> int | None:
        parts = sensor_name.split(" ")
        if part_index >= len(parts):
            return None

        try:
            return int(parts[part_index].strip())

        except ValueError:
            return None


    def _get_core(self, index: int, cpu_object: CpuHardware) -> CpuCore:

        if index not in cpu_object.cores:
            cpu_object.cores[index] = CpuCore(index=index)

        return cpu_object.cores[index]


    def _get_fan_index(self, sensor_name: str, part_index: int) -> int | None:
        parts = sensor_name.split(" ")
        if part_index >= len(parts):
            return None

        try:
            return int(parts[part_index].strip())

        except ValueError:
            return None


    def _get_fan_motherboard(self, index: int, motherboard_object: MotherboardHardware):
        if index not in motherboard_object.fans:
            motherboard_object.fans[index] = FanHardware(index=index)

        return motherboard_object.fans[index]


    def _get_fan_gpu(self, index: int, gpu_object: GpuHardware):
        if index not in gpu_object.fans:
            gpu_object.fans[index] = FanHardware(index=index)

        return gpu_object.fans[index]


    def _get_storage_device(self, name: str, storage_object: StorageHardware) -> StorageDevice:
        if name not in storage_object.devices:
            storage_object.devices[name] = StorageDevice(name=name)
        return storage_object.devices[name]