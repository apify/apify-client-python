from __future__ import annotations

from typing import TYPE_CHECKING

from apify_client._models import UserPrivateInfo, UserPublicInfo

if TYPE_CHECKING:
    from apify_client import ApifyClientAsync


async def test_apify_client(apify_client_async: ApifyClientAsync) -> None:
    user_client = apify_client_async.user('me')
    me = await user_client.get()
    assert isinstance(me, (UserPrivateInfo, UserPublicInfo))
    assert me.username is not None
