from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
from werkzeug import Response

from apify_client import ApifyClient, ApifyClientAsync
from apify_client._models import Request
from apify_client._utils.crypto import create_hmac_signature

if TYPE_CHECKING:
    from pytest_httpserver import HTTPServer
    from werkzeug import Request as WerkzeugRequest

_KVS_ID = 'test_kvs_id'
_QUEUE_ID = 'test_queue_id'
_PUBLIC_URL = 'https://public.example.com'

# Caller-supplied segments that must not be able to steer the request off its endpoint, plus an ordinary
# value that has to survive untouched. Each case is (raw value, the percent-encoded form it has to arrive as).
_SEGMENT_CASES = [
    pytest.param('../../actor-runs/VICTIM/abort', '..%2F..%2Factor-runs%2FVICTIM%2Fabort', id='traversal'),
    pytest.param('foo?injected=1', 'foo%3Finjected%3D1', id='query injection'),
    pytest.param('foo#frag', 'foo%23frag', id='fragment'),
    pytest.param('a/b', 'a%2Fb', id='slash'),
    pytest.param('a b', 'a%20b', id='space'),
    pytest.param('INPUT.json', 'INPUT.json', id='ordinary value'),
]

# The same for resource IDs, which `to_safe_id` first turns into their single-segment form: a `username/name`
# reference becomes `username~name`, and the tilde must survive the encoding untouched.
_RESOURCE_ID_CASES = [
    pytest.param('../../actor-runs/VICTIM/abort', '..~..~actor-runs~VICTIM~abort', id='traversal'),
    pytest.param('foo?injected=1', 'foo%3Finjected%3D1', id='query injection'),
    pytest.param('foo#frag', 'foo%23frag', id='fragment'),
    pytest.param('a b', 'a%20b', id='space'),
    pytest.param('username/name', 'username~name', id='username-prefixed ID'),
]

_DEGENERATE_SEGMENTS = [
    pytest.param('', id='empty'),
    pytest.param('.', id='current'),
    pytest.param('..', id='parent'),
]


@pytest.fixture
def api_url(httpserver: HTTPServer) -> str:
    """The base URL of the mock server, in the form the clients expect."""
    return httpserver.url_for('/').removesuffix('/')


@pytest.fixture
def kvs_signing_key(httpserver: HTTPServer) -> str:
    """Answer the store metadata call with a URL signing key, and return that key."""
    signing_key = 'test_signing_key'
    httpserver.expect_request(f'/v2/key-value-stores/{_KVS_ID}', method='GET').respond_with_json(
        {
            'data': {
                'id': _KVS_ID,
                'name': 'name',
                'userId': 'user_id',
                'createdAt': '2025-09-11T08:48:51.806Z',
                'modifiedAt': '2025-09-11T08:48:51.806Z',
                'accessedAt': '2025-09-11T08:48:51.806Z',
                'stats': {'readCount': 0, 'writeCount': 0, 'deleteCount': 0, 'listCount': 0, 'storageBytes': 0},
                'generalAccess': 'FOLLOW_USER_SETTING',
                'urlSigningSecretKey': signing_key,
            }
        }
    )
    return signing_key


@pytest.fixture
def captured_targets(httpserver: HTTPServer) -> list[str]:
    """Answer any GET with a 404 and collect the raw request targets the client sent.

    The raw target is read from `RAW_URI` rather than from `Request.path`, which is already percent-decoded and
    so cannot tell an encoded separator apart from a literal one.
    """
    targets: list[str] = []

    def capture_request(request: WerkzeugRequest) -> Response:
        targets.append(request.environ['RAW_URI'])
        return Response(status=404, response='{"error": {"type": "record-not-found"}}')

    httpserver.expect_request(re.compile('.*'), method='GET').respond_with_handler(capture_request)
    return targets


@pytest.fixture
def captured_delete_targets(httpserver: HTTPServer) -> list[str]:
    """Answer any DELETE with a 204 and collect the raw request targets the client sent."""
    targets: list[str] = []

    def capture_request(request: WerkzeugRequest) -> Response:
        targets.append(request.environ['RAW_URI'])
        return Response(status=204)

    httpserver.expect_request(re.compile('.*'), method='DELETE').respond_with_handler(capture_request)
    return targets


@pytest.mark.parametrize(('key', 'encoded_key'), _SEGMENT_CASES)
def test_get_record_encodes_key_into_a_single_path_segment_sync(
    *,
    api_url: str,
    captured_targets: list[str],
    key: str,
    encoded_key: str,
) -> None:
    """A record key cannot escape its path segment, inject query params, or be truncated by a fragment."""
    client = ApifyClient(token='test_token', api_url=api_url)

    assert client.key_value_store(_KVS_ID).get_record(key) is None

    assert captured_targets == [f'/v2/key-value-stores/{_KVS_ID}/records/{encoded_key}?attachment=true']


@pytest.mark.parametrize(('key', 'encoded_key'), _SEGMENT_CASES)
async def test_get_record_encodes_key_into_a_single_path_segment_async(
    *,
    api_url: str,
    captured_targets: list[str],
    key: str,
    encoded_key: str,
) -> None:
    """A record key cannot escape its path segment, inject query params, or be truncated by a fragment."""
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    assert await client.key_value_store(_KVS_ID).get_record(key) is None

    assert captured_targets == [f'/v2/key-value-stores/{_KVS_ID}/records/{encoded_key}?attachment=true']


@pytest.mark.parametrize(('key', 'encoded_key'), _SEGMENT_CASES)
def test_delete_record_encodes_key_into_a_single_path_segment_sync(
    *,
    api_url: str,
    captured_delete_targets: list[str],
    key: str,
    encoded_key: str,
) -> None:
    """A key cannot steer a record delete at another endpoint, where the same verb removes the whole store."""
    client = ApifyClient(token='test_token', api_url=api_url)

    client.key_value_store(_KVS_ID).delete_record(key)

    assert captured_delete_targets == [f'/v2/key-value-stores/{_KVS_ID}/records/{encoded_key}']


@pytest.mark.parametrize(('key', 'encoded_key'), _SEGMENT_CASES)
async def test_delete_record_encodes_key_into_a_single_path_segment_async(
    *,
    api_url: str,
    captured_delete_targets: list[str],
    key: str,
    encoded_key: str,
) -> None:
    """A key cannot steer a record delete at another endpoint, where the same verb removes the whole store."""
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    await client.key_value_store(_KVS_ID).delete_record(key)

    assert captured_delete_targets == [f'/v2/key-value-stores/{_KVS_ID}/records/{encoded_key}']


@pytest.mark.parametrize(('request_id', 'encoded_request_id'), _SEGMENT_CASES)
def test_get_request_encodes_request_id_into_a_single_path_segment_sync(
    *,
    api_url: str,
    captured_targets: list[str],
    request_id: str,
    encoded_request_id: str,
) -> None:
    """A request ID cannot escape the request-queue namespace it belongs to."""
    client = ApifyClient(token='test_token', api_url=api_url)

    assert client.request_queue(_QUEUE_ID).get_request(request_id) is None

    assert captured_targets == [f'/v2/request-queues/{_QUEUE_ID}/requests/{encoded_request_id}']


@pytest.mark.parametrize(('request_id', 'encoded_request_id'), _SEGMENT_CASES)
async def test_get_request_encodes_request_id_into_a_single_path_segment_async(
    *,
    api_url: str,
    captured_targets: list[str],
    request_id: str,
    encoded_request_id: str,
) -> None:
    """A request ID cannot escape the request-queue namespace it belongs to."""
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    assert await client.request_queue(_QUEUE_ID).get_request(request_id) is None

    assert captured_targets == [f'/v2/request-queues/{_QUEUE_ID}/requests/{encoded_request_id}']


@pytest.mark.parametrize(('request_id', 'encoded_request_id'), _SEGMENT_CASES)
def test_delete_request_lock_encodes_request_id_into_a_single_path_segment_sync(
    *,
    api_url: str,
    captured_delete_targets: list[str],
    request_id: str,
    encoded_request_id: str,
) -> None:
    """The encoding also covers a path that continues past the caller-supplied segment."""
    client = ApifyClient(token='test_token', api_url=api_url)

    client.request_queue(_QUEUE_ID).delete_request_lock(request_id)

    assert captured_delete_targets == [f'/v2/request-queues/{_QUEUE_ID}/requests/{encoded_request_id}/lock']


@pytest.mark.parametrize(('request_id', 'encoded_request_id'), _SEGMENT_CASES)
async def test_delete_request_lock_encodes_request_id_into_a_single_path_segment_async(
    *,
    api_url: str,
    captured_delete_targets: list[str],
    request_id: str,
    encoded_request_id: str,
) -> None:
    """The encoding also covers a path that continues past the caller-supplied segment."""
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    await client.request_queue(_QUEUE_ID).delete_request_lock(request_id)

    assert captured_delete_targets == [f'/v2/request-queues/{_QUEUE_ID}/requests/{encoded_request_id}/lock']


@pytest.mark.parametrize('key', _DEGENERATE_SEGMENTS)
def test_degenerate_key_is_rejected_before_the_request_sync(
    *,
    api_url: str,
    captured_targets: list[str],
    key: str,
) -> None:
    """An empty or dot key survives any encoding and lands on the store endpoint, so it is refused instead."""
    client = ApifyClient(token='test_token', api_url=api_url)

    with pytest.raises(ValueError, match='cannot be used as a URL path segment'):
        client.key_value_store(_KVS_ID).get_record(key)

    assert captured_targets == []


@pytest.mark.parametrize('key', _DEGENERATE_SEGMENTS)
async def test_degenerate_key_is_rejected_before_the_request_async(
    *,
    api_url: str,
    captured_targets: list[str],
    key: str,
) -> None:
    """An empty or dot key survives any encoding and lands on the store endpoint, so it is refused instead."""
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    with pytest.raises(ValueError, match='cannot be used as a URL path segment'):
        await client.key_value_store(_KVS_ID).get_record(key)

    assert captured_targets == []


@pytest.mark.parametrize('key', _DEGENERATE_SEGMENTS)
def test_degenerate_key_is_rejected_before_deleting_a_record_sync(
    *,
    api_url: str,
    captured_delete_targets: list[str],
    key: str,
) -> None:
    """A dot key would turn a record delete into a delete of the whole store, so it never reaches the wire."""
    client = ApifyClient(token='test_token', api_url=api_url)

    with pytest.raises(ValueError, match='cannot be used as a URL path segment'):
        client.key_value_store(_KVS_ID).delete_record(key)

    assert captured_delete_targets == []


@pytest.mark.parametrize('key', _DEGENERATE_SEGMENTS)
async def test_degenerate_key_is_rejected_before_deleting_a_record_async(
    *,
    api_url: str,
    captured_delete_targets: list[str],
    key: str,
) -> None:
    """A dot key would turn a record delete into a delete of the whole store, so it never reaches the wire."""
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    with pytest.raises(ValueError, match='cannot be used as a URL path segment'):
        await client.key_value_store(_KVS_ID).delete_record(key)

    assert captured_delete_targets == []


@pytest.mark.parametrize(('key', 'encoded_key'), _SEGMENT_CASES)
def test_record_public_url_encodes_key_into_a_single_path_segment_sync(
    *,
    api_url: str,
    captured_targets: list[str],
    key: str,
    encoded_key: str,
) -> None:
    """The shareable record URL carries the key encoded, so it addresses the record and nothing else."""
    client = ApifyClient(token='test_token', api_url=api_url, api_public_url=_PUBLIC_URL)

    public_url = client.key_value_store(_KVS_ID).get_record_public_url(key)

    assert captured_targets == [f'/v2/key-value-stores/{_KVS_ID}']
    assert public_url == f'{_PUBLIC_URL}/v2/key-value-stores/{_KVS_ID}/records/{encoded_key}'


@pytest.mark.parametrize(('key', 'encoded_key'), _SEGMENT_CASES)
async def test_record_public_url_encodes_key_into_a_single_path_segment_async(
    *,
    api_url: str,
    captured_targets: list[str],
    key: str,
    encoded_key: str,
) -> None:
    """The shareable record URL carries the key encoded, so it addresses the record and nothing else."""
    client = ApifyClientAsync(token='test_token', api_url=api_url, api_public_url=_PUBLIC_URL)

    public_url = await client.key_value_store(_KVS_ID).get_record_public_url(key)

    assert captured_targets == [f'/v2/key-value-stores/{_KVS_ID}']
    assert public_url == f'{_PUBLIC_URL}/v2/key-value-stores/{_KVS_ID}/records/{encoded_key}'


def test_record_public_url_signs_the_raw_key_sync(*, api_url: str, kvs_signing_key: str) -> None:
    """The signature covers the raw key the API decodes the path back into, not the encoded form in the path."""
    client = ApifyClient(token='test_token', api_url=api_url, api_public_url=_PUBLIC_URL)

    public_url = client.key_value_store(_KVS_ID).get_record_public_url('a/b')

    signature = create_hmac_signature(kvs_signing_key, 'a/b')
    assert public_url == f'{_PUBLIC_URL}/v2/key-value-stores/{_KVS_ID}/records/a%2Fb?signature={signature}'


async def test_record_public_url_signs_the_raw_key_async(*, api_url: str, kvs_signing_key: str) -> None:
    """The signature covers the raw key the API decodes the path back into, not the encoded form in the path."""
    client = ApifyClientAsync(token='test_token', api_url=api_url, api_public_url=_PUBLIC_URL)

    public_url = await client.key_value_store(_KVS_ID).get_record_public_url('a/b')

    signature = create_hmac_signature(kvs_signing_key, 'a/b')
    assert public_url == f'{_PUBLIC_URL}/v2/key-value-stores/{_KVS_ID}/records/a%2Fb?signature={signature}'


@pytest.mark.parametrize('key', _DEGENERATE_SEGMENTS)
def test_degenerate_key_is_rejected_before_the_public_url_metadata_call_sync(
    *,
    api_url: str,
    captured_targets: list[str],
    key: str,
) -> None:
    """A key that cannot be carried in a path segment is refused without spending an authenticated request."""
    client = ApifyClient(token='test_token', api_url=api_url, api_public_url=_PUBLIC_URL)

    with pytest.raises(ValueError, match='cannot be used as a URL path segment'):
        client.key_value_store(_KVS_ID).get_record_public_url(key)

    assert captured_targets == []


@pytest.mark.parametrize('key', _DEGENERATE_SEGMENTS)
async def test_degenerate_key_is_rejected_before_the_public_url_metadata_call_async(
    *,
    api_url: str,
    captured_targets: list[str],
    key: str,
) -> None:
    """A key that cannot be carried in a path segment is refused without spending an authenticated request."""
    client = ApifyClientAsync(token='test_token', api_url=api_url, api_public_url=_PUBLIC_URL)

    with pytest.raises(ValueError, match='cannot be used as a URL path segment'):
        await client.key_value_store(_KVS_ID).get_record_public_url(key)

    assert captured_targets == []


@pytest.mark.parametrize(('resource_id', 'encoded_resource_id'), _RESOURCE_ID_CASES)
def test_resource_id_is_encoded_into_a_single_path_segment(
    *,
    api_url: str,
    captured_targets: list[str],
    resource_id: str,
    encoded_resource_id: str,
) -> None:
    """A resource ID cannot inject query parameters, truncate the URL at a fragment, or escape the path."""
    client = ApifyClient(token='test_token', api_url=api_url)

    assert client.dataset(resource_id).get() is None

    assert captured_targets == [f'/v2/datasets/{encoded_resource_id}']


@pytest.mark.parametrize('resource_id', _DEGENERATE_SEGMENTS)
def test_degenerate_resource_id_is_rejected_before_the_request(
    *,
    api_url: str,
    captured_targets: list[str],
    resource_id: str,
) -> None:
    """An empty or dot resource ID would address the whole collection, so it is refused instead."""
    client = ApifyClient(token='test_token', api_url=api_url)

    with pytest.raises(ValueError, match='cannot be used as a URL path segment'):
        client.dataset(resource_id).get()

    assert captured_targets == []


def test_update_request_without_an_id_is_rejected_sync(*, api_url: str) -> None:
    """A request carrying no ID cannot address a queue record, so the update is refused before it is sent."""
    client = ApifyClient(token='test_token', api_url=api_url)

    with pytest.raises(ValueError, match='must have an ID'):
        client.request_queue(_QUEUE_ID).update_request(
            Request(url='https://example.com', unique_key='https://example.com')
        )


async def test_update_request_without_an_id_is_rejected_async(*, api_url: str) -> None:
    """A request carrying no ID cannot address a queue record, so the update is refused before it is sent."""
    client = ApifyClientAsync(token='test_token', api_url=api_url)

    with pytest.raises(ValueError, match='must have an ID'):
        await client.request_queue(_QUEUE_ID).update_request(
            Request(url='https://example.com', unique_key='https://example.com')
        )
