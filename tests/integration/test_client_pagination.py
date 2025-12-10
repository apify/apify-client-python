import pytest

from apify_client import ApifyClientAsync


@pytest.mark.parametrize(
    'factory_name',
    [
        'actors',
        'datasets',
    ],
)
async def test_client_list_iterable_total_count(apify_client_async: ApifyClientAsync, factory_name: str) -> None:
    """Basic test of client list methods on real API.

    More detailed tests are in unit tets.
    """
    client = getattr(apify_client_async, factory_name)()
    list_response = await client.list()
    all_items = [item async for item in client.list()]
    assert len(all_items) == list_response.total
