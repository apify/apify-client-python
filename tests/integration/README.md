# Integration tests

Integration tests are expected to communicate with the real Apify API.
They require valid API tokens provided via environment variables:

- `APIFY_TEST_USER_API_TOKEN`
- `APIFY_TEST_USER_2_API_TOKEN` (used for permission-related tests)

Tests that do not call the Apify API should be implemented as unit tests instead.
