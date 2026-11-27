from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from apify_client import ApifyClient, ApifyClientAsync

if TYPE_CHECKING:
    from collections.abc import Callable

_GETTERS = [
    pytest.param(lambda client: client.actor(''), id='actor'),
    pytest.param(lambda client: client.dataset(''), id='dataset'),
    pytest.param(lambda client: client.log(''), id='log'),
    pytest.param(lambda client: client.request_queue(''), id='request queue'),
    pytest.param(lambda client: client.user(''), id='user'),
    pytest.param(lambda client: client.actor('actor-id').version(''), id='actor version'),
    pytest.param(lambda client: client.actor('actor-id').version('0.1').env_var(''), id='env var'),
]


@pytest.mark.parametrize('get_client', _GETTERS)
@pytest.mark.parametrize('client_class', [ApifyClient, ApifyClientAsync])
def test_empty_resource_id_is_rejected_by_the_getter(
    client_class: type[ApifyClient | ApifyClientAsync],
    get_client: Callable[[ApifyClient | ApifyClientAsync], object],
) -> None:
    """A getter refuses an empty ID as soon as it is called."""
    client = client_class(token='test_token')

    with pytest.raises(ValueError, match='resource_id'):
        get_client(client)


@pytest.mark.parametrize('client_class', [ApifyClient, ApifyClientAsync])
@pytest.mark.parametrize('user_id', [pytest.param((), id='omitted'), pytest.param((None,), id='none')])
def test_user_without_an_id_is_the_current_user(
    client_class: type[ApifyClient | ApifyClientAsync], user_id: tuple[None, ...]
) -> None:
    """Only an omitted or `None` user ID stands for the current user."""
    client = client_class(token='test_token')

    assert client.user(*user_id).resource_id == 'me'
