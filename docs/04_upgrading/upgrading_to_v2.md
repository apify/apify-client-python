---
id: upgrading-to-v2
title: Upgrading to v2
---

This page summarizes the breaking changes between Apify Python API Client v1.x and v2.0.

## Python version support

Support for Python 3.9 has been dropped. The Apify Python API Client v2.x now requires Python 3.10 or later. Make sure your environment is running a compatible version before upgrading.

## New underlying HTTP library

In v2.0, the Apify Python API client switched from using [`httpx`](https://www.python-httpx.org/) to [`impit`](https://github.com/apify/impit) as the underlying HTTP library. However, this change shouldn't have much impact on the end user.

## API method changes

Several public methods have changed their signatures or behavior.

### Removed parameters and attributes

- The `parse_response` parameter has been removed from the `HTTPClient.call()` method. This was an internal parameter that added a private attribute to the `Response` object.
- The private `_maybe_parsed_body` attribute has been removed from the `Response` object.

### KeyValueStoreClient

- The deprecated parameters `as_bytes` and `as_file` have been removed from `KeyValueStoreClient.get_record()`. Use the dedicated methods `get_record_as_bytes()` and `stream_record()` instead.

### DatasetClient

- The `unwind` parameter no longer accepts a single string value. Use a list of strings instead: `unwind=['items']` rather than `unwind='items'`.

## Module reorganization

Some modules have been restructured.

### Constants

- Deprecated constant re-exports from `consts.py` have been removed. Constants should now be imported from the [apify-shared-python](https://github.com/apify/apify-shared-python) package if needed.

### Errors

- Error classes are now accessible from the public `apify_client.errors` module. See the [API documentation](https://docs.apify.com/api/client/python/reference/class/ApifyApiError) for a complete list of available error classes.
