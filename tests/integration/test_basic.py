from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apify_client import ApifyClient, ApifyClientAsync


class TestBasicSync:
    def test_basic(self, apify_client: ApifyClient) -> None:
        me = apify_client.user('me').get()
        assert me is not None
        assert me.get('id') is not None
        assert me.get('username') is not None


class TestBasicAsync:
    async def test_basic(self, apify_client_async: ApifyClientAsync) -> None:
        me = await apify_client_async.user('me').get()
        assert me is not None
        assert me.get('id') is not None
        assert me.get('username') is not None
