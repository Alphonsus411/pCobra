import pytest

from cobra.cli.cobrahub_client import CobraHubClient


@pytest.mark.timeout(5)
def test_retry_config_allows_post():
    client = CobraHubClient()
    adapter = client.session.get_adapter("https://")
    assert "POST" in adapter.max_retries.allowed_methods
    assert adapter.max_retries.total == CobraHubClient.MAX_RETRIES
