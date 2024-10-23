# Changelog

All notable changes to this project will be documented in this file.

## [1.8.1](https://github.com/apify/apify-client-python/releases/tags/v1.8.1) (2024-09-17)

### 🐛 Bug Fixes

- Batch add requests can handle more than 25 requests ([#268](https://github.com/apify/apify-client-python/pulls/268), closes [#264](https://github.com/apify/apify-client-python/issues/264)) ([9110ee0](https://github.com/apify/apify-client-python/commit/9110ee08954762aed00ac09cd042e802c1d041f7)) by [@vdusek](https://github.com/vdusek)

## [1.8.0](https://github.com/apify/apify-client-python/releases/tags/v1.8.0) (2024-08-30)

### 🚀 Features

- Adds headers_template to webhooks and webhooks_collection ([#239](https://github.com/apify/apify-client-python/pulls/239)) ([6dbd781](https://github.com/apify/apify-client-python/commit/6dbd781d24d9deb6a7669193ce4d5a4190fe5026)) by [@jakerobers](https://github.com/jakerobers)
- Add actor standby ([#248](https://github.com/apify/apify-client-python/pulls/248)) ([dd4bf90](https://github.com/apify/apify-client-python/commit/dd4bf9072a4caa189af5f90e513e37df325dc929)) by [@jirimoravcik](https://github.com/jirimoravcik)
- Allow passing list of fields to unwind parameter ([#256](https://github.com/apify/apify-client-python/pulls/256)) ([036b455](https://github.com/apify/apify-client-python/commit/036b455c51243e0ef81cb74a44fe670abc085ce7)) by [@fnesveda](https://github.com/fnesveda)

## [1.7.1](https://github.com/apify/apify-client-python/releases/tags/v1.7.1) (2024-07-11)

### 🐛 Bug Fixes

- Getting storages of last run ([#241](https://github.com/apify/apify-client-python/pulls/241), closes [#231](https://github.com/apify/apify-client-python/issues/231), [#240](https://github.com/apify/apify-client-python/issues/240)) ([1aaa196](https://github.com/apify/apify-client-python/commit/1aaa19688e3d124f73419961b03b6b35a619da84)) by [@vdusek](https://github.com/vdusek)

## [1.7.0](https://github.com/apify/apify-client-python/releases/tags/v1.7.0) (2024-05-20)

### 🐛 Bug Fixes

- Aborting of last Actor/task run ([#192](https://github.com/apify/apify-client-python/pulls/192)) ([186afe7](https://github.com/apify/apify-client-python/commit/186afe7b0ee1d371a56822bf79795f52079852b5)) by [@vdusek](https://github.com/vdusek)

## [1.6.4](https://github.com/apify/apify-client-python/releases/tags/v1.6.4) (2024-02-23)

### 🚀 Features

- Add monthlyUsage() and limits() methods to UserClient ([#183](https://github.com/apify/apify-client-python/pulls/183)) ([93d0afe](https://github.com/apify/apify-client-python/commit/93d0afe9c31f71e958171e9d511da53369fe418a)) by [@tobice](https://github.com/tobice)

## [1.6.3](https://github.com/apify/apify-client-python/releases/tags/v1.6.3) (2024-02-14)

### 🚀 Features

- Add log() method to BuildClient (Python) ([#179](https://github.com/apify/apify-client-python/pulls/179)) ([1b14d4e](https://github.com/apify/apify-client-python/commit/1b14d4e3944f94bb8d17915d1f89933f0aaaea02)) by [@tobice](https://github.com/tobice)

## [1.5.0](https://github.com/apify/apify-client-python/releases/tags/v1.5.0) (2023-10-18)

### 🚀 Features

- Add run, build delete to client ([#152](https://github.com/apify/apify-client-python/pulls/152)) ([df5e52e](https://github.com/apify/apify-client-python/commit/df5e52e0702547a5a473b229a789e147571c135e)) by [@Jkuzz](https://github.com/Jkuzz)

## [1.4.1](https://github.com/apify/apify-client-python/releases/tags/v1.4.1) (2023-09-06)

### 🚀 Features

- Added StoreCollectionClient for listing Actors in Apify store ([#147](https://github.com/apify/apify-client-python/pulls/147)) ([88cb4a0](https://github.com/apify/apify-client-python/commit/88cb4a01997a07a5e2ee48e28f1dad1664fcae46)) by [@drobnikj](https://github.com/drobnikj)

## [1.3.1](https://github.com/apify/apify-client-python/releases/tags/v1.3.1) (2023-07-28)

### 🚀 Features

- Add list_and_lock_head, delete_request_lock, prolong_request_lock, batch_add_requests, batch_delete_requests and list_requests methods ([#129](https://github.com/apify/apify-client-python/pulls/129)) ([2145cae](https://github.com/apify/apify-client-python/commit/2145cae6233853d6014ddff6d0597b9d3d63ca87)) by [@drobnikj](https://github.com/drobnikj)

## [1.0.0](https://github.com/apify/apify-client-python/releases/tags/v1.0.0) (2023-03-13)

### 🚀 Features

- Make ListPage generic ([#97](https://github.com/apify/apify-client-python/pulls/97)) ([7f383f9](https://github.com/apify/apify-client-python/commit/7f383f918867e2bcefd16e79b458236098292e16)) by [@jirimoravcik](https://github.com/jirimoravcik)
- Updating pull request toolkit config [INTERNAL] ([b4475a9](https://github.com/apify/apify-client-python/commit/b4475a9585fd7017b135e7fd1af316aa244eda85)) by [@mtrunkat](https://github.com/mtrunkat)
- Updating pull request toolkit config [INTERNAL] ([ee72c07](https://github.com/apify/apify-client-python/commit/ee72c07bb82d6be764bc340e9f596ad671afb542)) by [@mtrunkat](https://github.com/mtrunkat)

### 🐛 Bug Fixes

- Change dataset iterate_items return type to AsyncIterator[Dict] ([#94](https://github.com/apify/apify-client-python/pulls/94)) ([e9dedba](https://github.com/apify/apify-client-python/commit/e9dedba6cb5380e656511351ecd6fc481f5e5c95)) by [@jirimoravcik](https://github.com/jirimoravcik)
- Calling user().get() will use '/me' endpoint correctly ([#110](https://github.com/apify/apify-client-python/pulls/110)) ([01c645d](https://github.com/apify/apify-client-python/commit/01c645d5f70b33dc1ee903dfa3fc08607db8a7be)) by [@jirimoravcik](https://github.com/jirimoravcik)

## [0.1.0](https://github.com/apify/apify-client-python/releases/tags/v0.1.0) (2021-08-02)

### Docs

- Fix link ([#48](https://github.com/apify/apify-client-python/pulls/48)) ([dcb84be](https://github.com/apify/apify-client-python/commit/dcb84be87029e730e9b716dd62e4930ea540f265)) by [@dragonraid](https://github.com/dragonraid)

<!-- generated by git-cliff -->