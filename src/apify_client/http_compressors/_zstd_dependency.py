from __future__ import annotations

import sys

# `try_import` in `http_compressors/__init__.py` treats an import error named this or its parent package as a missing
# zstd. `_zstd.py` raises under this name when zstd is installed but can't load, and on Python 3.14+ also when the
# Python build has no zstd.
if sys.version_info >= (3, 14):
    ZSTD_DEPENDENCY_NAME = '_zstd'
else:
    ZSTD_DEPENDENCY_NAME = 'backports.zstd'
