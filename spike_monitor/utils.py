"""Utility functions."""

from datetime import datetime


def format_zendesk_url(subdomain, start, end):
    base = f"https://{subdomain}.zendesk.com/agent/search/1"
    query = f"type:ticket created>={start.strftime('%Y-%m-%d')}"
    return f"{base}?q={query}"
