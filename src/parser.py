import requests
import logging
from src.models import Metric

logger = logging.getLogger(__name__)

class LibreHardwareMonitorParser:

    def __init__(self, url):
        self.url = url


    def fetch_metrics(self) -> list[str]:
        response = requests.get(
            self.url,
            timeout=5
        )

        response.raise_for_status()

        lines = response.text.splitlines()
        logger.debug("Fetched %d lines from %s", len(lines), self.url)

        return lines



    def parse_metrics(self, lines) -> list[Metric]:

        metrics: list[Metric] = []
        skipped_malformed = 0
        skipped_empty = 0

        for line in lines:
            try:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                start = line.find("{")
                end = line.rfind("}")

                if start == -1 or end == -1 or end < start:
                    skipped_malformed += 1
                    continue

                metric = line[:start].strip()
                labels_str = line[start + 1 : end]
                raw_value = line[end + 1 :].strip()

                if not metric:
                    skipped_empty += 1
                    continue

                if not raw_value:
                    skipped_malformed += 1
                    continue

                value_token = raw_value.split(None, 1)[0]
                try:
                    value = float(value_token)
                except ValueError:
                    skipped_malformed += 1
                    continue

                labels: dict = {}

                for label in labels_str.split(", "):
                    key, seperator, label_value = label.partition("=")

                    if not seperator:
                        continue

                    key = key.strip().strip('"')
                    label_value = label_value.strip().strip('"')

                    labels[key] = label_value

                metrics.append(
                    Metric(
                        name=metric,
                        labels=labels,
                        value=value,
                    )
                )
            except Exception:
                skipped_malformed += 1

        logger.debug(
            "Parsed %d metrics (skipped malformed=%d empty=%d)",
            len(metrics),
            skipped_malformed,
            skipped_empty,
        )

        return metrics
            

            
            

            

            