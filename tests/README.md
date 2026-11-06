# Tests

The tests have two levels:

- [Unit tests](#unit-tests) (`tests/unit`) are isolated from the Apify API.
- [Integration tests](#integration-tests) (`tests/integration`) call the real Apify API.

A test that calls the Apify API is an integration test. Every other test is a unit test.

## Unit tests

Unit tests are fully isolated from the real Apify API. They use mocks, fakes, or a local HTTP test server, and they need no API tokens and no network access.

### Running unit tests

```bash
uv run poe unit-tests
```

### Mocking HTTP

Mock HTTP with the `httpserver` fixture from `pytest-httpserver`:

```python
def test_example(httpserver: HTTPServer) -> None:
    httpserver.expect_request('/v2/endpoint').respond_with_json({'data': ...})
    client = ApifyClient(token='test', api_url=httpserver.url_for('/').removesuffix('/'))
    # assert client behavior
```

## Integration tests

Integration tests communicate with the real Apify API.

### Running integration tests

The tests need valid API tokens in these environment variables:

- `APIFY_TEST_USER_API_TOKEN`
- `APIFY_TEST_USER_2_API_TOKEN`, for the permission-related tests

```bash
export APIFY_TEST_USER_API_TOKEN=<your-token>
export APIFY_TEST_USER_2_API_TOKEN=<your-second-token>
uv run poe integration-tests
```

To run them against a different Apify API environment, also set `APIFY_INTEGRATION_TESTS_API_URL`.
