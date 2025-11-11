import pytest
from spike_monitor.config import Config

@pytest.fixture
def sample_config():
    return Config(
        zendesk={"subdomain": "test", "email": "test@test.com", "api_token": "token"},
        query={"bucket_minutes": 5},
        detection={"mode": "threshold"}
    )
