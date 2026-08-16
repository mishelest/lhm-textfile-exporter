import logging
from src.models import Metric

logger = logging.getLogger(__name__)

class Classifier:

    def classify(self, parsed_metrics: list[Metric]) -> dict[str, list[Metric]]:

        metrics: dict[str, list[Metric]] = {}

        for metric in parsed_metrics:

            parts = metric.name.split("_")
            if len (parts) < 3:
                logger.debug("Skipped unclassified metric %s", metric.name)
                continue

            group = parts[1] # skip 'lhm'

            metrics.setdefault(group, []).append(metric)

        logger.debug(
            "Classified groups %s",
            {group: len(items) for group, items in metrics.items()},
        )

        return metrics