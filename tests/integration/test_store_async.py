from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync


async def test_store_list(apify_client_async: ApifyClientAsync) -> None:
    actors_list = await apify_client_async.store().list()
    assert actors_list is not None
    assert len(actors_list.items) != 0
