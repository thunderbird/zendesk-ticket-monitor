from datetime import datetime
from spike_monitor.state import StateMachine, AlertState

def test_state_machine():
    sm = StateMachine()
    emit_alert, _ = sm.process_bucket(True, 100, datetime.now())
    assert emit_alert is True
    assert sm.context.current_state == AlertState.ALERTED
