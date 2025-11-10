"""Ticket Spike Monitor - Zero-ops spike detection for Zendesk."""

__version__ = "1.0.0"
__all__ = ["SpikeMonitor", "Config"]

from spike_monitor.cli import SpikeMonitor
from spike_monitor.config import Config
