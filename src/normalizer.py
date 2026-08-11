from src.models import Metric, HardwareMetrics, CpuCore, CpuHardware



class Normalizer:

    def normalize(self, metrics: dict[str, list[Metric]]) -> HardwareMetrics:

        hardware_metrics = HardwareMetrics()

        hardware_metrics.cpu = self._normalize_cpu(metrics.get("cpu", []))


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
