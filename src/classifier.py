import logging
from src.models import Metric

logger = logging.getLogger(__name__)

class Classifier:

    def classify(self, parsed_metrics: list[Metric]) -> dict[str, list[Metric]]:

        metrics: dict[str, list[Metric]] = {}
        skipped_unclassified = 0

        for metric in parsed_metrics:

            parts = metric.name.split("_")
            if len (parts) < 3:
                skipped_unclassified += 1
                continue

            group = parts[1] # skip 'lhm'

            metrics.setdefault(group, []).append(metric)

        logger.debug(
            "Classified groups %s (skipped unclassified=%d)",
            {group: len(items) for group, items in metrics.items()},
            skipped_unclassified,
        )

        return metrics