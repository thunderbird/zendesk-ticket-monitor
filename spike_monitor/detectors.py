"""Detection algorithms."""

import math
from dataclasses import dataclass


@dataclass
class BucketData:
    timestamp: float
    count: int
    hour_of_day: int
    day_of_week: int


@dataclass
class DetectionResult:
    is_spike: bool
    current_count: int
    rolling_avg: float
    rolling_stddev: float
    threshold_value: float
    message: str = ""


class ThresholdDetector:
    def __init__(self, multiplier=2.0, min_delta=10):
        self.multiplier = multiplier
        self.min_delta = min_delta
    
    def detect(self, current, history):
        if not history:
            return DetectionResult(False, current.count, 0, 0, 0, "No history")
        
        counts = [b.count for b in history]
        avg = sum(counts) / len(counts)
        variance = sum((x - avg) ** 2 for x in counts) / len(counts)
        stddev = math.sqrt(variance)
        threshold = max(self.min_delta, avg * self.multiplier)
        
        return DetectionResult(
            is_spike=current.count >= threshold,
            current_count=current.count,
            rolling_avg=avg,
            rolling_stddev=stddev,
            threshold_value=threshold,
            message=f"Current: {current.count}, Threshold: {threshold}"
        )
