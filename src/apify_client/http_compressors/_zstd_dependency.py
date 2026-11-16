from __future__ import annotations

import sys

# zstd is in the standard library from Python 3.14, and no extra can add it to a build without it. Older versions need
# `backports.zstd` from the `zstd` extra. `_zstd.py` raises its `ModuleNotFoundError` under this name, so that
# `try_import` in `http_compressors/__init__.py` treats the dependency as missing.
if sys.version_info >= (3, 14):
    ZSTD_DEPENDENCY_NAME = '_zstd'
    ZSTD_EXTRA_NAME = None
else:
    ZSTD_DEPENDENCY_NAME = 'backports.zstd'
    ZSTD_EXTRA_NAME = 'zstd'
