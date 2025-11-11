from spike_monitor.config import Config

def test_config_loads():
    config = Config(
        zendesk={"subdomain": "test", "email": "test@test.com", "api_token": "token"},
        query={"bucket_minutes": 5},
        detection={"mode": "threshold"}
    )
    assert config.zendesk.subdomain == "test"
