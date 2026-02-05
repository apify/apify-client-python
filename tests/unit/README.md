# Unit tests

Unit tests must be fully isolated from the real Apify API.
Use mocks, fakes, or a local HTTP test server.

They must not require:

- production or test API tokens
- network access at all

Any test that calls the Apify API belong to integration tests.
