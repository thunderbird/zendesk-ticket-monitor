from spike_monitor.detectors import BucketData

def generate_baseline(count=100, avg=45):
    return [BucketData(i * 300, avg, 12, 1) for i in range(count)]
