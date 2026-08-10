from src.models import Metric

class Classifier:

    def classify(self, parsed_metrics: list[Metric]) -> dict[str, list[Metric]]:

        metrics: dict[str, list[Metric]] = {}

        for metric in parsed_metrics:

            parts = metric.name.split("_")
            if len (parts) < 3:
                continue

            group = parts[1] # skip 'lhm'

            metrics.setdefault(group, []).append(metric)

        return metrics