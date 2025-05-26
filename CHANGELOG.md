# Changelog

All notable changes to this project will be documented in this file.

<!-- git-cliff-unreleased-start -->
## 1.10.1 - **not yet released**

### 🚀 Features

- Add `validate_input` endpoint ([#396](https://github.com/apify/apify-client-python/pull/396)) ([1c5bf85](https://github.com/apify/apify-client-python/commit/1c5bf8550ffd91b94ea83694f7c933cf2767fadc)) by [@Pijukatel](https://github.com/Pijukatel), closes [#151](https://github.com/apify/apify-client-python/issues/151)
- Add list kv store keys by collection or prefix ([#397](https://github.com/apify/apify-client-python/pull/397)) ([6747c20](https://github.com/apify/apify-client-python/commit/6747c201cd654953a97a4c3fe8256756eb7568c7)) by [@MFori](https://github.com/MFori)
- Add redirected actor logs ([#403](https://github.com/apify/apify-client-python/pull/403)) ([fd02cd8](https://github.com/apify/apify-client-python/commit/fd02cd8726f1664677a47dcb946a0186080d7839)) by [@Pijukatel](https://github.com/Pijukatel), closes [#402](https://github.com/apify/apify-client-python/issues/402)
- Add `unlock_requests` method to RequestQueue clients ([#408](https://github.com/apify/apify-client-python/pull/408)) ([d4f0018](https://github.com/apify/apify-client-python/commit/d4f00186016fab4e909a7886467e619b23e627e5)) by [@drobnikj](https://github.com/drobnikj)


<!-- git-cliff-unreleased-end -->
## [1.10.0](https://github.com/apify/apify-client-python/releases/tag/v1.10.0) (2025-04-29)

### 🚀 Features

- Add support for general resource access ([#394](https://github.com/apify/apify-client-python/pull/394)) ([cc79c30](https://github.com/apify/apify-client-python/commit/cc79c30a7d0b57d21a5fc7efb94c08cc4035c8b4)) by [@tobice](https://github.com/tobice)


## [1.9.4](https://github.com/apify/apify-client-python/releases/tag/v1.9.4) (2025-04-24)

### 🐛 Bug Fixes

- Default_build() returns BuildClient ([#389](https://github.com/apify/apify-client-python/pull/389)) ([8149052](https://github.com/apify/apify-client-python/commit/8149052a97032f1336147a48c8a8f6cd5e076b95)) by [@danpoletaev](https://github.com/danpoletaev)


## [1.9.3](https://github.com/apify/apify-client-python/releases/tag/v1.9.3) (2025-04-14)

### 🚀 Features

- Add maxItems and maxTotalChargeUsd to resurrect ([#360](https://github.com/apify/apify-client-python/pull/360)) ([a020807](https://github.com/apify/apify-client-python/commit/a0208073ef93804358e4377959a56d8342f83447)) by [@novotnyj](https://github.com/novotnyj)
- Add get default build method ([#385](https://github.com/apify/apify-client-python/pull/385)) ([f818b95](https://github.com/apify/apify-client-python/commit/f818b95fec1c4e57e98b28ad0b2b346ee2f64602)) by [@danpoletaev](https://github.com/danpoletaev)


## [1.9.2](https://github.com/apify/apify-client-python/releases/tag/v1.9.2) (2025-02-14)

### 🐛 Bug Fixes

- Add missing PPE-related Actor parameters ([#351](https://github.com/apify/apify-client-python/pull/351)) ([75b1c6c](https://github.com/apify/apify-client-python/commit/75b1c6c4d26c21d69ce10ef4424c6ba458bd5a33)) by [@janbuchar](https://github.com/janbuchar)


## [1.9.1](https://github.com/apify/apify-client-python/releases/tag/v1.9.1) (2025-02-07)

### 🐛 Bug Fixes

- Add `stats` attribute for `ApifyClientAsync` ([#348](https://github.com/apify/apify-client-python/pull/348)) ([6631f8c](https://github.com/apify/apify-client-python/commit/6631f8ccbd56107647a6b886ddcd5cbae378069d)) by [@Mantisus](https://github.com/Mantisus)
- Fix return type of charge API call ([#350](https://github.com/apify/apify-client-python/pull/350)) ([28102fe](https://github.com/apify/apify-client-python/commit/28102fe42039df2f1f2bb3c4e4aa652e37933456)) by [@janbuchar](https://github.com/janbuchar)


## [1.9.0](https://github.com/apify/apify-client-python/releases/tag/v1.9.0) (2025-02-04)

### 🚀 Features

- Add user.update_limits ([#279](https://github.com/apify/apify-client-python/pull/279)) ([7aed9c9](https://github.com/apify/apify-client-python/commit/7aed9c928958831168ac8d293538d6fd3adbc5e5)) by [@MFori](https://github.com/MFori), closes [#329](https://github.com/apify/apify-client-python/issues/329)
- Add charge method to the run client for &quot;pay per event&quot; ([#304](https://github.com/apify/apify-client-python/pull/304)) ([3bd6bbb](https://github.com/apify/apify-client-python/commit/3bd6bbb86d2b777863f0c3d0459b61da9a7f15ff)) by [@Jkuzz](https://github.com/Jkuzz)
- Add error data to ApifyApiError ([#314](https://github.com/apify/apify-client-python/pull/314)) ([df2398b](https://github.com/apify/apify-client-python/commit/df2398b51d774c5f8653a80f83b320d0f5394dde)) by [@Pijukatel](https://github.com/Pijukatel), closes [#306](https://github.com/apify/apify-client-python/issues/306)
- Add GET: dataset.statistics ([#324](https://github.com/apify/apify-client-python/pull/324)) ([19ea4ad](https://github.com/apify/apify-client-python/commit/19ea4ad46068520885bd098739a9b64d1f17e1fc)) by [@MFori](https://github.com/MFori)
- Add `get_open_api_specification` method to `BuildClient` ([#336](https://github.com/apify/apify-client-python/pull/336)) ([9ebcedb](https://github.com/apify/apify-client-python/commit/9ebcedbaede53add167f1c51ec6196e793e67917)) by [@danpoletaev](https://github.com/danpoletaev)
- Add rate limit statistics ([#343](https://github.com/apify/apify-client-python/pull/343)) ([f35c68f](https://github.com/apify/apify-client-python/commit/f35c68ff824ce83bf9aca893589381782a1a48c7)) by [@Mantisus](https://github.com/Mantisus)


## [1.8.1](https://github.com/apify/apify-client-python/releases/tags/v1.8.1) (2024-09-17)

### 🐛 Bug Fixes

- Batch add requests can handle more than 25 requests ([#268](https://github.com/apify/apify-client-python/pull/268)) ([9110ee0](https://github.com/apify/apify-client-python/commit/9110ee08954762aed00ac09cd042e802c1d041f7)) by [@vdusek](https://github.com/vdusek), closes [#264](https://github.com/apify/apify-client-python/issues/264)


## [1.8.0](https://github.com/apify/apify-client-python/releases/tags/v1.8.0) (2024-08-30)

- drop support for Python 3.8

### 🚀 Features

- Adds headers_template to webhooks and webhooks_collection ([#239](https://github.com/apify/apify-client-python/pull/239)) ([6dbd781](https://github.com/apify/apify-client-python/commit/6dbd781d24d9deb6a7669193ce4d5a4190fe5026)) by [@jakerobers](https://github.com/jakerobers)
- Add actor standby ([#248](https://github.com/apify/apify-client-python/pull/248)) ([dd4bf90](https://github.com/apify/apify-client-python/commit/dd4bf9072a4caa189af5f90e513e37df325dc929)) by [@jirimoravcik](https://github.com/jirimoravcik)
- Allow passing list of fields to unwind parameter ([#256](https://github.com/apify/apify-client-python/pull/256)) ([036b455](https://github.com/apify/apify-client-python/commit/036b455c51243e0ef81cb74a44fe670abc085ce7)) by [@fnesveda](https://github.com/fnesveda)

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
- added option to set up webhooks for Actor builds
- added logger with basic debugging info
- added support for `schema` parameter in `get_or_create` method for datasets and key-value stores
- added support for `title` parameter in task and schedule methods
- added `x-apify-workflow-key` header support
- added support for `flatten` and `view` parameters in dataset items methods
- added support for `origin` parameter in Actor/task run methods
- added clients for Actor version environment variables

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

- Dropped support for single-file Actors

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
  to enable easier passing of the API server url from environment variables available to Actors on the Apify platform

### Internal changes

- changed tags for Actor images with this client on Docker Hub to be aligned with the Apify SDK Node.js images
- updated the `requests` dependency to 2.26.0
- updated development dependencies

## [0.1.0](../../releases/tag/v0.1.0) - 2021-08-02

### Changed

- methods using specific option values for arguments now use well-defined and documented `Enum`s for those arguments instead of generic strings
- made the submodule `apify_client.consts` containing those `Enum`s available

### Internal changes

- updated development dependencies
- enforced unified use of single quotes and double quotes
- added repository dispatch to build Actor images with this client when publishing a new version

## [0.0.1](../../releases/tag/v0.0.1) - 2021-05-13

Initial release of the package.