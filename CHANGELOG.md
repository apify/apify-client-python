# Changelog

## [1.7.2](../../releases/tag/v1.7.2) - Unreleased

...

## [1.7.1](../../releases/tag/v1.7.1) - 2024-07-11

### Fixed

- fix breaking change (sync -> async) in 1.7.0
- fix getting storages of last run

## [1.7.0](../../releases/tag/v1.7.0) - 2024-05-20

### Fixed

- fix abort of last task run
- fix abort of last Actor run
- `ActorClient`'s and `TaskClient`'s `last_run` methods are asynchronous

## [1.6.4](../../releases/tag/v1.6.4) - 2024-02-27

### Added

- added `monthlyUsage()` and `limits()` methods to `UserClient`

## [1.6.3](../../releases/tag/v1.6.3) - 2023-02-16

### Added

- added `log()` method to `BuildClient`

## [1.6.2](../../releases/tag/v1.6.2) - 2023-01-08

### Internal changes

- Relative imports were replaced for absolute imports

## [1.6.1](../../releases/tag/v1.6.1) - 2023-12-11

### Fixed

- Fixed `_BaseHTTPClient._parse_params()` method to ensure correct conversion of API list parameters

## [1.6.0](../../releases/tag/v1.6.0) - 2023-11-16

### Internal changes

- Migrate from Autopep8 and Flake8 to Ruff

## [1.5.0](../../releases/tag/v1.5.0) - 2023-10-18

### Added

- added support for Python 3.12
- added DELETE to Actor runs
- added DELETE to Actor builds

### Internal changes

- rewrote documentation publication to use Docusaurus
- removed PR Toolkit workflow

## [1.4.1](../../releases/tag/v1.4.1) - 2023-09-06

### Added

- added `StoreCollectionClient` for listing Actors in the Apify Store
- added support for specifying the `max_items` parameter for pay-per result Actors and their runs

### Internal changes

- improved logging of HTTP requests
- removed `pytest-randomly` Pytest plugin

## [1.4.0](../../releases/tag/v1.4.0) - 2023-08-23

### Added

- added `RunClient.reboot` method to reboot Actor runs

### Internal changes

- simplified code via `flake8-simplify`
- unified indentation in configuration files

## [1.3.1](../../releases/tag/v1.3.1) - 2023-07-28

### Internal changes

- started importing general constants and utilities from the `apify-shared` library

## [1.3.0](../../releases/tag/v1.3.0) - 2023-07-24

### Added

- added `list_and_lock_head`, `delete_request_lock`, `prolong_request_lock` methods to `RequestQueueClient`
- added `batch_add_requests`, `batch_delete_requests`, `list_requests` methods `RequestQueueClient`

## [1.2.2](../../releases/tag/v1.2.2) - 2023-05-31

### Fixed

- fixed encoding webhook lists in request parameters

## [1.2.1](../../releases/tag/v1.2.1) - 2023-05-23

### Fixed

- relaxed dependency requirements to improve compatibility with other libraries

## [1.2.0](../../releases/tag/v1.2.0) - 2023-05-23

### Added

- added option to change the build, memory limit and timeout when resurrecting a run

### Internal changes

- updated dependencies

## [1.1.1](../../releases/tag/v1.1.1) - 2023-05-05

### Internal changes

- changed GitHub workflows to use new secrets

## [1.1.0](../../releases/tag/v1.1.0) - 2023-05-05

### Added

- added support for `is_status_message_terminal` flag in Actor run status message update

### Internal changes

- switched from `setup.py` to `pyproject.toml` for specifying project setup

## [1.0.0](../../releases/tag/v1.0.0) - 2023-03-13

### Breaking changes

- dropped support for Python 3.7, added support for Python 3.11
- unified methods for streaming resources
- switched underlying HTTP library from `requests` to `httpx`

### Added

- added support for asynchronous usage via `ApifyClientAsync`
- added configurable socket timeout for requests to the Apify API
- added `py.typed` file to signal type checkers that this package is typed
- added method to update status message for a run
- added option to set up webhooks for actor builds
- added logger with basic debugging info
- added support for `schema` parameter in `get_or_create` method for datasets and key-value stores
- added support for `title` parameter in task and schedule methods
- added `x-apify-workflow-key` header support
- added support for `flatten` and `view` parameters in dataset items methods
- added support for `origin` parameter in actor/task run methods
- added clients for actor version environment variables

### Fixed

- disallowed `NaN` and `Infinity` values in JSONs sent to the Apify API

### Internal changes

- simplified retrying with exponential backoff
- improved checks for "not found" errors
- simplified flake8 config
- updated development dependencies
- simplified development scripts
- updated GitHub Actions versions to fix deprecations
- unified unit test style
- unified preparing resource representation
- updated output management in GitHub Workflows to fix deprecations
- improved type hints across codebase
- added option to manually publish the package with a workflow dispatch
- added `pre-commit` to run code quality checks before committing
- converted `unittest`-style tests to `pytest`-style tests
- backported project setup improvements from `apify-sdk-python`

## [0.6.0](../../releases/tag/v0.6.0) - 2022-06-27

### Removed

- Dropped support for single-file actors

### Internal changes

- updated dependencies
- fixed some lint issues in shell scripts and `setup.py`
- added Python 3.10 to unit test roster

## [0.5.0](../../releases/tag/v0.5.0) - 2021-09-16

### Changed

- improved retrying broken API server connections

### Fixed

- fixed timeout value in actively waiting for a run to finish

### Internal changes

- updated development dependencies

## [0.4.0](../../releases/tag/v0.4.0) - 2021-09-07

### Changed

- improved handling of `Enum` arguments
- improved support for storing more data types in key-value stores

### Fixed

- fixed values of some `ActorJobStatus` `Enum` members

## [0.3.0](../../releases/tag/v0.3.0) - 2021-08-26

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

## [0.2.0](../../releases/tag/v0.2.0) - 2021-08-09

### Added

- added the `gracefully` parameter to the "Abort run" method

### Changed

- replaced `base_url` with `api_url` in the client constructor
  to enable easier passing of the API server url from environment variables available to actors on the Apify platform

### Internal changes

- changed tags for actor images with this client on Docker Hub to be aligned with the Apify SDK Node.js images
- updated the `requests` dependency to 2.26.0
- updated development dependencies

## [0.1.0](../../releases/tag/v0.1.0) - 2021-08-02

### Changed

- methods using specific option values for arguments now use well-defined and documented `Enum`s for those arguments instead of generic strings
- made the submodule `apify_client.consts` containing those `Enum`s available

### Internal changes

- updated development dependencies
- enforced unified use of single quotes and double quotes
- added repository dispatch to build actor images with this client when publishing a new version

## [0.0.1](../../releases/tag/v0.0.1) - 2021-05-13

Initial release of the package.
