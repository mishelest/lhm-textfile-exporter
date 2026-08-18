import time
import requests
import logging
from pathlib import Path

from src import __version__

from src.config import Config, resolve_under
from src.models import HardwareMetrics, ExporterHealth

from src.parser import LibreHardwareMonitorParser
from src.classifier import Classifier
from src.normalizer import Normalizer
from src.exporter.prometheus_exporter import PrometheusExporter


logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class ExporterService:

    def __init__(self, base_dir: Path | None = None):

        self.base_dir = (
            Path(base_dir).resolve()
            if base_dir is not None
            else Path(__file__).resolve().parent
        )

        self._ensure_fallback_logging()
        self.config = Config(base_dir=self.base_dir)

        # setup logging
        logging_cfg = self.config.data.get("logging") or {}
        self._setup_logging(logging_cfg)
        if self.config.created_from_default:
            logger.info("Created config.yaml from config.default.yaml")


        logger.info("lhmTF-exporter %s starting", __version__)

        # get exporter configurations
        exporter_cfg = self.config.data["exporter"]
        output_dir = resolve_under(
            self.base_dir,
            exporter_cfg.get("output_dir", "textfile_inputs"),
        )

        self.parser = LibreHardwareMonitorParser(self.config.data["librehardwaremonitor"]["url"])
        self.classifier = Classifier()
        self.normalizer = Normalizer()
        self.exporter = PrometheusExporter(
            output_dir=output_dir,
            output_file=exporter_cfg.get("output_file", "hardware.prom"),
        )

        self.interval = exporter_cfg["scrape_interval_seconds"]
        self._error_log_every = max(1, 60 // max(1, int(self.interval)))
        self._last_metrics = HardwareMetrics()
        self._scrape_errors_total = 0
        self._last_scrape_success_timestamp = 0.0
        self._logged_first_success = False
        self._consecutive_scrape_errors = 0
        self._consecutive_write_errors = 0
        self._logged_stale_write = False


        logger.info("Config loaded")
        logger.info("Base directory: %s", self.base_dir)
        logger.info("LibreHardwareMonitor URL: %s", self.config.data["librehardwaremonitor"]["url"])
        logger.info("Scrape interval: %s seconds", self.interval)
        logger.info(
            "Output file: %s",
            output_dir / exporter_cfg.get("output_file", "hardware.prom"),
        )

        logger.info(
            "Logging level=%s file=%s",
            logging.getLevelName(logging.getLogger().level),
            self._log_file,
        )



    @staticmethod
    def _ensure_fallback_logging() -> None:
        root = logging.getLogger()
        if root.handlers:
            return
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


    def _setup_logging(self, cfg: dict) -> None:

        level_name = str(cfg.get("level", "INFO")).upper()
        valid_levels = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
        }
        invalid_level = None
        if level_name not in valid_levels:
            invalid_level = level_name
            level = logging.INFO
        else:
            level = valid_levels[level_name]

        log_file = resolve_under(self.base_dir, str(cfg.get("file", "logs/exporter.log")))
        log_file.parent.mkdir(parents=True, exist_ok=True)
        self._log_file = log_file

        fmt = logging.Formatter(LOG_FORMAT)

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

        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)

        if invalid_level:
            logger.warning("Invalid logging level %r, using INFO", invalid_level)



    def _should_log_repeat(self, consecutive: int) -> bool:
        return consecutive == 1 or consecutive % self._error_log_every == 0


    def _note_scrape_failure(self) -> int:
        self._scrape_errors_total += 1
        self._consecutive_scrape_errors += 1
        return self._consecutive_scrape_errors


    def _log_scrape_error(self, message: str, *args) -> None:
        n = self._note_scrape_failure()
        if n == 1:
            logger.error(message, *args)
        elif self._should_log_repeat(n):
            formatted = message % args if args else message
            logger.error(
                "LibreHardwareMonitor still failing (%d consecutive errors): %s",
                n,
                formatted,
            )


    def _log_scrape_success(self, started: float, parsed_count: int, group_count: int) -> None:
        if self._consecutive_scrape_errors:
            logger.info(
                "LibreHardwareMonitor scrape recovered after %d error(s)",
                self._consecutive_scrape_errors,
            )
            self._consecutive_scrape_errors = 0
        elif not self._logged_first_success:
            logger.info("LibreHardwareMonitor scrape succeeded")
        self._logged_first_success = True

        logger.debug(
            "Scrape ok in %.3fs (parsed=%d, groups=%d)",
            time.time() - started,
            parsed_count,
            group_count,
        )


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

                self._log_scrape_success(
                    started,
                    len(parsed_metrics),
                    len(grouped_metrics),
                )

            except requests.exceptions.ConnectionError:
                self._log_scrape_error(
                    "LibreHardwareMonitor is unreachable at %s",
                    self.parser.url,
                )

            except requests.exceptions.Timeout:
                self._log_scrape_error(
                    "LibreHardwareMonitor timeout at %s",
                    self.parser.url,
                )

            except requests.exceptions.HTTPError as e:
                self._log_scrape_error("LibreHardwareMonitor HTTP error: %s", e)

            except requests.exceptions.RequestException as e:
                self._log_scrape_error("LibreHardwareMonitor request failed: %s", e)

            except ValueError as e:
                self._log_scrape_error("Invalid LibreHardwareMonitor payload: %s", e)

            except Exception:
                n = self._note_scrape_failure()
                if n == 1:
                    logger.exception("Scrape iteration failed")
                elif self._should_log_repeat(n):
                    logger.exception(
                        "Scrape iteration still failing (%d consecutive errors)",
                        n,
                    )


            health = ExporterHealth(
                up=up,
                scrape_duration_seconds = time.time() - started,
                last_scrape_success_timestamp = self._last_scrape_success_timestamp,
                scrape_errors_total = float(self._scrape_errors_total),
            )

            if up == 0 and self._last_scrape_success_timestamp:
                if not self._logged_stale_write:
                    logger.warning("Writing last successful samples after scrape failure")
                    self._logged_stale_write = True
                metrics_to_write = self._last_metrics
            elif up == 0:
                self._logged_stale_write = False
                metrics_to_write = HardwareMetrics()
            else:
                self._logged_stale_write = False
                metrics_to_write = self._last_metrics

            logger.debug(
                "Health up=%s duration=%.3fs errors_total=%s",
                health.up,
                health.scrape_duration_seconds,
                health.scrape_errors_total,
            )

            # try to write prometheus file
            try:
                self.exporter.write(metrics_to_write, health)
                if self._consecutive_write_errors:
                    logger.info(
                        "Prometheus textfile write recovered after %d error(s)",
                        self._consecutive_write_errors,
                    )
                    self._consecutive_write_errors = 0
                else:
                    logger.debug("Wrote Prometheus textfile")

            except Exception:
                self._consecutive_write_errors += 1
                n = self._consecutive_write_errors
                if n == 1:
                    if up:
                        write_context = "ok"
                    elif self._last_scrape_success_timestamp:
                        write_context = "failed; writing last samples"
                    else:
                        write_context = "failed; health only (up=0)"
                    logger.exception(
                        "Failed to write Prometheus textfile (scrape %s)",
                        write_context,
                    )
                elif self._should_log_repeat(n):
                    logger.exception(
                        "Prometheus textfile write still failing (%d consecutive errors)",
                        n,
                    )


            time.sleep(self.interval)
