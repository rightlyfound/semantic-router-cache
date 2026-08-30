from __future__ import annotations

import json
from pathlib import Path

from models.adapter_manifest import validate_manifest

ROOT = Path(__file__).parents[1]


def test_existing_manifests_validate():
    for path in sorted((ROOT / "adapters").glob("*/manifest.json")):
        valid, errors = validate_manifest(path)
        assert valid, (path, errors)


def test_missing_required_field_fails():
    data = json.loads((ROOT / "adapters/61381583dec31b83_03e547d1918cb5cf/manifest.json").read_text())
    data.pop("adapter_id")
    valid, errors = validate_manifest(data)
    assert not valid
    assert any("adapter_id" in error for error in errors)


def test_wrong_type_fails():
    data = json.loads((ROOT / "adapters/61381583dec31b83_03e547d1918cb5cf/manifest.json").read_text())
    data["models_used"] = "deepseek/deepseek-chat"
    valid, errors = validate_manifest(data)
    assert not valid
    assert any("models_used" in error for error in errors)


def test_invalid_enum_fails():
    data = json.loads((ROOT / "adapters/61381583dec31b83_03e547d1918cb5cf/manifest.json").read_text())
    data["status"] = "unknown"
    valid, errors = validate_manifest(data)
    assert not valid
    assert any("status" in error for error in errors)
