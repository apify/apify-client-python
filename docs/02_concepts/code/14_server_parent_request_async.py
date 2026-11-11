import os
from collections.abc import Mapping
from typing import Any

from apify_client import ApifyClientAsync


async def search_other_actor(incoming_headers: Mapping[str, str]) -> Any:
    # Call this while handling a request your Server Actor received, with the headers
    # of that incoming request. The client uses the token of the Actor's run.
    apify_client = ApifyClientAsync(os.environ['APIFY_TOKEN'])
    other_server_client = apify_client.actor('username/other-actor').server()

    # The outgoing request is charged at the pricing tier of the incoming one.
    response = await other_server_client.request(
        '/search',
        params={'q': 'apify'},
        parent_request_id=incoming_headers['X-Actor-Request-ID'],
    )
    return response.json()
