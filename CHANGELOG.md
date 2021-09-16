Changelog
=========

[0.5.0](../../releases/tag/v0.5.0) - 2021-09-16
-----------------------------------------------

### Changed

- improved retrying broken API server connections

### Fixed

- fixed timeout value in actively waiting for a run to finish

### Internal changes

- updated development dependencies

[0.4.0](../../releases/tag/v0.4.0) - 2021-09-07
-----------------------------------------------

### Changed

- improved handling of `Enum` arguments
- improved support for storing more data types in key-value stores

### Fixed

- fixed values of some `ActorJobStatus` `Enum` members

[0.3.0](../../releases/tag/v0.3.0) - 2021-08-26
-----------------------------------------------

### Added

- added the `test()` method to the webhook client
- added support for indicating the pagination direction in the `ListPage` objects

### Changed

- improved support for storing more data types in datasets

### Fixed

- fixed return type in the `DatasetClient.list_items()` method docs

### Internal changes

- added human-friendly names to the jobs in Github Action workflows
- updated development dependencies

[0.2.0](../../releases/tag/v0.2.0) - 2021-08-09
-----------------------------------------------

### Added

- added the `gracefully` parameter to the "Abort run" method

### Changed

- replaced `base_url` with `api_url` in the client constructor
  to enable easier passing of the API server url from environment variables available to actors on the Apify platform

### Internal changes

- changed tags for actor images with this client on Docker Hub to be aligned with the Apify SDK Node.js images
- updated the `requests` dependency to 2.26.0
- updated development dependencies

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
