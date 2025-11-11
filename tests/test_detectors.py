from spike_monitor.detectors import ThresholdDetector, BucketData

def test_threshold_detector():
    detector = ThresholdDetector(multiplier=2.0, min_delta=10)
    history = [BucketData(i, 45, 12, 1) for i in range(100)]
    current = BucketData(200, 100, 12, 1)
    result = detector.detect(current, history)
    assert result.is_spike is True
