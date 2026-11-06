# Tests

The tests have two levels:

- [Unit tests](#unit-tests) (`tests/unit`) are isolated from the Apify API and need no credentials or network access.
- [Integration tests](#integration-tests) (`tests/integration`) call the real Apify API.

A test that calls the Apify API is an integration test. Every other test is a unit test. Helpers shared by both levels live in `tests/_utils.py`.

## Unit tests

Unit tests are fully isolated from the real Apify API. They use mocks, fakes, or a local HTTP server, so they need no API tokens and no network access.

### Running unit tests

```bash
uv run poe unit-tests
```

To run a single test:

```bash
uv run pytest tests/unit/<path>.py::<test_name>
```

### Unit test fixtures

- `httpserver`: a local HTTP server (from `pytest-httpserver`) on `127.0.0.1`, shared by the session and cleared after each test.
- `sync_client` and `async_client`: an `ApifyClient` and an `ApifyClientAsync` pointed at `httpserver`.
- `http_client_classes`: runs the test once per built-in HTTP transport (`impit` and `httpx2`) and makes it the default transport the clients construct. A module opts all its tests in with `pytestmark = pytest.mark.usefixtures('http_client_classes')`. Tests that construct a transport directly use `http_client_class` and `http_client_async_class`.

### Mocking the API

Register the expected requests on `httpserver` and point the client at it:

```python
def test_example(httpserver: HTTPServer, sync_client: ApifyClient) -> None:
    httpserver.expect_request('/v2/endpoint').respond_with_json({'data': ...})
    # call sync_client and assert its behavior
```

## Integration tests

Integration tests communicate with the real Apify API.

### Running integration tests

The tests need API tokens of two test users:

- `APIFY_TEST_USER_API_TOKEN`: the main test user.
- `APIFY_TEST_USER_2_API_TOKEN`: a second user, who owns the storages for the permission tests.

```bash
export APIFY_TEST_USER_API_TOKEN=<your-token>
export APIFY_TEST_USER_2_API_TOKEN=<your-second-token>
uv run poe integration-tests
```

To run them against a different Apify API environment, also set `APIFY_INTEGRATION_TESTS_API_URL`.

### Integration test fixtures

- `client`: an `ApifyClient` or `ApifyClientAsync` for the main test user. Each test that uses it runs four times, once for each combination of sync or async client and `impit` or `httpx2` transport.
- `is_async`: `True` when the test runs with the async client.
- `test_dataset_of_another_user` and `test_kvs_of_another_user`: a dataset and a key-value store owned by the second user, with known content and the signatures for accessing it.

### Writing integration tests

One test function covers both clients. Wrap each client call in `maybe_await`, which awaits the result of the async client and returns the result of the sync one as is:

```python
async def test_dataset_get_or_create(client: ApifyClient | ApifyClientAsync) -> None:
    """A dataset created by name can be retrieved by its ID."""
    dataset_name = get_random_resource_name('dataset')
    dataset = await maybe_await(client.datasets().get_or_create(name=dataset_name))
    dataset_client = client.dataset(dataset.id)

    try:
        retrieved = await maybe_await(dataset_client.get())
        assert retrieved is not None
        assert retrieved.name == dataset_name
    finally:
        await maybe_await(dataset_client.delete())
```

- Name the resources a test creates with `get_random_resource_name`, so parallel test runs don't collide, and delete them in a `finally` block.
- The API is eventually consistent, so a resource you just created or changed may take a moment to show up. Poll with `poll_until_condition`, or with `collect_iterate_until_present` for `iterate()` listings, instead of sleeping for a fixed time. Where a test has to sleep, use `maybe_sleep`, which blocks only for the sync client.
