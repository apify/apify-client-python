from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import pytest

from scripts import openapi_spec
from scripts.openapi_spec import (
    MIN_SPEC_SIZE_BYTES,
    read_recorded_version,
    read_spec_version,
    record_version,
    write_recorded_version,
)

if TYPE_CHECKING:
    from pathlib import Path


def make_spec(**overrides: Any) -> bytes:
    """Build a specification payload that passes validation, padded past the minimum size."""
    spec: dict[str, Any] = {
        'openapi': '3.1.2',
        'info': {'title': 'Apify API', 'version': 'v2-2026-07-28T083939Z'},
        'paths': {},
        'components': {},
    }
    spec.update(overrides)
    spec['x-padding'] = 'x' * MIN_SPEC_SIZE_BYTES
    return json.dumps(spec).encode()


def make_pyproject(tmp_path: Path, content: str) -> Path:
    """Write a `pyproject.toml` stub and point the module at it."""
    path = tmp_path / 'pyproject.toml'
    path.write_text(content, encoding='utf-8')
    return path


def test_read_spec_version_returns_the_version() -> None:
    """A valid specification yields its `info.version`."""
    assert read_spec_version(make_spec()) == 'v2-2026-07-28T083939Z'


@pytest.mark.parametrize(
    'payload',
    [
        pytest.param(b'{}', id='too small'),
        pytest.param(b'<html>error</html>' + b'x' * MIN_SPEC_SIZE_BYTES, id='not JSON'),
        pytest.param(json.dumps(['x' * MIN_SPEC_SIZE_BYTES]).encode(), id='JSON array'),
        pytest.param(json.dumps({'padding': 'x' * MIN_SPEC_SIZE_BYTES}).encode(), id='missing top-level members'),
        pytest.param(make_spec(info={'title': 'Apify API'}), id='no info.version'),
        pytest.param(make_spec(info={'version': ''}), id='empty info.version'),
        pytest.param(make_spec(info='not an object'), id='info is not an object'),
    ],
)
def test_read_spec_version_rejects_unusable_payloads(payload: bytes) -> None:
    """An error page, a truncated response, or a specification without a version stamp aborts instead of generating."""
    with pytest.raises(SystemExit) as exit_info:
        read_spec_version(payload)

    assert exit_info.value.code == 1


@pytest.mark.parametrize(
    'content',
    [
        pytest.param('[tool.apify.openapi-spec]\nversion = "old"\n', id='canonical'),
        pytest.param('[tool.apify.openapi-spec]\nversion="old"\n', id='no spaces around the equals sign'),
        pytest.param('[ tool.apify.openapi-spec ]\nversion = "old"\n', id='spaces inside the table header'),
        pytest.param('[tool.apify.openapi-spec] # pinned\nversion = "old"\n', id='comment after the table header'),
        pytest.param('[tool.apify.openapi-spec]\n# a note\nversion = "old"\n', id='comment before the entry'),
        pytest.param('[tool.other]\nversion = "keep"\n\n[tool.apify.openapi-spec]\nversion = "old"\n', id='not first'),
    ],
)
def test_write_recorded_version_rewrites_any_valid_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, content: str
) -> None:
    """Reformatting `pyproject.toml` doesn't break recording, so the nightly regeneration can't be tripped by it."""
    path = make_pyproject(tmp_path, content)
    monkeypatch.setattr(openapi_spec, 'PYPROJECT_PATH', path)

    write_recorded_version('new')

    assert read_recorded_version() == 'new'


def test_write_recorded_version_preserves_a_trailing_comment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Only the quoted value is replaced, so a comment on the same line survives."""
    path = make_pyproject(tmp_path, '[tool.apify.openapi-spec]\nversion = "old"  # bumped by the nightly job\n')
    monkeypatch.setattr(openapi_spec, 'PYPROJECT_PATH', path)

    write_recorded_version('new')

    assert path.read_text(encoding='utf-8').endswith('version = "new"  # bumped by the nightly job\n')


def test_write_recorded_version_leaves_a_later_table_alone(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing entry aborts rather than falling through to the next table's `version`."""
    path = make_pyproject(tmp_path, '[tool.apify.openapi-spec]\nother = "x"\n\n[tool.next]\nversion = "keep"\n')
    monkeypatch.setattr(openapi_spec, 'PYPROJECT_PATH', path)

    with pytest.raises(SystemExit) as exit_info:
        write_recorded_version('new')

    assert exit_info.value.code == 1
    assert 'version = "keep"' in path.read_text(encoding='utf-8')


def test_write_recorded_version_rejects_a_missing_table(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Without the table there is nowhere to record the version, so the run fails instead of guessing."""
    path = make_pyproject(tmp_path, '[tool.other]\nversion = "keep"\n')
    monkeypatch.setattr(openapi_spec, 'PYPROJECT_PATH', path)

    with pytest.raises(SystemExit) as exit_info:
        write_recorded_version('new')

    assert exit_info.value.code == 1
    assert path.read_text(encoding='utf-8') == '[tool.other]\nversion = "keep"\n'


def test_record_version_writes_the_fetched_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The fetched specification's version replaces the recorded one."""
    path = make_pyproject(tmp_path, '[tool.apify.openapi-spec]\nversion = "v2-2020-01-01T000000Z"\n')
    spec_path = tmp_path / 'openapi.json'
    spec_path.write_bytes(make_spec())
    monkeypatch.setattr(openapi_spec, 'PYPROJECT_PATH', path)
    monkeypatch.setattr(openapi_spec, 'SPEC_PATH', spec_path)

    record_version()

    assert read_recorded_version() == 'v2-2026-07-28T083939Z'


def test_record_version_is_idempotent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Recording an already-recorded version leaves the file byte for byte identical."""
    path = make_pyproject(tmp_path, '[tool.apify.openapi-spec]\nversion = "v2-2026-07-28T083939Z"\n')
    spec_path = tmp_path / 'openapi.json'
    spec_path.write_bytes(make_spec())
    monkeypatch.setattr(openapi_spec, 'PYPROJECT_PATH', path)
    monkeypatch.setattr(openapi_spec, 'SPEC_PATH', spec_path)
    before = path.read_bytes()

    record_version()

    assert path.read_bytes() == before


def test_record_version_requires_a_fetched_specification(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Running the recording step on its own aborts instead of recording a stale or absent version."""
    path = make_pyproject(tmp_path, '[tool.apify.openapi-spec]\nversion = "old"\n')
    monkeypatch.setattr(openapi_spec, 'REPO_ROOT', tmp_path)
    monkeypatch.setattr(openapi_spec, 'PYPROJECT_PATH', path)
    monkeypatch.setattr(openapi_spec, 'SPEC_PATH', tmp_path / 'missing.json')

    with pytest.raises(SystemExit) as exit_info:
        record_version()

    assert exit_info.value.code == 1
    assert read_recorded_version() == 'old'
