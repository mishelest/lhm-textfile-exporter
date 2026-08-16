import time
import requests
import logging
from pathlib import Path

from src.config import Config
from src.models import HardwareMetrics, ExporterHealth

from src.parser import LibreHardwareMonitorParser
from src.classifier import Classifier
from src.normalizer import Normalizer
from src.exporter.prometheus_exporter import PrometheusExporter


logger = logging.getLogger(__name__)

class ExporterService:

    def __init__(self):

        self.config = Config()

        # setup logging
        self._setup_logging(self.config.data["logging"])
        if self.config.created_from_default:
            logger.info("Created config.yaml from config.default.yaml")

        # get exporter configurations
        exporter_cfg = self.config.data["exporter"]

        self.parser = LibreHardwareMonitorParser(self.config.data["librehardwaremonitor"]["url"])
        self.classifier = Classifier()
        self.normalizer = Normalizer()
        self.exporter = PrometheusExporter(
            output_dir=exporter_cfg.get("output_dir", "textfile_inputs"),
            output_file=exporter_cfg.get("output_file", "hardware.prom"),            
        )

        self.interval = exporter_cfg["scrape_interval_seconds"]
        self._last_metrics = HardwareMetrics()
        self._scrape_errors_total = 0
        self._last_scrape_success_timestamp = 0.0


        logger.info("Config loaded")
        logger.info("LibreHardwareMonitor URL: %s", self.config.data["librehardwaremonitor"]["url"])
        logger.info("Scrape interval: %s seconds", self.interval)
        logger.info(
            "Output file: %s",
            Path(exporter_cfg.get("output_dir", "textfile_inputs"))
            / exporter_cfg.get("output_file", "hardware.prom"),
        )

        logger.info(
            "Logging level=%s file=%s",
            self.config.data["logging"].get("level", "INFO"),
            self.config.data["logging"].get("file", "logs/exporter.log")
        )



    def _setup_logging(self, cfg: dict) -> None:

        level_name = cfg.get("level", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        log_file = Path(cfg.get("file", "logs/exporter.log"))
        log_file.parent.mkdir(parents=True, exist_ok=True)

        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

        root = logging.getLogger()
        root.setLevel(level)
        root.handlers.clear()

        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(fmt)
        root.addHandler(console)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)



    def run(self):
        while True:

            started = time.time()
            up = 0

            try:
                lines = self.parser.fetch_metrics()

                # empty / invalid response
                data_lines = [
                    line for line in lines
                    if line.strip() and not line.strip().startswith("#")
                ]
                if not data_lines:
                    raise ValueError("Empty or invalid LibreHardwareMonitor response")

                parsed_metrics = self.parser.parse_metrics(lines)
                if not parsed_metrics:
                    raise ValueError("No metrics parsed from LibreHardwareMonitor response")

                grouped_metrics = self.classifier.classify(parsed_metrics)
                normalized_metrics = self.normalizer.normalize(grouped_metrics)

                self._last_metrics = normalized_metrics
                self._last_scrape_success_timestamp = time.time()
                up = 1

            except requests.exceptions.ConnectionError:
                self._scrape_errors_total += 1
                logger.error(
                    "LibreHardwareMonitor is unreachable at %s",
                    self.parser.url,
                )

            except requests.exceptions.Timeout:
                self._scrape_errors_total += 1
                logger.error(
                    "LibreHardwareMonitor timeout at %s",
                    self.parser.url,
                )

            except requests.exceptions.HTTPError as e:
                self._scrape_errors_total += 1
                logger.error("LibreHardwareMonitor HTTP error: %s", e)

            except requests.exceptions.RequestException as e:
                self._scrape_errors_total += 1
                logger.error("LibreHardwareMonitor request failed: %s", e)

            except ValueError as e:
                self._scrape_errors_total += 1
                logger.error("%s", e)

            except Exception:
                self._scrape_errors_total += 1
                logger.exception("Scrape iteration failed")


            health = ExporterHealth(
                up=up,
                scrape_duration_seconds = time.time() - started,
                last_scrape_success_timestamp = self._last_scrape_success_timestamp,
                scrape_errors_total = float(self._scrape_errors_total),
            )


            # try to write prometheus file
            try:
                self.exporter.write(self._last_metrics)

            except Exception:
                logger.exception("Failed to write prometheus file")


            time.sleep(self.interval)