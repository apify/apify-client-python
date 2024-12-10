from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


class TestStoreCollectionSync:
    def test_list(self, apify_client: ApifyClient) -> None:
        actors_list = apify_client.store().list()
        assert actors_list is not None
        assert len(actors_list.items) != 0


class TestStoreCollectionAsync:
    async def test_list(self, apify_client_async: ApifyClientAsync) -> None:
        actors_list = await apify_client_async.store().list()
        assert actors_list is not None
        assert len(actors_list.items) != 0
