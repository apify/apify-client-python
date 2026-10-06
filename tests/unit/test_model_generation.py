from __future__ import annotations

import json
import subprocess
import sys
from typing import TYPE_CHECKING

from scripts.postprocess_generated_models import (
    REPO_ROOT,
    RESOURCE_INPUT_TYPEDDICTS,
    build_alias_map,
    postprocess_models,
    postprocess_typeddicts,
)

if TYPE_CHECKING:
    from pathlib import Path

MINIMAL_SPEC = {
    'openapi': '3.1.0',
    'info': {'title': 'Test', 'version': '1.0.0'},
    'paths': {},
    'components': {
        'schemas': {
            'RunStatus': {'type': 'string', 'enum': ['READY', 'RUNNING', 'SUCCEEDED']},
            'Run': {
                'type': 'object',
                'required': ['id', 'startedAt', 'status'],
                'properties': {
                    'id': {'type': 'string'},
                    'startedAt': {'type': 'string', 'format': 'date-time'},
                    'status': {'$ref': '#/components/schemas/RunStatus'},
                },
            },
            # Post-processing fails unless every TypedDict seed is present in the generated file. Each gets its own
            # field, so `reuse_model` doesn't turn them into empty subclasses of one shared class.
            **{
                name: {
                    'type': 'object',
                    'required': [f'{name[0].lower()}{name[1:]}Id'],
                    'properties': {f'{name[0].lower()}{name[1:]}Id': {'type': 'string'}},
                }
                for name in RESOURCE_INPUT_TYPEDDICTS
            },
        }
    },
}


def run_datamodel_codegen(*args: str) -> None:
    # Running from the repository root makes datamodel-codegen pick up `[tool.datamodel-codegen]` from `pyproject.toml`.
    subprocess.run(  # noqa: S603
        [sys.executable, '-m', 'datamodel_code_generator', *args],
        check=True,
        cwd=REPO_ROOT,
    )


def test_model_generation_pipeline(tmp_path: Path) -> None:
    """The `generate-models` pipeline (both codegen passes and post-processing) runs on a minimal spec."""
    # PR CI never runs `poe generate-models`, so this catches a dependency update that breaks the generator.
    spec_path = tmp_path / 'openapi.json'
    spec_path.write_text(json.dumps(MINIMAL_SPEC))
    models_path = tmp_path / '_models.py'
    literals_path = tmp_path / '_literals.py'
    typeddicts_path = tmp_path / '_typeddicts.py'

    run_datamodel_codegen('--input', str(spec_path), '--output', str(models_path), '--alias-generator', 'to_camel')
    run_datamodel_codegen(
        '--input',
        str(spec_path),
        '--output',
        str(typeddicts_path),
        '--output-model-type',
        'typing.TypedDict',
        '--no-use-closed-typed-dict',
    )
    postprocess_models(models_path, literals_path)
    postprocess_typeddicts(typeddicts_path, build_alias_map(models_path.read_text()))

    models = models_path.read_text()
    assert "@docs_group('Models')\nclass Run(BaseModel):" in models
    assert 'alias_generator=to_camel' in models
    assert 'started_at: AwareDatetime' in models
    assert 'from apify_client._literals import RunStatus' in models
    assert 'class RunStatus' not in models

    literals = literals_path.read_text()
    assert "RunStatus = Literal[\n    'READY',\n    'RUNNING',\n    'SUCCEEDED',\n] | str" in literals

    typeddicts = typeddicts_path.read_text()
    assert 'class RequestDict(TypedDict):\n    request_id: str' in typeddicts
    assert 'class RequestCamelDict(TypedDict):\n    requestId: str' in typeddicts
    assert 'class Run' not in typeddicts
