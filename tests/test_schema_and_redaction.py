from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.redaction_check import scan

ROOT = Path(__file__).parents[1]


def test_manifest_json_schema_accepts_current_manifests():
    schema = json.loads((ROOT / "schemas/adapter_manifest.schema.json").read_text())
    validator = Draft202012Validator(schema)
    for path in (ROOT / "adapters").glob("*/manifest.json"):
        data = json.loads(path.read_text())
        errors = list(validator.iter_errors(data))
        assert not errors, (path, [error.message for error in errors])


def test_redaction_scanner_flags_private_key(tmp_path):
    path = tmp_path / "secret.txt"
    path.write_text("-----BEGIN PRIVATE KEY-----\nredacted\n")
    findings = scan([path])
    assert any(name == "private-key" for _, _, name in findings)


def test_redaction_scanner_ignores_normal_fixture(tmp_path):
    path = tmp_path / "fixture.json"
    path.write_text('{"email": "Sincere@april.biz", "token": null}\n')
    assert scan([path]) == []
