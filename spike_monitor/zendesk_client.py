"""Zendesk API client."""

import requests


class ZendeskClient:
    def __init__(self, subdomain, email, api_token):
        self.subdomain = subdomain
        self.base_url = f"https://{subdomain}.zendesk.com/api/v2/"
        self.session = requests.Session()
        self.session.auth = (f"{email}/token", api_token)
    
    def count_new_tickets(self, start, end, **kwargs):
        """Count tickets in time range."""
        query = f"type:ticket created>={start.isoformat()}"
        response = self.session.get(
            f"{self.base_url}search/count.json",
            params={"query": query}
        )
        return response.json().get("count", 0)
