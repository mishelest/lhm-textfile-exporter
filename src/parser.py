import shlex
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

        for line in lines:
            
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            start = line.find("{")
            end = line.rfind("}")

            if start == -1 or end == -1 or end < start:
                logger.debug("Skipping malformed metric line: %r", line[:200])
                continue


            metric = line[:start].strip()
            labels_str = line[start + 1 : end]
            value_str = line[end + 1 : ].strip()

            if not metric or not value_str:
                logger.debug("Skipping metric line with empty name or value: %r", line[:200])
                continue


            labels: dict = {}

            for label in labels_str.split(", "):
                key, seperator, value = label.partition("=")

                if not seperator:
                    continue

                key = key.strip().strip('"')
                value = value.strip().strip('"')

                labels[key] = value

            metrics.append(
                Metric(
                    name=metric,
                    labels=labels,
                    value=value_str
                )
            )

        logger.debug("Parsed %d metrics", len(metrics))

        return metrics
            

            
            

            

            