from spike_monitor.zendesk_client import ZendeskClient

def test_client_init():
    client = ZendeskClient("test", "test@test.com", "token")
    assert client.subdomain == "test"
