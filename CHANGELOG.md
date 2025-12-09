# Changelog

All notable changes to this project will be documented in this file.

<!-- git-cliff-unreleased-start -->
## 2.3.1 - **not yet released**

### 🚀 Features

- Expose `actorPermissionLevel` in Actor client ([#553](https://github.com/apify/apify-client-python/pull/553)) ([198e2ca](https://github.com/apify/apify-client-python/commit/198e2cad0d9b79a599a678285420e7dc7026ef00)) by [@stepskop](https://github.com/stepskop)


<!-- git-cliff-unreleased-end -->
## [2.3.0](https://github.com/apify/apify-client-python/releases/tag/v2.3.0) (2025-11-13)

### 🚀 Features

- Add support for Python 3.14 ([#520](https://github.com/apify/apify-client-python/pull/520)) ([68ebbd9](https://github.com/apify/apify-client-python/commit/68ebbd9162f076a20a4a02dd1ebe0dac7ece696a)) by [@vdusek](https://github.com/vdusek)
- Add signature arguments for dataset and kvs methods ([#530](https://github.com/apify/apify-client-python/pull/530)) ([10d1e45](https://github.com/apify/apify-client-python/commit/10d1e45c727cd0cc9324dca70755d8fd61c67f74)) by [@Pijukatel](https://github.com/Pijukatel), closes [#517](https://github.com/apify/apify-client-python/issues/517)

### 🐛 Bug Fixes

- Update impit to fix rare `JSONDecodeError` ([#536](https://github.com/apify/apify-client-python/pull/536)) ([c0b9096](https://github.com/apify/apify-client-python/commit/c0b90967a085307f08e455c860f990f824ce87e2)) by [@Pijukatel](https://github.com/Pijukatel)


## [2.2.1](https://github.com/apify/apify-client-python/releases/tag/v2.2.1) (2025-10-20)

### 🐛 Bug Fixes

- Move restart on error Actor option to Run options ([#508](https://github.com/apify/apify-client-python/pull/508)) ([8f73420](https://github.com/apify/apify-client-python/commit/8f73420ba2b9f2045bfdf3a224b6573ca2941b85)) by [@DaveHanns](https://github.com/DaveHanns)


## [2.2.0](https://github.com/apify/apify-client-python/releases/tag/v2.2.0) (2025-10-13)

### 🚀 Features

- Add `KeyValueStoreClient(Async).get_record_public_url` ([#506](https://github.com/apify/apify-client-python/pull/506)) ([6417d26](https://github.com/apify/apify-client-python/commit/6417d26f90af2113247b73a42a5909510a3a1a16)) by [@Pijukatel](https://github.com/Pijukatel), closes [#497](https://github.com/apify/apify-client-python/issues/497)
- Add started_before and started_after to run list ([#513](https://github.com/apify/apify-client-python/pull/513)) ([3aaa056](https://github.com/apify/apify-client-python/commit/3aaa056a651f773638b6847c846117365bae6309)) by [@danpoletaev](https://github.com/danpoletaev)


## [2.1.0](https://github.com/apify/apify-client-python/releases/tag/v2.1.0) (2025-09-15)

### 🚀 Features

- Add forcePermissionLevel run option ([#498](https://github.com/apify/apify-client-python/pull/498)) ([b297523](https://github.com/apify/apify-client-python/commit/b2975233c30f47883dbcfc716fc6bb77ce388306)) by [@tobice](https://github.com/tobice)

### 🐛 Bug Fixes

- Casing in `exclusiveStartKey` API param ([#495](https://github.com/apify/apify-client-python/pull/495)) ([5e96f71](https://github.com/apify/apify-client-python/commit/5e96f71cc6d3290d161fa46fc8cd9adef478088e)) by [@barjin](https://github.com/barjin), closes [#484](https://github.com/apify/apify-client-python/issues/484)
- Presigned resource urls shouldn&#x27;t follow base url ([#500](https://github.com/apify/apify-client-python/pull/500)) ([b224218](https://github.com/apify/apify-client-python/commit/b2242185f7eb0891bda29c361c7f5cf6f7dcba20)) by [@Pijukatel](https://github.com/Pijukatel), closes [#496](https://github.com/apify/apify-client-python/issues/496)


## [2.0.0](https://github.com/apify/apify-client-python/releases/tag/v2.0.0) (2025-08-15)

- Check out the [Upgrading guide](https://docs.apify.com/api/client/python/docs/upgrading/upgrading-to-v2) to ensure a smooth update.

### 🚀 Features

- Extend status parameter to an array of possible statuses  ([#455](https://github.com/apify/apify-client-python/pull/455)) ([76f6769](https://github.com/apify/apify-client-python/commit/76f676973d067ce8af398d8e6ceea55595da5ecf)) by [@JanHranicky](https://github.com/JanHranicky)
- Expose apify_client.errors module ([#468](https://github.com/apify/apify-client-python/pull/468)) ([c0cc147](https://github.com/apify/apify-client-python/commit/c0cc147fd0c5a60e5a025db6b6c761e811efe1da)) by [@Mantisus](https://github.com/Mantisus), closes [#158](https://github.com/apify/apify-client-python/issues/158)
- Add dataset.create_items_public_url and key_value_store.create_keys_public_url ([#453](https://github.com/apify/apify-client-python/pull/453)) ([2b1e110](https://github.com/apify/apify-client-python/commit/2b1e1104c15c987b0024010df41d6d356ea37dd3)) by [@danpoletaev](https://github.com/danpoletaev)

### Chore

- [**breaking**] Bump minimum Python version to 3.10 ([#469](https://github.com/apify/apify-client-python/pull/469)) ([92b4789](https://github.com/apify/apify-client-python/commit/92b47895eb48635e2d573b99d59bb077999c5b27)) by [@vdusek](https://github.com/vdusek)

### Refactor

- [**breaking**] Remove support for passing a single string to the `unwind` parameter in `DatasetClient` ([#467](https://github.com/apify/apify-client-python/pull/467)) ([e8aea2c](https://github.com/apify/apify-client-python/commit/e8aea2c8f3833082bf78562f3fa981a1f8e88b26)) by [@Mantisus](https://github.com/Mantisus), closes [#255](https://github.com/apify/apify-client-python/issues/255)
- [**breaking**] Remove deprecated constant re-exports from `consts.py` ([#466](https://github.com/apify/apify-client-python/pull/466)) ([7731f0b](https://github.com/apify/apify-client-python/commit/7731f0b3a4ca8c99be9392517d36f841cb293ed5)) by [@Mantisus](https://github.com/Mantisus), closes [#163](https://github.com/apify/apify-client-python/issues/163)
- [**breaking**] Replace `httpx` HTTP client with `impit` ([#456](https://github.com/apify/apify-client-python/pull/456)) ([1df6792](https://github.com/apify/apify-client-python/commit/1df6792386398b28eb565dfbc58c7eba13f451a4)) by [@Mantisus](https://github.com/Mantisus)
- [**breaking**] Remove deprecated `as_bytes` and `as_file` parameters from `KeyValueStoreClient.get_record` ([#463](https://github.com/apify/apify-client-python/pull/463)) ([b880231](https://github.com/apify/apify-client-python/commit/b88023125a41d02f95f687b8fd6090e7080efe3e)) by [@Mantisus](https://github.com/Mantisus)
- [**breaking**] Remove `parse_response` arg from the `call` method ([#462](https://github.com/apify/apify-client-python/pull/462)) ([840d51a](https://github.com/apify/apify-client-python/commit/840d51af12a7e53decf9d3294d0e0c3c848e9c08)) by [@Mantisus](https://github.com/Mantisus), closes [#166](https://github.com/apify/apify-client-python/issues/166)


## [1.12.2](https://github.com/apify/apify-client-python/releases/tag/v1.12.2) (2025-08-08)

### 🐛 Bug Fixes

- Fix API error with stream ([#459](https://github.com/apify/apify-client-python/pull/459)) ([0c91ca5](https://github.com/apify/apify-client-python/commit/0c91ca516a01a6fca7bc8fa07f7bf9c15c75bf9d)) by [@Pijukatel](https://github.com/Pijukatel)


## [1.12.1](https://github.com/apify/apify-client-python/releases/tag/v1.12.1) (2025-07-30)

### 🐛 Bug Fixes

- Restrict apify-shared version ([#447](https://github.com/apify/apify-client-python/pull/447)) ([22cd220](https://github.com/apify/apify-client-python/commit/22cd220e8f22af01f5fdfcedc684015c006b6fe6)) by [@vdusek](https://github.com/vdusek)


## [1.12.0](https://github.com/apify/apify-client-python/releases/tag/v1.12.0) (2025-06-26)

### 🚀 Features

- Allow sorting of Actors collection ([#422](https://github.com/apify/apify-client-python/pull/422)) ([df6e47d](https://github.com/apify/apify-client-python/commit/df6e47d3b72e0aa5563f1ece7abc9d9da50b77a2)) by [@protoss70](https://github.com/protoss70)
- Add `KeyValueStoreClient.record_exists` ([#427](https://github.com/apify/apify-client-python/pull/427)) ([519529b](https://github.com/apify/apify-client-python/commit/519529b01895958aa33516d8ec4853290c388d05)) by [@janbuchar](https://github.com/janbuchar)

### 🐛 Bug Fixes

- Enable to add headers template in webhooks created dynamically ([#419](https://github.com/apify/apify-client-python/pull/419)) ([b84d1ec](https://github.com/apify/apify-client-python/commit/b84d1ec0491ad2623defcfba5fe1aa06274cf533)) by [@gaelloyoly](https://github.com/gaelloyoly)
- Rename sortBy parameters option ([#426](https://github.com/apify/apify-client-python/pull/426)) ([a270409](https://github.com/apify/apify-client-python/commit/a2704095928651bf183743bf85fb365c65480d80)) by [@protoss70](https://github.com/protoss70)


## [1.11.0](https://github.com/apify/apify-client-python/releases/tag/v1.11.0) (2025-06-13)

### 🚀 Features

- Add `validate_input` endpoint ([#396](https://github.com/apify/apify-client-python/pull/396)) ([1c5bf85](https://github.com/apify/apify-client-python/commit/1c5bf8550ffd91b94ea83694f7c933cf2767fadc)) by [@Pijukatel](https://github.com/Pijukatel), closes [#151](https://github.com/apify/apify-client-python/issues/151)
- Add list kv store keys by collection or prefix ([#397](https://github.com/apify/apify-client-python/pull/397)) ([6747c20](https://github.com/apify/apify-client-python/commit/6747c201cd654953a97a4c3fe8256756eb7568c7)) by [@MFori](https://github.com/MFori)
- Add redirected actor logs ([#403](https://github.com/apify/apify-client-python/pull/403)) ([fd02cd8](https://github.com/apify/apify-client-python/commit/fd02cd8726f1664677a47dcb946a0186080d7839)) by [@Pijukatel](https://github.com/Pijukatel), closes [#402](https://github.com/apify/apify-client-python/issues/402)
- Add `unlock_requests` method to RequestQueue clients ([#408](https://github.com/apify/apify-client-python/pull/408)) ([d4f0018](https://github.com/apify/apify-client-python/commit/d4f00186016fab4e909a7886467e619b23e627e5)) by [@drobnikj](https://github.com/drobnikj)
- Add `StatusMessageWatcher` ([#407](https://github.com/apify/apify-client-python/pull/407)) ([a535512](https://github.com/apify/apify-client-python/commit/a53551217b62a2a6ca2ccbc81130043560fbc475)) by [@Pijukatel](https://github.com/Pijukatel), closes [#404](https://github.com/apify/apify-client-python/issues/404)


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


## [1.7.1](https://github.com/apify/apify-client-python/releases/tag/v1.7.1) (2024-07-11)

### 🐛 Bug Fixes

- Fix breaking change (sync -> async) in 1.7.0
- Fix getting storages of last run


## [1.7.0](https://github.com/apify/apify-client-python/releases/tag/v1.7.0) (2024-05-20)

### 🐛 Bug Fixes

- Fix abort of last task run
- Fix abort of last Actor run
- `ActorClient`'s and `TaskClient`'s `last_run` methods are asynchronous


## [1.6.4](https://github.com/apify/apify-client-python/releases/tag/v1.6.4) (2024-02-27)

### 🚀 Features

- Add `monthlyUsage()` and `limits()` methods to `UserClient`


## [1.6.3](https://github.com/apify/apify-client-python/releases/tag/v1.6.3) (2023-02-16)

### 🚀 Features

- Add `log()` method to `BuildClient`


## [1.6.2](https://github.com/apify/apify-client-python/releases/tag/v1.6.2) (2023-01-08)

### Chore

- Relative imports were replaced for absolute imports


## [1.6.1](https://github.com/apify/apify-client-python/releases/tag/v1.6.1) (2023-12-11)

### 🐛 Bug Fixes

- Fix `_BaseHTTPClient._parse_params()` method to ensure correct conversion of API list parameters


## [1.6.0](https://github.com/apify/apify-client-python/releases/tag/v1.6.0) (2023-11-16)

### Chore

- Migrate from Autopep8 and Flake8 to Ruff


## [1.5.0](https://github.com/apify/apify-client-python/releases/tag/v1.5.0) (2023-10-18)

### 🚀 Features

- Add support for Python 3.12
- Add DELETE to Actor runs
- Add DELETE to Actor builds

### Chore

- Rewrite documentation publication to use Docusaurus
- Remove PR Toolkit workflow


## [1.4.1](https://github.com/apify/apify-client-python/releases/tag/v1.4.1) (2023-09-06)

### 🚀 Features

- Add `StoreCollectionClient` for listing Actors in the Apify Store
- Add support for specifying the `max_items` parameter for pay-per result Actors and their runs

### Chore

- Improve logging of HTTP requests
- Remove `pytest-randomly` Pytest plugin


## [1.4.0](https://github.com/apify/apify-client-python/releases/tag/v1.4.0) (2023-08-23)

### 🚀 Features

- Add `RunClient.reboot` method to reboot Actor runs

### Chore

- Simplify code via `flake8-simplify`
- Unify indentation in configuration files


## [1.3.1](https://github.com/apify/apify-client-python/releases/tag/v1.3.1) (2023-07-28)

### Chore

- Start importing general constants and utilities from the `apify-shared` library


## [1.3.0](https://github.com/apify/apify-client-python/releases/tag/v1.3.0) (2023-07-24)

### 🚀 Features

- Add `list_and_lock_head`, `delete_request_lock`, `prolong_request_lock` methods to `RequestQueueClient`
- Add `batch_add_requests`, `batch_delete_requests`, `list_requests` methods `RequestQueueClient`


## [1.2.2](https://github.com/apify/apify-client-python/releases/tag/v1.2.2) (2023-05-31)

### 🐛 Bug Fixes

- Fix encoding webhook lists in request parameters


## [1.2.1](https://github.com/apify/apify-client-python/releases/tag/v1.2.1) (2023-05-23)

### 🐛 Bug Fixes

- Relax dependency requirements to improve compatibility with other libraries


## [1.2.0](https://github.com/apify/apify-client-python/releases/tag/v1.2.0) (2023-05-23)

### 🚀 Features

- Add option to change the build, memory limit and timeout when resurrecting a run

### Chore

- Update dependencies


## [1.1.1](https://github.com/apify/apify-client-python/releases/tag/v1.1.1) (2023-05-05)

### Chore

- Change GitHub workflows to use new secrets


## [1.1.0](https://github.com/apify/apify-client-python/releases/tag/v1.1.0) (2023-05-05)

### 🚀 Features

- Add support for `is_status_message_terminal` flag in Actor run status message update

### Chore

- Switch from `setup.py` to `pyproject.toml` for specifying project setup


## [1.0.0](https://github.com/apify/apify-client-python/releases/tag/v1.0.0) (2023-03-13)

### Breaking changes

- Drop support for Python 3.7, add support for Python 3.11
- Unify methods for streaming resources
- Switch underlying HTTP library from `requests` to `httpx`

### 🚀 Features

- Add support for asynchronous usage via `ApifyClientAsync`
- Add configurable socket timeout for requests to the Apify API
- Add `py.typed` file to signal type checkers that this package is typed
- Add method to update status message for a run
- Add option to set up webhooks for Actor builds
- Add logger with basic debugging info
- Add support for `schema` parameter in `get_or_create` method for datasets and key-value stores
- Add support for `title` parameter in task and schedule methods
- Add `x-apify-workflow-key` header support
- Add support for `flatten` and `view` parameters in dataset items methods
- Add support for `origin` parameter in Actor/task run methods
- Add clients for Actor version environment variables

### 🐛 Bug Fixes

- Disallow `NaN` and `Infinity` values in JSONs sent to the Apify API

### Chore

- Simplify retrying with exponential backoff
- Improve checks for "not found" errors
- Simplify flake8 config
- Update development dependencies
- Simplify development scripts
- Update GitHub Actions versions to fix deprecations
- Unify unit test style
- Unify preparing resource representation
- Update output management in GitHub Workflows to fix deprecations
- Improve type hints across codebase
- Add option to manually publish the package with a workflow dispatch
- Add `pre-commit` to run code quality checks before committing
- Convert `unittest`-style tests to `pytest`-style tests
- Backport project setup improvements from `apify-sdk-python`


## [0.6.0](https://github.com/apify/apify-client-python/releases/tag/v0.6.0) (2022-06-27)

### Removed

- Drop support for single-file Actors

### Chore

- Update dependencies
- Fix some lint issues in shell scripts and `setup.py`
- Add Python 3.10 to unit test roster


## [0.5.0](https://github.com/apify/apify-client-python/releases/tag/v0.5.0) (2021-09-16)

### Changed

- Improve retrying broken API server connections

### 🐛 Bug Fixes

- Fix timeout value in actively waiting for a run to finish

### Chore

- Update development dependencies


## [0.4.0](https://github.com/apify/apify-client-python/releases/tag/v0.4.0) (2021-09-07)

### Changed

- Improve handling of `Enum` arguments
- Improve support for storing more data types in key-value stores

### 🐛 Bug Fixes

- Fix values of some `ActorJobStatus` `Enum` members


## [0.3.0](https://github.com/apify/apify-client-python/releases/tag/v0.3.0) (2021-08-26)

### 🚀 Features

- Add the `test()` method to the webhook client
- Add support for indicating the pagination direction in the `ListPage` objects

### Changed

- Improve support for storing more data types in datasets

### 🐛 Bug Fixes

- Fix return type in the `DatasetClient.list_items()` method docs

### Chore

- Add human-friendly names to the jobs in Github Action workflows
- Update development dependencies


## [0.2.0](https://github.com/apify/apify-client-python/releases/tag/v0.2.0) (2021-08-09)

### 🚀 Features

- Add the `gracefully` parameter to the "Abort run" method

### Changed

- Replace `base_url` with `api_url` in the client constructor to enable easier passing of the API server url from environment variables available to Actors on the Apify platform

### Chore

- Change tags for Actor images with this client on Docker Hub to be aligned with the Apify SDK Node.js images
- Update the `requests` dependency to 2.26.0
- Update development dependencies


## [0.1.0](https://github.com/apify/apify-client-python/releases/tag/v0.1.0) (2021-08-02)

### Changed

- Methods using specific option values for arguments now use well-defined and documented `Enum`s for those arguments instead of generic strings
- Make the submodule `apify_client.consts` containing those `Enum`s available

### Chore

- Update development dependencies
- Enforce unified use of single quotes and double quotes
- Add repository dispatch to build Actor images with this client when publishing a new version


## [0.0.1](https://github.com/apify/apify-client-python/releases/tag/v0.0.1) (2021-05-13)

- Initial release of the package.