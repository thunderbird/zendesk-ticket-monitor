"""State machine."""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta


class AlertState(str, Enum):
    NORMAL = "NORMAL"
    ALERTING = "ALERTING"
    ALERTED = "ALERTED"


@dataclass
class StateContext:
    current_state: AlertState = AlertState.NORMAL
    alert_timestamp: datetime = None
    normal_bucket_count: int = 0


class StateMachine:
    def __init__(self, cooldown_buckets=3, suppress_minutes=30):
        self.cooldown_buckets = cooldown_buckets
        self.suppress_minutes = suppress_minutes
        self.context = StateContext()
    
    def process_bucket(self, is_spike, spike_count, timestamp):
        emit_alert = False
        emit_clear = False
        
        if is_spike:
            if self.context.current_state == AlertState.NORMAL:
                self.context.current_state = AlertState.ALERTED
                emit_alert = True
        else:
            if self.context.current_state == AlertState.ALERTED:
                self.context.normal_bucket_count += 1
                if self.context.normal_bucket_count >= self.cooldown_buckets:
                    emit_clear = True
                    self.context.current_state = AlertState.NORMAL
        
        return emit_alert, emit_clear
