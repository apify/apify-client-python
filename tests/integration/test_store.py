from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient


def test_store_list(apify_client: ApifyClient) -> None:
    actors_list = apify_client.store().list()
    assert actors_list is not None
    assert len(actors_list.items) != 0
