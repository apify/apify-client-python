"""Unified tests for the server interface of an Actor (sync + async)."""

from __future__ import annotations

import json
import os
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from .._utils import API_URL_ENV_VAR, get_random_resource_name, maybe_await
from apify_client import ApifyClient
from apify_client._consts import DEFAULT_API_URL

if TYPE_CHECKING:
    from collections.abc import Generator

    from apify_client import ApifyClientAsync

OPENAPI_SPEC = {
    'openapi': '3.0.0',
    'info': {'title': 'Echo server', 'version': '1.0.0'},
    'paths': {'/echo': {'post': {'responses': {'200': {'description': 'The echoed request.'}}}}},
}

# A web server that answers every request, including the platform's readiness probe, with the request it received.
ECHO_SERVER_SOURCE = """
const http = require('http');

http.createServer((req, res) => {
    let body = '';
    req.on('data', (chunk) => { body += chunk; });
    req.on('end', () => {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ method: req.method, url: req.url, headers: req.headers, body }));
    });
}).listen(process.env.ACTOR_WEB_SERVER_PORT);
"""

DOCKERFILE = """
FROM node:22-alpine
COPY main.js ./
CMD ["node", "main.js"]
"""


@pytest.fixture(scope='module')
def server_actor_id(api_token: str) -> Generator[str]:
    """Create and build a Server Actor running an echo server, and delete it after the module's tests."""
    client = ApifyClient(api_token, api_url=os.getenv(API_URL_ENV_VAR) or DEFAULT_API_URL)
    actor_name = get_random_resource_name('server')
    actor_json = {
        'actorSpecification': 1,
        'name': actor_name,
        'version': '0.0',
        'usesStandbyMode': True,
        'webServerSchema': OPENAPI_SPEC,
    }
    actor = client.actors().create(
        name=actor_name,
        versions=[
            {
                'versionNumber': '0.0',
                'sourceType': 'SOURCE_FILES',
                'buildTag': 'latest',
                'sourceFiles': [
                    {'name': 'Dockerfile', 'format': 'TEXT', 'content': DOCKERFILE},
                    {'name': 'main.js', 'format': 'TEXT', 'content': ECHO_SERVER_SOURCE},
                    {'name': '.actor/actor.json', 'format': 'TEXT', 'content': json.dumps(actor_json)},
                ],
            }
        ],
        actor_standby_is_enabled=True,
        actor_standby_memory_mbytes=256,
        actor_standby_idle_timeout=timedelta(minutes=1),
    )
    actor_client = client.actor(actor.id)

    try:
        build = actor_client.build(version_number='0.0')
        finished_build = client.build(build.id).wait_for_finish(wait_duration=timedelta(minutes=5))
        assert finished_build is not None
        assert finished_build.status == 'SUCCEEDED'
        yield actor.id
    finally:
        actor_client.delete()


async def test_actor_server(client: ApifyClient | ApifyClientAsync, server_actor_id: str) -> None:
    """The server client returns the Actor's URL and OpenAPI specification, and sends requests to its server."""
    actor = await maybe_await(client.actor(server_actor_id).get())
    assert actor is not None
    actor_server_client = client.actor(server_actor_id).server()

    assert await maybe_await(actor_server_client.get_url()) == actor.standby_url
    assert await maybe_await(actor_server_client.get_openapi_spec()) == OPENAPI_SPEC

    response = await maybe_await(
        actor_server_client.request('/echo', method='POST', params={'q': 'apify'}, json={'limit': 5})
    )

    assert response.status_code == 200
    echoed = response.json()
    assert echoed['method'] == 'POST'
    assert echoed['url'] == '/echo?q=apify'
    assert json.loads(echoed['body']) == {'limit': 5}
    # The platform consumes the client's token, so it never reaches the Actor's code.
    assert 'authorization' not in echoed['headers']
