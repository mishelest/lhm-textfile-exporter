from dataclasses import dataclass, field


@dataclass(slots=True)
class Metric:
    name:   str
    value:  str
    labels: dict
