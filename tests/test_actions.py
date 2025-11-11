from datetime import datetime
from spike_monitor.actions import ActionBus, AlertPayload

def test_action_bus():
    bus = ActionBus()
    payload = AlertPayload("ALERT", "P1", datetime.now(), 100, 45.0, "Test")
    results = bus.execute_all(payload)
    assert isinstance(results, dict)
