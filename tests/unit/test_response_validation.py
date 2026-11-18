from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from pydantic import ValidationError

from apify_client._models import UserPublicInfo
from apify_client.errors import ApifyClientError, ResponseValidationError

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_httpserver import HTTPServer

    from apify_client import ApifyClient, ApifyClientAsync

pytestmark = pytest.mark.usefixtures('http_client_classes')

# A body with the response envelope whose `data` fits none of the models. The terminal `status` lets `wait_for_finish`
# stop polling.
_MISMATCHED_BODY = {'data': {'status': 'SUCCEEDED', 'unexpected': 'shape'}}

_SYNC_CASES = [
    pytest.param('/v2/datasets/ds-1', 'GET', lambda c: c.dataset('ds-1').get(), id='single_get'),
    pytest.param('/v2/datasets', 'GET', lambda c: c.datasets().list(), id='collection_list'),
    pytest.param('/v2/datasets', 'POST', lambda c: c.datasets().get_or_create(), id='collection_get_or_create'),
    pytest.param('/v2/datasets/ds-1', 'PUT', lambda c: c.dataset('ds-1').update(name='x'), id='single_update'),
    pytest.param('/v2/actor-runs/run-1', 'GET', lambda c: c.run('run-1').wait_for_finish(), id='wait_for_finish'),
]

_ASYNC_CASES = [
    pytest.param('/v2/datasets/ds-1', 'GET', lambda c: c.dataset('ds-1').get(), id='single_get'),
    pytest.param('/v2/datasets', 'GET', lambda c: c.datasets().list(), id='collection_list'),
    pytest.param('/v2/datasets', 'POST', lambda c: c.datasets().get_or_create(), id='collection_get_or_create'),
    pytest.param('/v2/datasets/ds-1', 'PUT', lambda c: c.dataset('ds-1').update(name='x'), id='single_update'),
    pytest.param('/v2/actor-runs/run-1', 'GET', lambda c: c.run('run-1').wait_for_finish(), id='wait_for_finish'),
]


def _assert_response_validation_error(error: ResponseValidationError, *, path: str, method: str) -> None:
    assert isinstance(error, ApifyClientError)
    assert isinstance(error, ValidationError)
    assert isinstance(error, ValueError)
    assert error.method == method
    assert error.url is not None
    assert error.url.endswith(path)
    assert error.error_count() > 0
    assert error.errors()
    assert isinstance(error.__cause__, ValidationError)
    assert f'{method} {error.url}' in str(error)


@pytest.mark.parametrize(('path', 'method', 'call'), _SYNC_CASES)
def test_mismatched_response_raises_response_validation_error(
    httpserver: HTTPServer,
    sync_client: ApifyClient,
    path: str,
    method: str,
    call: Callable[[ApifyClient], Any],
) -> None:
    """A response that does not match its model raises `ResponseValidationError` with the request details."""
    httpserver.expect_request(path, method=method).respond_with_json(_MISMATCHED_BODY)

    with pytest.raises(ResponseValidationError) as exc_info:
        call(sync_client)

    _assert_response_validation_error(exc_info.value, path=path, method=method)


@pytest.mark.parametrize(('path', 'method', 'call'), _ASYNC_CASES)
async def test_mismatched_response_raises_response_validation_error_async(
    httpserver: HTTPServer,
    async_client: ApifyClientAsync,
    path: str,
    method: str,
    call: Callable[[ApifyClientAsync], Any],
) -> None:
    """A response that does not match its model raises `ResponseValidationError` with the request details."""
    httpserver.expect_request(path, method=method).respond_with_json(_MISMATCHED_BODY)

    with pytest.raises(ResponseValidationError) as exc_info:
        await call(async_client)

    _assert_response_validation_error(exc_info.value, path=path, method=method)


def test_response_validation_error_url_has_no_query_string(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """The URL on the error leaves out the query parameters of the request."""
    httpserver.expect_request('/v2/datasets', method='GET').respond_with_json(_MISMATCHED_BODY)

    with pytest.raises(ResponseValidationError) as exc_info:
        sync_client.datasets().list(limit=1, desc=True)

    assert exc_info.value.url is not None
    assert '?' not in exc_info.value.url


def test_user_get_falls_back_to_public_info(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    """A user body that fits only the public model still returns the public info."""
    body = {'data': {'username': 'bob', 'email': 'not-an-email'}}
    httpserver.expect_request('/v2/users/me').respond_with_json(body)

    user = sync_client.user().get()

    assert isinstance(user, UserPublicInfo)
    assert user.username == 'bob'


def test_user_get_raises_response_validation_error_when_no_model_fits(
    httpserver: HTTPServer, sync_client: ApifyClient
) -> None:
    """A user body that fits neither the private nor the public model raises `ResponseValidationError`."""
    httpserver.expect_request('/v2/users/me').respond_with_json(_MISMATCHED_BODY)

    with pytest.raises(ResponseValidationError) as exc_info:
        sync_client.user().get()

    _assert_response_validation_error(exc_info.value, path='/v2/users/me', method='GET')


def test_invalid_request_input_still_raises_pydantic_validation_error(sync_client: ApifyClient) -> None:
    """A validation error on request input is raised as is, since no response is involved."""
    with pytest.raises(ValidationError) as exc_info:
        sync_client.actor('actor-1').update(versions=[{'unexpected': 'shape'}])

    assert not isinstance(exc_info.value, ResponseValidationError)
