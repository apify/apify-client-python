from __future__ import annotations

from typing import TYPE_CHECKING

from apify_client._models import UserPrivateInfo, UserPublicInfo

if TYPE_CHECKING:
    from apify_client import ApifyClient


def test_apify_client(apify_client: ApifyClient) -> None:
    user_client = apify_client.user('me')
    me = user_client.get()
    assert isinstance(me, (UserPrivateInfo, UserPublicInfo))
    assert me.username is not None
