Changelog
=========

[0.2.0](../../releases/tag/v0.2.0) - 2021-08-09
-----------------------------------------------

### Changed

- replaced `base_url` with `api_url` in the client constructor
  to enable easier passing of the API server url from environment variables availabl to actors on the Apify platform
- added the `gracefully` parameter to the "Abort run" method

### Internal changes

- changed tags for actor images with this client on Docker Hub to be aligned with the Apify SDK Node.js images

[0.1.0](../../releases/tag/v0.1.0) - 2021-08-02
-----------------------------------------------

### Changed

- methods using specific option values for arguments now use well-defined and documented `Enum`s for those arguments instead of generic strings
- made the submodule `apify_client.consts` containing those `Enum`s available

### Internal changes

- updated development dependencies
- enforced unified use of single quotes and double quotes
- added repository dispatch to build actor images with this client when publishing a new version

[0.0.1](../../releases/tag/v0.0.1) - 2021-05-13
-----------------------------------------------

Initial release of the package.
