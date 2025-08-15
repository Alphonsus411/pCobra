import pytest
import requests
import urllib3

from cobra.cli.cobrahub_client import CobraHubClient


@pytest.mark.timeout(5)
def test_post_request_is_not_retried(monkeypatch):
    client = CobraHubClient()
    counter = {"calls": 0}

    def fake_urlopen(self, method, url, *args, **kwargs):
        counter["calls"] += 1
        raise urllib3.exceptions.ProtocolError("boom")

    monkeypatch.setattr(
        urllib3.connectionpool.HTTPConnectionPool, "urlopen", fake_urlopen
    )

    with pytest.raises(requests.exceptions.ConnectionError):
        client.session.post("https://example.com")

    assert counter["calls"] == 1

