# Unit tests

Unit tests must be fully isolated from the real Apify API.
Use mocks, fakes, or a local HTTP test server.

They must not require:

- production or test API tokens
- network access at all

Any test that calls the Apify API belongs to integration tests.

Mock HTTP with the `httpserver` fixture from `pytest-httpserver`:

```python
def test_example(httpserver: HTTPServer) -> None:
    httpserver.expect_request('/v2/endpoint').respond_with_json({'data': ...})
    client = ApifyClient(token='test', api_url=httpserver.url_for('/').removesuffix('/'))
    # assert client behavior
```
