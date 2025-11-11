"""Alert actions."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class AlertPayload:
    event_type: str
    severity: str
    timestamp: datetime
    current_count: int
    rolling_avg: float
    message: str


class ActionBus:
    def __init__(self):
        self.actions = []
    
    def register(self, action):
        self.actions.append(action)
    
    def execute_all(self, payload):
        results = {}
        for i, action in enumerate(self.actions):
            try:
                results[f"action_{i}"] = action.execute(payload)
            except Exception as e:
                results[f"action_{i}"] = False
        return results
