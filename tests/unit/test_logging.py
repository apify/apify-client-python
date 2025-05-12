import time
from collections.abc import AsyncIterator

import httpx
import respx


from apify_client import ApifyClientAsync
from apify_client.clients import RunClientAsync




@respx.mock
async def test_redirected_logs(caplog) -> None:
    """Test that redirected logs are formatted correctly."""

    class AsyncByteStream:
        async def __aiter__(self) -> AsyncIterator[bytes]:
            for i in range(2):
                yield b"Some text"
                time.sleep(1)
            print("b")

        async def aclose(self) -> None:
            print("a")
            pass

    run_client = ApifyClientAsync(token="mocked_token", api_url='https://example.com').run(run_id="run_is_mocked")
    respx.get(url='https://example.com/v2/actor-runs/run_is_mocked').mock(
        return_value=httpx.Response(stream=AsyncByteStream(), status_code=200))
        # {'http_version': b'HTTP/1.1', 'network_stream': <httpcore._backends.anyio.AnyIOStream object at 0x7fc82543db70>, 'reason_phrase': b'OK'}
        # [(b'Date', b'Mon, 12 May 2025 13:24:41 GMT'), (b'Content-Type', b'application/json; charset=utf-8'), (b'Transfer-Encoding', b'chunked'), (b'Connection', b'keep-alive'), (b'Cache-Control', b'no-cache, no-store, must-revalidate'), (b'Pragma', b'no-cache'), (b'Expires', b'0'), (b'Access-Control-Allow-Origin', b'*'), (b'Access-Control-Allow-Headers', b'User-Agent, Content-Type, Authorization, X-Apify-Request-Origin, openai-conversation-id, openai-ephemeral-user-id'), (b'Access-Control-Allow-Methods', b'GET, POST'), (b'Access-Control-Expose-Headers', b'X-Apify-Pagination-Total, X-Apify-Pagination-Offset, X-Apify-Pagination-Desc, X-Apify-Pagination-Count, X-Apify-Pagination-Limit'), (b'Referrer-Policy', b'no-referrer'), (b'X-Robots-Tag', b'none'), (b'X-RateLimit-Limit', b'200'), (b'Location', b'https://api.apify.com/v2/actor-runs/ywNUnFFbOksQLa4mH'), (b'Vary', b'Accept-Encoding'), (b'Content-Encoding', b'gzip')]
    streamed_log = await run_client.get_streamed_log(actor_name="mocked_actor")
    async with streamed_log:
        # do some stuff
        pass

    records = caplog.get_records()
