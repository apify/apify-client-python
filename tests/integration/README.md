# Integration tests

Integration tests are expected to communicate with the real Apify API.
They require valid API tokens provided via environment variables:

- `APIFY_TEST_USER_API_TOKEN`
- `APIFY_TEST_USER_2_API_TOKEN` (used for permission-related tests)

To run them against a different Apify API environment, also set `APIFY_INTEGRATION_TESTS_API_URL`.

Tests that do not call the Apify API should be implemented as unit tests instead.
